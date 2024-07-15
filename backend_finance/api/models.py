from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction")
    title = models.CharField(max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    category = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.amount} on: {self.date}"