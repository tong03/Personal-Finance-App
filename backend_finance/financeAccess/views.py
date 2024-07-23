from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import *
from .serializers import *
from datetime import datetime, timedelta
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Sum, Q
import collections
from .utils import categorize_transactions
import os
import logging

# REST
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

# Plaid
from plaid.api import plaid_api
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.models import InstitutionsGetByIdRequest, ItemGetRequest
from plaid.model.country_code import CountryCode
import plaid
from .models import PlaidItem
from plaid.model.transactions_sync_request import TransactionsSyncRequest

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')

# Debugging: Print the environment variables to verify they are set correctly
print(f"PLAID_CLIENT_ID: {PLAID_CLIENT_ID}")
print(f"PLAID_SECRET: {PLAID_SECRET}")

# Initialize plaid client with credentials
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
print(f"Plaid client: {client}")


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_link_token(request):
    print("Request received")
    user = request.user
    print(f"User: {user}")
    client_user_id = str(user.id)
    print(f"Client User ID: {client_user_id}")
    # Create link_token for given user
    link_request = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(client_user_id=client_user_id),
        products=[Products('auth')],
        client_name="Plaid Test App",
        country_codes=[CountryCode("US")],
        language='en',
    )
    try:
        print(f"About to do link_token_create")
        response = client.link_token_create(link_request)
        print(f"Link token created successfully: {response}")
        return JsonResponse({
            'link_token': response['link_token']
        })
    except plaid.ApiException as e:
        error_response = json.loads(e.body)
        print(f"Plaid API error: {error_response}")
        return JsonResponse({'error': error_response}, status=e.status)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def exchange_public_token(request):
    public_token = request.data.get('public_token')
    if not public_token:
        return JsonResponse({'error': "public_token required"}, status=400)


    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']

        if not access_token or not item_id:
            return JsonResponse({'error': "Failed to retrieve access token or item ID"}, status=500)


        item_request = ItemGetRequest(access_token=access_token)
        item_response = client.item_get(item_request)
        institution_id = item_response['item']['institution_id']

        institution_request = InstitutionsGetByIdRequest(
            institution_id=institution_id,
            country_codes=[CountryCode('US')]
        )
        institution_response = client.institutions_get_by_id(institution_request)
        institution_name = institution_response['institution']['name']

        plaid_item = PlaidItem.objects.filter(user=request.user, institution_name=institution_name).first()
        if plaid_item:
            return JsonResponse({
                'public_token_exchange': 'complete',
                'access_token': plaid_item.access_token,
                'item_id': plaid_item.item_id,
                'institution_name': plaid_item.institution_name,
            })
        else:
            plaid_item = PlaidItem(
                user=request.user,
                access_token=access_token,
                item_id=item_id,
                institution_name=institution_name,
            )
            plaid_item.save()

            return JsonResponse({
                'public_token_exchange': 'complete', 
                'access_token': access_token, 
                'item_id': item_id,
                'institution_name': institution_name,
                })
    except plaid.ApiException as e:
        return JsonResponse({'error': {
            'display_message': str(e),
            'error_code': e.status
        }}, status=500)
    

@csrf_exempt
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def get_transactions(request):
    try:
        plaid_item = PlaidItem.objects.get(user=request.user)
    except PlaidItem.DoesNotExist:
        return JsonResponse({'error': "Plaid item not found"}, status=404)
    
    access_token = plaid_item.access_token
    cursor = plaid_item.cursor or ''
    all_transactions = []
    has_more = True

    while has_more:
        try:
            ### TODO: BELOW IS WRONG AT THE MOMENT
            sync_request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor
            )
            response = client.transactions_sync(sync_request)
            print(f"Plaid API response: {response}")
            ### TODO: ABOVE IS WRONG
            transactions = response['transactions']
            all_transactions.extend(transactions['added'])

            cursor = response['next_cursor']
            has_more = response['has_more']
            plaid_item.cursor = cursor
            plaid_item.save()
        except plaid.ApiException as e:
            if e.body['error_code'] == 'TRANSACTIONS_SYNC_MUTATION_DURING_PAGINATION':
                # Restart the pagination loop from the original cursor
                cursor = ''
                continue
            else:
                return JsonResponse({'error': {
                    'display_message': str(e),
                    'error_code': e.status
                }}, status=500)

    return JsonResponse({'transactions': all_transactions})

@csrf_exempt
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_accounts(request):
    plaid_items = PlaidItem.objects.filter(user=request.user)
    if not plaid_items.exists():
        return JsonResponse({'error': "No Plaid items found for this user"}, status=404)
    
    accounts = []
    for item in plaid_items:
        access_token = item.access_token
        try:
            api_request = plaid_api.AccountsGetRequest(access_token=access_token)
            api_response = client.accounts_get(api_request)
            accounts.extend(api_response.to_dict()['accounts'])

        except plaid.ApiException as e:
            response = json.loads(e.body)
            return JsonResponse({
                'error': {
                    'status_code': e.status,
                    'display_message': response['error_message'],
                    'error_code': response['error_code'],
                    'error_type': response['error_type']
                }
            }, status=e.status)
    return JsonResponse({"accounts": accounts})



@api_view(['GET'])
@permission_classes([AllowAny])
def testing(request):
    plaid_items = PlaidItem.objects.all()
    if plaid_items.exists():
        plaid_items.delete()
        return Response({"message": "Deleted all PlaidItems"})
    return Response({"message": "This is a test"})
