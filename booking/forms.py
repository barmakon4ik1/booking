from django import forms
from .models import Housing
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class HousingForm(forms.ModelForm):
    class Meta:
        model = Housing
        fields = '__all__'
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

        # widgets = {
        #     'username': forms.TextInput(attrs={
        #         'class': 'form-control',
        #         'placeholder': 'Введите Ваш логин'
        #     }),
        #     'first_name': forms.TextInput(attrs={
        #         'class': 'form-control',
        #         'placeholder': 'Введите Ваше имя'
        #     }),
        #     'last_name': forms.TextInput(attrs={
        #         'class': 'form-control',
        #         'placeholder': 'Введите Вашу фамилию'
        #     }),
        #     'password1': forms.PasswordInput(attrs={
        #         'class': 'form-control',
        #         'placeholder': 'Введите пароль'
        #     }),
        #     'password2': forms.PasswordInput(attrs={
        #         'class': 'form-control',
        #         'placeholder': 'Повторите пароль'
        #     }),
        # }
