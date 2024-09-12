from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Housing(models.Model):
    TYPE_CHOICES = (
        ('APARTMENT', 'Apartment'),
        ('HOUSE', 'House'),
        ('STUDIO', 'Studio'),
        ('CASTLE', 'Castle'),
        ('HOTEL', 'Hotel'),
        # другие типы жилья
    )
    name = models.CharField('Name of object', max_length=100)
    type = models.CharField('Type of object', max_length=20, choices=TYPE_CHOICES, default='APARTMENT')
    country = models.CharField('Country', max_length=50)
    post_code = models.CharField('Postal code', max_length=10)
    city = models.CharField('City', max_length=50)
    street = models.CharField('Street', max_length=50, null=True, blank=True)
    house_number = models.CharField('House number', max_length=50, null=True, blank=True)
    rooms = models.IntegerField('Number of rooms')
    description = models.TextField('Description')
    price = models.DecimalField('Price', max_digits=10, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_visible = models.BooleanField(default=True)  # видимость объекта для просмотра
    created_at = models.DateTimeField(auto_now_add=True)  # дата создания записи

    def __str__(self):
        return f'{self.name} (Owner: {self.owner.first_name} {self.owner.last_name})'

    class Meta:
        verbose_name_plural = 'housings'
        verbose_name = 'housing'


class Booking(models.Model):
    BOOKING_STATUS = (
        ("CONFIRMED", "Confirmed"),
        ("PENDING", "Pending confirmation"),
        ("CANCELED", "Canceled"),
        ("UNCONFIRMED", "Unconfirmed")
    )
    status = models.CharField('Status', max_length=20, choices=BOOKING_STATUS, default='UNCONFIRMED')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    date_from = models.DateField('Booking from', null=True, blank=True)
    date_to = models.DateField('Booking to', null=True, blank=True)
    object = models.ForeignKey(Housing, on_delete=models.CASCADE)

    def __str__(self):
        return f'Время бронирования объекта с {self.date_from} по {self.date_to}'

    class Meta:
        verbose_name_plural = 'bookings'
        verbose_name = 'booking'


class Review(models.Model):
    rating = models.IntegerField('Rating')
    text = models.TextField('Review')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    object = models.ForeignKey(Housing, on_delete=models.CASCADE)

    def __str__(self):
        return f'Отзыв от {self.user.first_name} {self.user.last_name} для {self.object.name}'

    class Meta:
        verbose_name_plural = 'reviews'
        verbose_name = 'review'
