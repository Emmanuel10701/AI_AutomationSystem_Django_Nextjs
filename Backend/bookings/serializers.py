from rest_framework import serializers
from .models import Booking, BookingHistory
from flights.serializers import FlightSerializer

class BookingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingHistory
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(read_only=True)
    history = BookingHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('booking_reference', 'created_at', 'updated_at')

class CreateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('flight', 'passengers')
    
    def validate_passengers(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("At least one passenger is required")
        return value
    
    def create(self, validated_data):
        flight = validated_data['flight']
        passengers = validated_data['passengers']
        total_amount = flight.price * len(passengers)
        
        booking = Booking.objects.create(
            **validated_data,
            user=self.context['request'].user,
            total_amount=total_amount
        )
        return booking