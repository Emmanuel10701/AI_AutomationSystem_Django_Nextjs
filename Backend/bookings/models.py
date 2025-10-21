from django.db import models
from users.models import User
from flights.models import Flight

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    booking_reference = models.CharField(max_length=10, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    passengers = models.JSONField()  # Store passenger details as JSON
    
    class Meta:
        db_table = 'bookings'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['booking_reference']),
        ]
    
    def __str__(self):
        return f"{self.booking_reference} - {self.user.username}"

class BookingHistory(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'booking_history'