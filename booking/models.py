from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _


class Housing(models.Model):
    class HousingType(models.TextChoices):
        APARTMENT = 'APARTMENT', 'Квартира'
        HOUSE = 'HOUSE', 'Дом'
        STUDIO = 'STUDIO', 'Студия'
        CASTLE = 'CASTLE', 'Замок'
        HOTEL = 'HOTEL', 'Гостиница'
        VILLA = 'VILLA', 'Вилла'
        COTTAGE = 'COTTAGE', 'Коттедж'

    name = models.CharField(_('Name of object'), max_length=100)
    type = models.CharField(
        _('Type of object'),
        max_length=20,
        choices=HousingType.choices,
        default=HousingType.APARTMENT
    )
    country = models.CharField(_('Country'), max_length=50)
    post_code = models.CharField(_('Postal code'), max_length=10)
    city = models.CharField(_('City'), max_length=50)
    street = models.CharField(_('Street'), max_length=50, null=True, blank=True)
    house_number = models.CharField(_('House number'), max_length=50, null=True, blank=True)
    rooms = models.IntegerField(_('Number of rooms'))
    description = models.TextField(_('Description'))
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_housings')
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

    def get_average_rating(self):
        avg_rating = self.reviews.aggregate(Avg('rating')).get('rating__avg')
        return avg_rating if avg_rating is not None else 0  # Возвращаем 0, если нет отзывов


class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        PENDING = 'PENDING', _('Pending confirmation')
        CANCELED = 'CANCELED', _('Canceled')
        UNCONFIRMED = 'UNCONFIRMED', _('Unconfirmed')

    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.UNCONFIRMED
    ) # Статус бронирования
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    ) # Пользователь, который забронировал
    created_at = models.DateTimeField(
        auto_now_add=True
    ) # Дата создания бронирования
    date_from = models.DateField(
        _('Booking from'),
        null=True,
        blank=True) # Дата начала бронирования
    date_to = models.DateField(
        _('Booking to'),
        null=True,
        blank=True) # Дата окончания бронирования
    housing = models.ForeignKey(
        Housing,
        on_delete=models.CASCADE,
        related_name='bookings'
    )  # Жилье, которое было забронировано

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValidationError(_('Booking start date cannot be after the end date.'))

    def __str__(self):
        return f"Бронирование {self.housing} от {self.date_from} до {self.date_to}"

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
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    housing = models.ForeignKey(Housing, on_delete=models.CASCADE, related_name='reviews')

    def __str__(self):
        return f'Отзыв от {self.owner.first_name} {self.owner.last_name} для {self.housing.name}'

    class Meta:
        verbose_name_plural = _('reviews')
        verbose_name = _('review')






