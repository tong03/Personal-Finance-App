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
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    account_owner = models.CharField(max_length=200, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    authorized_date = models.CharField(max_length=200, null=True)
    builtin_category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.DO_NOTHING, default=int(BuiltinCategories.MISCELLANEOUS.value))
    category = ArrayField(models.CharField(max_length=200), null=True)
    category_id = models.CharField(max_length=200, null=True)
    date = models.DateTimeField(null=False, default=datetime.now())
    iso_currency_code = models.CharField(max_length=200, null=True)
    location = models.JSONField(null=True)
    merchant_name = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, null=True)
    payment_meta = models.JSONField(null=True)
    payment_channel = models.CharField(max_length=200, null=True)
    pending = models.BooleanField(null=True)
    pending_transaction_id = models.CharField(max_length=200, null=True)
    transaction_code = models.CharField(max_length=200, null=True)
    transaction_id = models.CharField(max_length=200, unique=True, null=True, blank=False)
    transaction_type = models.CharField(max_length=200, null=True)
    unofficial_currency_code = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f"{self.name} - ${self.amount} on {self.date.strftime('%Y-%m-%d')}"
    

# Create your models here.
# class Transaction(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction")
#     title = models.CharField(max_length=100)
#     amount = models.DecimalField(decimal_places=2, max_digits=10)
#     category = models.TextField()
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.title} - {self.amount} on: {self.date}"