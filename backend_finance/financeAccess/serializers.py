from rest_framework import serializers
from .models import *

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class PlaidItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaidItem
        fields = '__all__'
        extra_kwargs = {"user": {"read_only": True}}

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'plaid_account_id', 'balances', 'mask', 'name', 'official_name', 'subtype', 'account_type', 'user', 'item']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'description', 'parent_category', 'user', 'custom']

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'date', 'user']

class BudgetCategoryAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategoryAmount
        fields = ['id', 'budget', 'category', 'amount']
