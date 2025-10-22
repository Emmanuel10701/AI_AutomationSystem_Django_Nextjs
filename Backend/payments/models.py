from django.db import models
from bookings.models import Booking

class Payment(models.Model):
    PAYMENT_METHODS = [('paypal', 'PayPal'), ('stripe', 'Stripe'), ('card', 'Credit Card')]
    STATUS_CHOICES = [('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='paypal')
    paypal_order_id = models.CharField(max_length=100, blank=True, null=True)
    paypal_payer_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.booking.booking_reference} - {self.status}"

class PaymentWebhookLog(models.Model):
    payload = models.JSONField()
    event_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.created_at}"
