from django.db import models

class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'airports'
    
    def __str__(self):
        return f"{self.code} - {self.city}"

class Flight(models.Model):
    flight_number = models.CharField(max_length=10)
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures')
    arrival_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.IntegerField()
    airline = models.CharField(max_length=50)
    aircraft_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'flights'
        indexes = [
            models.Index(fields=['departure_airport', 'arrival_airport']),
            models.Index(fields=['departure_time']),
        ]
    
    def __str__(self):
        return f"{self.flight_number} - {self.departure_airport.code} to {self.arrival_airport.code}"