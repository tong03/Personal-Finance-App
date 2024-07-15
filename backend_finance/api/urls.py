from django.urls import path
from . import views

# TODO: Make it more RESTful by cleaning up paths
urlpatterns = [
    path('', views.getRoutes, name='routes'),
    path('transactions/', views.getTransactions, name='transactions'),
    path('transactions/create/', views.createTransaction, name='create-transaction'),
    path('transactions/<str:pk>/', views.getTransaction, name='transaction'),
    path('transactions/<str:pk>/update/', views.updateTransaction, name='update-transaction'),
    path('transactions/<str:pk>/delete/', views.deleteTransaction, name='delete-transaction'),
]
