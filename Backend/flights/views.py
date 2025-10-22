from rest_framework import generics, permissions
from django.db.models import Q
from .models import Flight, Airport
from .serializers import FlightSerializer, AirportSerializer
from datetime import datetime, timedelta

# ------------------------------
# List all airports
# ------------------------------
class AirportListAPI(generics.ListAPIView):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [permissions.IsAuthenticated]


# ------------------------------
# Search for flights
# ------------------------------
class FlightSearchAPI(generics.ListAPIView):
    serializer_class = FlightSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Use self.request.GET to avoid query_params Pylance errors
        departure = self.request.GET.get('departure')
        arrival = self.request.GET.get('arrival')
        date = self.request.GET.get('date')
        passengers_param = self.request.GET.get('passengers')
        passengers = int(passengers_param) if passengers_param and passengers_param.isdigit() else 1

        queryset = Flight.objects.select_related('departure_airport', 'arrival_airport')

        # Filter by departure airport
        if departure:
            queryset = queryset.filter(
                Q(departure_airport__city__icontains=departure) |
                Q(departure_airport__code__icontains=departure)
            )

        # Filter by arrival airport
        if arrival:
            queryset = queryset.filter(
                Q(arrival_airport__city__icontains=arrival) |
                Q(arrival_airport__code__icontains=arrival)
            )

        # Filter by date
        if date:
            try:
                search_date = datetime.strptime(date, '%Y-%m-%d').date()
                next_day = search_date + timedelta(days=1)
                queryset = queryset.filter(departure_time__date__range=[search_date, next_day])
            except ValueError:
                pass

        # Filter by available seats
        queryset = queryset.filter(available_seats__gte=passengers)

        return queryset.order_by('departure_time')


# ------------------------------
# Flight detail view
# ------------------------------
class FlightDetailAPI(generics.RetrieveAPIView):
    queryset = Flight.objects.select_related('departure_airport', 'arrival_airport')
    serializer_class = FlightSerializer
    permission_classes = [permissions.IsAuthenticated]
