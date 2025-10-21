from rest_framework import generics, permissions
from django.db.models import Q
from .models import Flight, Airport
from .serializers import FlightSerializer, AirportSerializer
from datetime import datetime, timedelta

class AirportListAPI(generics.ListAPIView):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [permissions.IsAuthenticated]

class FlightSearchAPI(generics.ListAPIView):
    serializer_class = FlightSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Flight.objects.select_related('departure_airport', 'arrival_airport')
        
        departure = self.request.query_params.get('departure')
        arrival = self.request.query_params.get('arrival')
        date = self.request.query_params.get('date')
        passengers = int(self.request.query_params.get('passengers', 1))
        
        if departure:
            queryset = queryset.filter(
                Q(departure_airport__city__icontains=departure) |
                Q(departure_airport__code__icontains=departure)
            )
        if arrival:
            queryset = queryset.filter(
                Q(arrival_airport__city__icontains=arrival) |
                Q(arrival_airport__code__icontains=arrival)
            )
        if date:
            try:
                search_date = datetime.strptime(date, '%Y-%m-%d').date()
                next_day = search_date + timedelta(days=1)
                queryset = queryset.filter(
                    departure_time__date__range=[search_date, next_day]
                )
            except ValueError:
                pass
        
        # Filter by available seats
        queryset = queryset.filter(available_seats__gte=passengers)
        
        return queryset.order_by('departure_time')

class FlightDetailAPI(generics.RetrieveAPIView):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [permissions.IsAuthenticated]