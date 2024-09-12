from rest_framework import viewsets
from booking.models import *
from booking.serializers import *


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class HousingViewSet(viewsets.ModelViewSet):
    queryset = Housing.objects.all()
    serializer_class = HousingSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

