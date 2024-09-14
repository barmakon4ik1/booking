from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from booking.views import *

router = DefaultRouter()
router.register('housings', HousingViewSet, basename='housings')
router.register('bookings', BookingViewSet, basename='bookings')
router.register('reviews', ReviewViewSet, basename='reviews')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', index, name='index'),
    path('about', about, name='about'),
    path('create', create, name='create'),


    path('login', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('api/', include(router.urls)),
]
