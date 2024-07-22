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
from plaid.model.country_code import CountryCode
import plaid
from .models import PlaidItem

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


# create_link_token
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

    request = ItemPublicTokenExchangeRequest(public_token=public_token)

    try:
        exchange_response = client.item_public_token_exchange(request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']

        plaid_item = PlaidItem(
            user=request.user,
            access_token=access_token,
            item_id=item_id,
        )
        plaid_item.save()

        return JsonResponse({'public_token_exchange': 'complete', 'access_token': access_token, 'item_id': item_id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def testing(request):
    return Response({"message": "This is a test"})
