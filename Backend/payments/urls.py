from django.urls import path
from .views import create_paypal_payment, execute_paypal_payment, paypal_webhook

urlpatterns = [
    path('create-paypal-payment/<int:booking_id>/', create_paypal_payment, name='create-paypal-payment'),
    path('execute-payment/', execute_paypal_payment, name='execute-payment'),
    path('webhook/paypal/', paypal_webhook, name='paypal-webhook'),
]