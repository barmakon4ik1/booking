from django.views.generic import DetailView
from django_filters.views import FilterView
from rest_framework import viewsets
from booking.serializers import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .filters import *
from .forms import *
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from .permissions import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import *
from django.views.generic import ListView


def housing_list(request):
    housing = Housing.objects.all()
    housing_filter = HousingFilter(request.GET, queryset=housing)

    context = {
        'filter': housing_filter,
        'housing': housing_filter.qs,  # отфильтрованные результаты
        'title': 'Список жилья'
    }
    return render(request, 'booking/housing_list.html', context)


# class HousingListView(FilterView):
#     model = Housing
#     filterset_class = HousingFilter
#     template_name = 'booking/housing_list.html'


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)

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
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = HousingFilter
    ordering_fields = '__all__'  # Позволяет сортировать по всем полям модели
    ordering = ['-created_at']  # Сортировка по умолчанию

    def get_queryset(self):
        """
        Получение данных с учетом фильтров
        """
        queryset = Housing.objects.all()
        filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return filterset.qs

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
    """
    Главная страница сайта
    """
    housing = Housing.objects.order_by('-id')
    return render(request, 'booking/index.html', {'title': 'AT-Booking Просмотр объектов', 'housing': housing})


def about(request):
    """
    Страница о программе и ее назначении
    """
    return render(request, 'booking/about.html')


def create(request):
    """
    Регистрация объекта недвижимости
    """
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
    """
    Функция регистрации пользователей
    """
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

