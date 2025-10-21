from django.urls import path
from .views import BookingListAPI, BookingDetailAPI, create_booking

urlpatterns = [
    path('', BookingListAPI.as_view(), name='booking-list'),
    path('create/', create_booking, name='create-booking'),
    path('<int:pk>/', BookingDetailAPI.as_view(), name='booking-detail'),
]