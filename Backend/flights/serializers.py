from rest_framework import serializers
from .models import Airport, Flight

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = '__all__'

class FlightSerializer(serializers.ModelSerializer):
    departure_airport = AirportSerializer(read_only=True)
    arrival_airport = AirportSerializer(read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Flight
        fields = '__all__'
    
    def get_duration(self, obj):
        duration = obj.arrival_time - obj.departure_time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        return f"{hours}h {minutes}m"