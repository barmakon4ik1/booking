import logging

from django.http import HttpResponseForbidden
from django.views.generic import DetailView
from django_filters.views import FilterView
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from booking.serializers import *
from django.shortcuts import render, redirect, get_object_or_404
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
from django.utils import timezone


def user_filter(request):
    """
    Фильтрация объектов по категории пользователей
    """
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
    if request.user.is_authenticated:
        housing_filter = HousingFilter(request.GET, queryset=user_filter(request))
        context = {
            'filter': housing_filter,
            'housing': housing_filter.qs,  # отфильтрованные результаты
            'title': 'Список жилья'
        }
        return render(request, 'booking/housing_list.html', context)
    else:
        return redirect('login')


class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookings to be viewed or edited.
    """
    queryset = Booking.objects.all().order_by('id')
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BookingDetailListCreateView(ListCreateAPIView):
    queryset = Booking.objects.all().order_by('id')
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BookingDetailSerializer
        return BookingDetailCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BookingDetailListRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = Booking.objects.all().order_by('id')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BookingDetailSerializer
        return BookingDetailCreateUpdateSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
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
    """
    API - просмотр записей об отзывах
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]


def login_view(request):
    """
    Аунтентификация пользователя
    """
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
    """
    Выход из системы
    """
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


@login_required
def create(request):
    """
    Регистрация объекта недвижимости
    """
    try:
        user = request.user
        error = ''

        if request.method == 'POST':
            form = HousingForm(request.POST)
            if form.is_valid():
                # Создаем объект, но не сохраняем его сразу
                housing = form.save(commit=False)
                # Автоматически задаем владельца объекта
                housing.owner = user
                # Сохраняем объект с заполненным полем owner
                housing.save()
                return redirect('/')
            else:
                error = 'Неверные данные'

        form = HousingForm()
        context = {
            'form': form,
            'error': error
        }
        return render(request, 'booking/create.html', context)

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error occurred: {e}")
        # Перенаправление на главную страницу
        return render(request, 'booking/index.html', {'error_message': str(e)})


@login_required
def edit_housing(request, housing_id):
    """
    Редактирование объекта недвижимости для владельца или администратора
    """
    try:
        housing = get_object_or_404(Housing, id=housing_id)
        user = request.user

        # Проверка, что пользователь является владельцем объекта или администратором
        if user != housing.owner and not user.is_staff:
            return HttpResponseForbidden("У вас нет прав для редактирования этого объекта.")

        if request.method == 'POST':
            form = HousingForm(request.POST, instance=housing)
            if form.is_valid():
                form.save()
                return redirect('/')  # Перенаправление на главную страницу или список объектов
        else:
            form = HousingForm(instance=housing)

        return render(request, 'booking/edit_housing.html', {
            'form': form,
            'housing': housing
        })

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error occurred while editing housing: {e}")
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


@login_required
def create_booking(request, housing_id):
    """
    Создание бронирования
    """
    housing = get_object_or_404(Housing, pk=housing_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.owner = request.user  # Устанавливаем владельца бронирования
            booking.housing = housing  # Устанавливаем жилье для бронирования
            booking.save()
            messages.success(request, 'Бронирование успешно создано и ожидает подтверждения!')
            return redirect('my_bookings')  # Перенаправляем на страницу бронирования
    else:
        form = BookingForm()

    return render(request, 'booking/create_booking.html', {
        'form': form,
        'housing': housing
    })


@login_required
def my_bookings(request):
    """
    Отображение всех бронирований пользователя
    """
    bookings = Booking.objects.filter(owner=request.user)
    reviews = Review.objects.filter(owner=request.user)

    return render(request, 'booking/my_bookings.html', {
        'bookings': bookings,
        'reviews': reviews,
    })


@login_required
def edit_review(request, review_id):
    """
    Редактирование отзыва
    """
    review = get_object_or_404(Review, pk=review_id, owner=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш отзыв был успешно обновлен.')
            return redirect('my_bookings')  # Возвращаем пользователя на страницу его бронирований
    else:
        form = ReviewForm(instance=review)

    return render(request, 'booking/edit_review.html', {
        'form': form,
        'review': review
    })


@login_required
def cancel_booking(request, booking_id):
    """
    Отмена бронирования
    """
    booking = get_object_or_404(Booking, id=booking_id, owner=request.user)

    if request.method == 'POST':
        form = CancelBookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('my_bookings')
    else:
        form = CancelBookingForm(instance=booking)

    return render(request, 'booking/cancel_booking.html', {'form': form, 'booking': booking})


@login_required
def edit_booking(request, booking_id):
    """
    Редактирование бронирования
    """
    # Проверяем, что бронирование принадлежит пользователю
    booking = get_object_or_404(Booking, id=booking_id, owner=request.user)

    if request.method == 'POST':
        form = EditBookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            # Перенаправляем на страницу со списком бронирований после сохранения
            return redirect('my_bookings')
    else:
        form = EditBookingForm(instance=booking)

    return render(request, 'booking/edit_booking.html', {
        'form': form,
        'booking': booking
    })


@login_required
def change_booking_status(request, booking_id):
    """
    Изменение статуса бронирования
    """
    booking = get_object_or_404(Booking, id=booking_id)

    # Проверяем, что пользователь является владельцем объекта или администратором
    if request.user != booking.housing.owner and not request.user.is_staff:
        messages.error(request, "У вас нет прав для изменения статуса этого бронирования.")
        return redirect('my_bookings')

    if request.method == 'POST':
        form = ChangeBookingStatusForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, "Статус бронирования успешно обновлен.")
            # Перенаправляем на страницу со списком бронирований после изменения статуса бронирования
            return redirect('my_confirmation')
    else:
        form = ChangeBookingStatusForm(instance=booking)

    return render(request, 'booking/change_booking_status.html', {
        'form': form,
        'booking': booking
    })


@login_required
def my_confirmation(request):
    """
    Подтверждение бронирования
    """
    user = request.user

    # Если пользователь администратор, получаем все бронирования со статусом PENDING или UNCONFIRMED
    if user.is_staff or user.is_superuser:
        bookings_status = Booking.objects.filter(status__in=['PENDING', 'UNCONFIRMED']).order_by('-created_at')
    else:
        # Для владельца объекта получаем бронирования его объектов со статусом PENDING или UNCONFIRMED
        bookings_status = Booking.objects.filter(
            housing__owner=user, status__in=['PENDING', 'UNCONFIRMED']
        ).order_by('-created_at')

    return render(request, 'booking/my_confirmation.html', {'bookings_status': bookings_status})


@login_required
def create_review(request, housing_id):
    """
    Функция оставления отзыва
    """
    housing = get_object_or_404(Housing, pk=housing_id)

    # Проверка, бронировал ли пользователь данный объект
    has_booking = Booking.objects.filter(housing=housing, owner=request.user).exists()

    if not has_booking:
        messages.error(request, 'Вы не можете оставить отзыв на объект, который не бронировали.')
        return redirect('index')

    # Проверка, оставлял ли пользователь уже отзыв на данный объект
    has_review = Review.objects.filter(housing=housing, owner=request.user).exists()

    if has_review:
        messages.error(request, 'Вы уже оставляли отзыв на этот объект.')
        return redirect('my_bookings')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.owner = request.user # Владелец отзыва - текущий пользователь
            review.housing = housing
            review.save()
            messages.success(request, 'Ваш отзыв был успешно добавлен.')
            return redirect('my_bookings')
    else:
        form = ReviewForm()

    return render(request, 'booking/create_review.html', {
        'form': form,
        'housing': housing
    })