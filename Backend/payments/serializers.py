from rest_framework import serializers
from .models import Payment, PaymentWebhookLog

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_method', 'paypal_order_id', 'paypal_payer_id', 'status', 'created_at', 'updated_at']

class PaymentWebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentWebhookLog
        fields = ['id', 'payload', 'event_type', 'created_at']
