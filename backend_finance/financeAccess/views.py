from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import *
from .serializers import *
from datetime import datetime, date
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
import traceback
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
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
from .models import PlaidItem, Account
from plaid.model.transactions_sync_request import TransactionsSyncRequest

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')

# Debugging: Print the environment variables to verify they are set correctly
# print(f"PLAID_CLIENT_ID: {PLAID_CLIENT_ID}")
# print(f"PLAID_SECRET: {PLAID_SECRET}")

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
# print(f"Plaid client: {client}")


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
    user = request.user
    public_token = request.data.get('public_token')
    print(request.data)
    if not public_token:
        return JsonResponse({'error': "public_token required"}, status=400)
    # accounts = request.data.get('accounts')
    # if not accounts:
    #     return JsonResponse({'error': "No accounts found"}, status=400)

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

# TODO: Could turn the section below more concise with a try-except block
        plaid_item = PlaidItem.objects.filter(user=request.user, item_id=item_id).first()
        # check to see if filtered object exists
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
    curr_user = request.user
    if not curr_user:
        return JsonResponse({'error': 'User not authenticated'}, status=403)
    
    page = int(request.GET.get('page', 1))  
    per_page = int(request.GET.get('per_page', 10))

    plaid_items = PlaidItem.objects.filter(user=curr_user)
    if not plaid_items.exists():
        return JsonResponse({'error': "No Plaid items found for this user"}, status=404)
    transactions = []
    for item in plaid_items:
        try:
            access_token = item.access_token
            # Make cursor if not presence
            if not item.cursor:
                item.cursor = ""
                item.save()

            sync_request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=item.cursor
            )
            sync_response = client.transactions_sync(sync_request)
            print("Sync_response:", sync_response.to_dict())
            transactions.extend(sync_response['added'])

            # Update cursor
            item.cursor = sync_response['next_cursor']
            item.save()

            # screen the transactions to see if they exist already for user
            for transaction in transactions:
                try:
                    existing_trans = Transaction.objects.get(transaction_id=transaction['transaction_id'], user=curr_user)
                    continue
                except Transaction.DoesNotExist:
                    try:
                        account = curr_user.account_set.get(plaid_account_id=transaction['account_id'])
                    except Account.DoesNotExist:
                        print(f"Account with plaid_account_id {transaction['account_id']} not found for user {curr_user}")
                        continue  # Skip this transaction if the account does not exist
                    new_trans = Transaction()
                    new_trans.account = curr_user.account_set.get(plaid_account_id=transaction['account_id'])
                    new_trans.user = curr_user
                    new_trans.transaction_id = transaction['transaction_id']
                    new_trans.amount = transaction['amount']
                    new_trans.date = parse_date(transaction['date'])
                    new_trans.iso_currency_code = transaction['iso_currency_code']
                    new_trans.unofficial_currency_code = transaction.get('unofficial_currency_code', None)
                    new_trans.category = ', '.join(transaction['category'])
                    new_trans.payment_channel = transaction['payment_channel']
                    new_trans.pending = transaction['pending']
                    new_trans.location = {
                        "city": transaction['location'].get('city', ''),
                        "postal_code" : transaction['location'].get('postal_code', ''),
                    }          
                    new_trans.name = transaction['name']

                    new_trans.save()
   
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
        except Exception as e:
            print("Exception occurred: ", str(e))
            print(traceback.format_exc()) 
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)       


    # Pagination attempt before returning data    
    transactions_query = Transaction.objects.filter(user=curr_user)
    paginator = Paginator(transactions_query, per_page)

    try:
        transactions_page = paginator.page(page)
    except PageNotAnInteger:
        transactions_page = paginator.page(1)
    except EmptyPage:
        transactions_page = paginator.page(paginator.num_pages)

    # Turning transactions into a dict to return in JSON
    transactions_data = [transaction_to_dict(trans) for trans in transactions_page]
    
    response_data = {
        'status': 'success',
        'transactions': transactions_data,
        'page': transactions_page.number,
        'pages': paginator.num_pages,
        'total': paginator.count,
    }

    return JsonResponse(response_data)


def parse_date(date_value):
    if isinstance(date_value, date):
        return date_value
    elif isinstance(date_value, str):
        return datetime.strptime(date_value, '%Y-%m-%d').date()
    else:
        raise ValueError(f"Unsupported date format: {date_value}")

def transaction_to_dict(transaction):
    return {
        'transaction_id': transaction.transaction_id,
        'account': transaction.account.id,  # or any other identifier
        'user': transaction.user.id,
        'amount': transaction.amount,
        'date': transaction.date.strftime('%Y-%m-%d'),
        'iso_currency_code': transaction.iso_currency_code,
        'unofficial_currency_code': transaction.unofficial_currency_code,
        'category': transaction.category,
        'payment_channel': transaction.payment_channel,
        'pending': transaction.pending,
        'location': transaction.location,
        'name': transaction.name,
    }

@csrf_exempt
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_accounts(request):
    curr_user=request.user
    if not curr_user:
        return JsonResponse({'error': 'User not authenticated'}, status=403)
    plaid_items = PlaidItem.objects.filter(user=curr_user)
    if not plaid_items.exists():
        return JsonResponse({'error': "No Plaid items found for this user"}, status=404)
    
    accounts = []
    for item in plaid_items: 
        access_token = item.access_token
        try:
            api_request = plaid_api.AccountsGetRequest(access_token=access_token)
            api_response = client.accounts_get(api_request)
            accounts.extend(api_response.to_dict()['accounts'])
            
            for account in accounts:
                existing_acct = Account.objects.filter(plaid_account_id=account['account_id'], user=curr_user).first()
                if not existing_acct:
                    new_acct = Account(
                        plaid_account_id=account['account_id'],
                        balances=account['balances'],
                        mask=account['mask'],
                        name=account['name'],
                        official_name=account['official_name'],
                        subtype=account['subtype'],
                        account_type=account['type'],
                        user=curr_user,
                        item=item
                    )
                    new_acct.save()
            return JsonResponse({"accounts": accounts})
        
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
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)
            



@api_view(['GET'])
@permission_classes([AllowAny])
def testing(request):
    plaid_items = PlaidItem.objects.all()
    if plaid_items.exists():
        plaid_items.delete()
        return Response({"message": "Deleted all in DB."})
    
    return Response({"message": "This is a test"})
