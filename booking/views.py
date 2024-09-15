import logging

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
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


def user_filter(request):
    user = request.user
    # Определяем фильтр для видимости
    if user.is_staff or user.is_superuser:
        # Если пользователь администратор, возвращаем все объекты
        return Housing.objects.all().order_by('id')
    else:
        # Фильтруем объекты по видимости и добавляем объекты, где пользователь является владельцем
        housing = Housing.objects.filter(
            is_visible=True
        ).order_by('-id')
        return housing | Housing.objects.filter(owner=user)


def housing_list(request):
    """
    Отображение формы с возможностью фильтрации - меню "Фильтр"
    """
    try:
        housing_filter = HousingFilter(request.GET, queryset=user_filter(request))
        context = {
            'filter': housing_filter,
            'housing': housing_filter.qs,  # отфильтрованные результаты
            'title': 'Список жилья'
        }
        return render(request, 'booking/housing_list.html', context)
    except Exception as e:
        # Логирование ошибки для отладки
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error occurred: {e}")
        # Перенаправление на страницу с авторизацией
        return render(request, 'booking/error.html', {'error_message': str(e)})


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class HousingViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт просмотра объектов найма и редактирования
    """
    serializer_class = HousingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = HousingFilter
    ordering_fields = '__all__'  # Позволяет сортировать по всем полям модели
    ordering = ['-created_at']  # Сортировка по умолчанию

    def get_queryset(self):
        """
        Получение данных с учетом фильтров и видимости, с учетом прав доступа
        """
        user = self.request.user

        if user.is_superuser:
            # Если пользователь администратор, возвращаем все объекты
            queryset = Housing.objects.all()
        else:
            # Для обычных пользователей - только видимые объекты
            # queryset = Housing.objects.filter(is_visible=True)
            queryset = Housing.objects.filter(
                Q(is_visible=True) |
                Q(owner=user)
            ).order_by('-id')

        # Применение фильтров
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
    Начальная страница сайта - меню "Главная"
    """
    try:
        return render(request, 'booking/index.html', {
            'title': 'AT-Booking Просмотр объектов',
            'housing': user_filter(request)
        })
    except Exception as e:
        # Логирование ошибки для отладки
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error occurred: {e}")
        # Перенаправление на страницу с авторизацией
        return render(request, 'booking/error.html', {'error_message': str(e)})


def about(request):
    """
    Страница о программе и ее назначении - меню "О программе"
    """
    return render(request, 'booking/about.html')


def create(request):
    """
    Регистрация объекта недвижимости
    """
    try:
        user = request.user
        if user.is_authenticated:
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
        else:
            return redirect('login')
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error occurred: {e}")
        # Перенаправление на страницу с авторизацией
        return render(request, 'booking/error.html', {'error_message': str(e)})


def register(request):
    """
    Функция регистрации пользователей - в меню "Войти" есть опция "Создать аккаунт"
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



