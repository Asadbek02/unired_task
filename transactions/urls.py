from django.urls import path
from . import views

urlpatterns = [
    path('transaction/create/', views.create_transaction, name='create_transaction'),
    path('transaction/confirm/', views.confirm_transaction, name='confirm_transaction'),
    path('transaction/cancel/', views.cancel_transaction, name='cancel_transaction'),
    path('transaction/history/', views.transaction_history, name='transaction_history'),
]
