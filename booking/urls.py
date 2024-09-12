from django.urls import path, include
from rest_framework.routers import DefaultRouter

from booking.views import *

router = DefaultRouter()
router.register('housings', HousingViewSet, basename='housings')
router.register('bookings', BookingViewSet, basename='bookings')
router.register('reviews', ReviewViewSet, basename='reviews')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]