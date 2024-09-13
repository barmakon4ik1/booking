from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Housing(models.Model):
    class HousingType(models.TextChoices):
        APARTMENT = 'APARTMENT', _('Apartment')
        HOUSE = 'HOUSE', _('House')
        STUDIO = 'STUDIO', _('Studio')
        CASTLE = 'CASTLE', _('Castle')
        HOTEL = 'HOTEL', _('Hotel')

    name = models.CharField(_('Name of object'), max_length=100)
    type = models.CharField(_('Type of object'), max_length=20, choices=HousingType.choices, default=HousingType.APARTMENT)
    country = models.CharField(_('Country'), max_length=50)
    post_code = models.CharField(_('Postal code'), max_length=10)
    city = models.CharField(_('City'), max_length=50)
    street = models.CharField(_('Street'), max_length=50, null=True, blank=True)
    house_number = models.CharField(_('House number'), max_length=50, null=True, blank=True)
    rooms = models.IntegerField(_('Number of rooms'))
    description = models.TextField(_('Description'))
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_housings')
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} (Owner: {self.owner.first_name} {self.owner.last_name})'

    class Meta:
        verbose_name_plural = _('housings')
        verbose_name = _('housing')
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['price']),
        ]


class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        PENDING = 'PENDING', _('Pending confirmation')
        CANCELED = 'CANCELED', _('Canceled')
        UNCONFIRMED = 'UNCONFIRMED', _('Unconfirmed')

    status = models.CharField(_('Status'), max_length=20, choices=BookingStatus.choices, default=BookingStatus.UNCONFIRMED)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    date_from = models.DateField(_('Booking from'), null=True, blank=True)
    date_to = models.DateField(_('Booking to'), null=True, blank=True)
    housing = models.ForeignKey(Housing, on_delete=models.CASCADE, related_name='bookings')

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValidationError(_('Booking start date cannot be after the end date.'))

    def __str__(self):
        return f'Время бронирования объекта с {self.date_from} по {self.date_to}'

    class Meta:
        verbose_name_plural = _('bookings')
        verbose_name = _('booking')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['date_from', 'date_to']),
        ]


class Review(models.Model):
    rating = models.IntegerField(_('Rating'))
    text = models.TextField(_('Review'))
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    housing = models.ForeignKey(Housing, on_delete=models.CASCADE, related_name='reviews')

    def __str__(self):
        return f'Отзыв от {self.user.first_name} {self.user.last_name} для {self.housing.name}'

    class Meta:
        verbose_name_plural = _('reviews')
        verbose_name = _('review')
