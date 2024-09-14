from rest_framework import viewsets
from booking.models import *
from booking.serializers import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import LoginForm, HousingForm, UserRegistrationForm
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from .permissions import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class HousingViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт просмотра объектов найма и редактирования
    """
    queryset = Housing.objects.all()
    serializer_class = HousingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        """
        Устанавливает текущего пользователя как владельца
        """
        serializer.save(owner=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]


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
        'error': error
    }
    return render(request, 'booking/create.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
            return redirect('login')  # Редирект на страницу входа после успешной регистрации
    else:
        form = UserRegistrationForm()
    return render(request, 'booking/register.html', {'form': form})

