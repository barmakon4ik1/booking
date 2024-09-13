from django import forms
from .models import Housing


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
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ввести описание объекта'
            }),
        }
