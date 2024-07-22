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

# REST
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

# Plaid
from plaid.api import plaid_api
from plaid import Configuration, ApiClient
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from django.contrib.auth.models import User

# Initialize plaid client with credentials
configuration = Configuration(
    host="http://sandbox.plaid.com",
    api_key={
        'clientId': '', # enter plaid id
        'secret': '', # enter secret
    }
)
api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# create_link_token
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_link_token(request):
    if request.method == 'POST':
        user = request.user
        client_user_id = user.id
        # Create link_token for given user
        link_request = LinkTokenCreateRequest(
            products=[Products('auth')],
            client_name="Plaid Test App",
            country_codes=[CountryCode("US")],
            redirect_uri='https://domainname.com/oauth-page.html',
            language='en',
            webhook='https://webhook.example.com',
            user=LinkTokenCreateRequestUser(client_user_id=client_user_id)
        )
        response = client.link_token_create(link_request)
        return JsonResponse(response.to_dict())
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)





# logged_in = False

# api_view(['GET'])
# def index(request):
#     user = request.user
#     global logged_in
#     if user.is_authenticated:
#         latest_budgets = user.budget_set.order_by(('-date')[:5])
#         latest_transactions = user.transaction_set.order_by(('-date')[:5])
#         accounts = user.account_set.order_by('name')
#         username = user.username
#         logged_in = user.is_authenticated

#         budgetSerialized = BudgetSerializer(latest_budgets, many=True)
#         transactionsSerialized = TransactionSerializer(latest_transactions, many=True)
#         accountsSerialized = AccountSerializer(accounts, many=True)

#         data = {
#             "latest_budgets": budgetSerialized,
#             "latest_transactions": transactionsSerialized,
#             "accounts": accountsSerialized,
#             "username": username,
#         }

#         return Response(data)
#     else:
#         return Response({'error': "User not authenticated!"}, status=401)
    
# @api_view(['POST'])
# def create_link_token(request):
#     user = request.user
#     if user.is_authenticated():
#         data = {
#             'user': {
#                 'client_user_id': str(user.id)
#             },
#             'product': ["transactions"],
#             'client_name': "Your App Name",
#             'country_code': ['US'],
#             'language': "en",
#         }
#         try:
#             response = client.LinkToken.create(data)
#             link_token = response['link-token']
#             return Response({'link_token': link_token})
#         except plaid.errors.PlaidError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     return Response({'error': "User not authenticated!"}, status=401)


# def get_access_token(request):
#     return Response("")

@api_view(['GET'])
@permission_classes([AllowAny])
def testing(request):
    return Response({"message": "This is a test"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_link_token(request):

    return Response("")