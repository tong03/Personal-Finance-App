from django.shortcuts import render
from django.contrib.auth.models import User

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
# from rest_framework.renderers import JSONRenderer

from .serializers import UserSerializer



# Practice function based views

# Create User function
@api_view(['POST'])
@permission_classes([AllowAny])
def createUser(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Get all CRUD endpoints initially
@api_view(['GET'])
@permission_classes([AllowAny])
# @renderer_classes([JSONRenderer])
def getRoutes(request):
    # routes = [
    #     {
    #         'Endpoint': '/transactions/',
    #         'method': 'GET',
    #         'body': None,
    #         'description': 'Returns an array of transactions',
    #     },
    #     {
    #         'Endpoint': '/transactions/id/',
    #         'method': 'GET',
    #         'body': None,
    #         'description': 'Returns a single transactions',
    #     },
    #     {
    #         'Endpoint': '/transactions/create/',
    #         'method': 'POST',
    #         'body': {'body': ""},
    #         'description': 'Creates a new transaction with data sent in post request',
    #     },
    #     {
    #         'Endpoint': '/transactions/id/update/',
    #         'method': 'PUT',
    #         'body': {'body': ""},
    #         'description': 'Updates an existing transaction with data sent in put request',
    #     },
    #     {
    #         'Endpoint': '/transactions/id/delete/',
    #         'method': 'DELETE',
    #         'body': None,
    #         'description': 'Delete existing transaction',
    #     },
    # ]
    routes = []
    return Response(routes)


# /transactions GET
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def getTransactions(request):
#     transactions = Transaction.objects.filter(user=request.user)
#     serializer = TransactionSerializer(transactions, many=True)
#     return Response(serializer.data)

# /transactions/create POST
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def createTransaction(request):
#     dataObtained = request.data
#     transaction = Transaction.objects.create(user=request.user,body=dataObtained['body'])
#     serializer = TransactionSerializer(transaction, many=False)
#     return Response(serializer.data)

# /transactions/<id> GET
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def getTransaction(request, pk):
#     transaction = Transaction.objects.get(id=pk, user=request.user)
#     serializer = TransactionSerializer(transaction, many=False)
#     return Response(serializer.data)

# /transactions/<id>/update PUT
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def updateTransaction(request, pk):
#     dataObtained = request.data
#     transaction = Transaction.objects.get(id=pk, user=request.user)
#     # select target transaction, replaces old data with dataObtained
#     serializer = TransactionSerializer(instance=transaction, data=dataObtained)
    
#     # validation of serialized data, then save it
#     if serializer.is_valid():
#         serializer.save()

#     return Response(serializer.data)

# /transactions/<id>/delete DELETE
# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def deleteTransaction(request, pk):
#     transaction = Transaction.objects.get(id=pk, user=request.user)
#     transaction.delete()
#     return Response("Transaction deleted!", status=status.HTTP_204_NO_CONTENT)