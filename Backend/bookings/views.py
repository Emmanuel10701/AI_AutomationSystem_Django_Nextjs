from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import random
import string
from .models import Booking
from .serializers import BookingSerializer, CreateBookingSerializer

def generate_booking_reference():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class BookingListAPI(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('flight')

class BookingDetailAPI(generics.RetrieveAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_booking(request):
    serializer = CreateBookingSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        booking = serializer.save()
        booking.booking_reference = generate_booking_reference()
        booking.save()
        
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)