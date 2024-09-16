from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class HousingForm(forms.ModelForm):

    class Meta:
        model = Housing
        fields = ['name',
                  'type',
                  'description',
                  'street',
                  'house_number',
                  'post_code',
                  'city',
                  'country',
                  'rooms',
                  'price',
                  'is_visible'
                  ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ввести данные объекта'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Выберите тип объекта'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите страну'
            }),
            'post_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите почтовый индекс'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите город'
            }),
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите улицу'
            }),
            'house_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите номер дома'
            }),
            'rooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите количество комнат'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите описание объекта'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите цену за сутки проживания'
            }),
            'is_visible': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'is_visible': 'Сделать объект видимым для просмотра'
        }


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Введите ваше имя')
    last_name = forms.CharField(max_length=30, required=True, help_text='Введите вашу фамилию')
    email = forms.EmailField(required=True, help_text='Введите действующий email')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date_from', 'date_to'] # Поля, заполняемые пользователем
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_to': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        # Проверка на валидность диапазона дат
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Дата начала бронирования не может быть позже даты окончания.")

        return cleaned_data


class CancelBookingForm(forms.ModelForm):
    """
    Форма отмены бронирования
    """
    class Meta:
        model = Booking
        fields = [] # Не отображаем поле status как обязательное

    def save(self, commit=True):
        # Устанавливаем статус бронирования как 'CANCELED'
        booking = super().save(commit=False)
        booking.status = Booking.BookingStatus.CANCELED
        if commit:
            booking.save()
        return booking


class EditBookingForm(forms.ModelForm):
    """
    Форма редактирования бронирования
    """
    class Meta:
        model = Booking
        fields = ['date_from', 'date_to']  # Добавляем поля для редактирования дат
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_to': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        # Проверка на корректность дат
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Дата начала не может быть позже даты окончания.")
        return cleaned_data


class ChangeBookingStatusForm(forms.ModelForm):
    """
    Подтверждение статуса бронирования
    """
    class Meta:
        model = Booking
        fields = ['status']  # Позволяем редактировать только статус
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),  # Добавляем класс для стилей
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'rating': 'Рейтинг (1-5)',
            'text': 'Ваш отзыв'
        }
