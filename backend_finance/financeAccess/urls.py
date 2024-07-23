from django.urls import path
from . import views


urlpatterns = [
    path('testing/', views.testing, name='testing'),
    path('create_link_token/', views.create_link_token, name='create_link_token'),
    path('exchange_public_token/', views.exchange_public_token, name='exchange_public_token'),
    path('get_transactions/', views.get_transactions, name='get_transactions'),
    path('get_accounts/', views.get_accounts, name='get_accounts'),
]
