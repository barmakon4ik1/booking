from rest_framework import serializers
from .models import *


class HousingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Housing
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    booking_user = UserSerializer(read_only=True)
    booking_object = HousingSerializer(read_only=True)
    booking_review = ReviewSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
