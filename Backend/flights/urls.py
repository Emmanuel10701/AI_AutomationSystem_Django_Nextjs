from django.urls import path
from .views import AirportListAPI, FlightSearchAPI, FlightDetailAPI

urlpatterns = [
    path('airports/', AirportListAPI.as_view(), name='airports'),
    path('search/', FlightSearchAPI.as_view(), name='flight-search'),
    path('<int:pk>/', FlightDetailAPI.as_view(), name='flight-detail'),
]