from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class HousingSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Housing
        fields = '__all__'
        read_only_fields = ['owner']  # Автоматическое добавление владельца объекта


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    housing = HousingSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('owner',)


class BookingDetailSerializer(BookingSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class BookingDetailCreateUpdateSerializer(BookingSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = '__all__'


class ViewHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewHistory
        fields = '__all__'

