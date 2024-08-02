# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import HStoreField
from datetime import datetime
from .utils import BuiltinCategories
    

# PlaidItem Model -- 1 item can have multiple accounts from different banking apps
class PlaidItem(models.Model):
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE, default=None)
    access_token = models.CharField(max_length=200, unique=True)
    item_id = models.CharField(max_length=200, unique=True)
    cursor = models.CharField(max_length=200, blank=True, null=True)
    institution_name = models.CharField(max_length=200, blank=True, null=True)

# Account Model
class Account(models.Model):
    id = models.AutoField(primary_key=True)
    plaid_account_id = models.CharField(max_length=200, null=True, unique=True)
    balances = models.JSONField(null=True)
    mask = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, null=True)
    official_name = models.CharField(max_length=200, null=True)
    subtype = models.CharField(max_length=200, null=True)
    account_type = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE, default=None)
    item = models.ForeignKey(PlaidItem, blank=True, null=True, on_delete=models.CASCADE, default=None)

# Category Model
class Category(models.Model):
    description = models.CharField(max_length=200, unique=True, null=False, blank=False)
    parent_category = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, default=None)
    custom = models.BooleanField(default=False, null=False, blank=False)
    def __str__(self):
        return f"User {self.user}, Description: {self.description}, Parent Cat: {self.parent_category}"

# Budget Model
class Budget(models.Model):
    date = models.DateField()
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE, default=None)
    def __str__(self):
        return f"User: {self.user}, Date: {self.date}"

# BudgetCategoryAmount Model -- linking Budget and Category Model
class BudgetCategoryAmount(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, default=0, blank=False, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=0, blank=False, null=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)

    def __str__(self):
        return f"Budget: {self.budget}, Category: {self.category}, Amount: {self.amount}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['budget', 'category'], name="unique_budget_category")
        ]

# Transaction Model
class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)
    transaction_id = models.CharField(max_length=200, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    iso_currency_code = models.CharField(max_length=3, null=True, blank=True)
    unofficial_currency_code = models.CharField(max_length=3, null=True, blank=True)
    category = ArrayField(models.CharField(max_length=200), null=True)
    # builtin_category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.DO_NOTHING, default=int(BuiltinCategories.MISCELLANEOUS.value))
    name = models.CharField(max_length=200, null=True)
    date = models.DateField()
    payment_channel = models.CharField(max_length=50)
    location = models.JSONField(null=True)
    pending = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.name} - ${self.amount} on {self.date.strftime('%Y-%m-%d')}"
