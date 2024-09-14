from rest_framework import viewsets
from booking.models import *
from booking.serializers import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import LoginForm, HousingForm
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages


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


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            if user is not None:
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('/')  # Перенаправление на главную или нужную страницу
                else:
                    messages.error(request, 'Неверный пароль.')
            else:
                messages.error(request, 'Пользователь с таким email не найден.')
        else:
            messages.error(request, 'Некорректные данные.')
    else:
        form = LoginForm()

    return render(request, 'booking/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')  # Перенаправление на страницу логина или другую нужную страницу


def index(request):
    housing = Housing.objects.order_by('-id')
    return render(request, 'booking/index.html', {'title': 'Main page', 'housing': housing})


def about(request):
    return render(request, 'booking/about.html')


def create(request):
    error = ''
    if request.method == 'POST':
        form = HousingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
        else:
            error = 'Неверные данные'

    form = HousingForm()
    context = {
        'form': form,
        'errors': error
    }
    return render(request, 'booking/create.html', context)