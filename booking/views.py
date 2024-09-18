import logging
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden
from django.utils.timezone import now
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
from django.db.models import Q, F, Count, Sum
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
from django.utils.dateformat import format


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
    Список объектов жилья с возможностью сортировки и фильтрации
    """
    if request.user.is_authenticated:
        # Логика фильтрации объектов
        housing = Housing.objects.filter(is_visible=True).order_by('id')

        # Получаем ключевое слово из GET-запроса
        keyword = request.GET.get('keyword', None)

        if keyword:
            # Фильтруем объекты по ключевому слову
            housing = housing.filter(Q(description__icontains=keyword) | Q(name__icontains=keyword))

            # Сохраняем запрос в историю поиска
            if request.user.is_authenticated:
                search_entry, created = SearchHistory.objects.get_or_create(
                    user=request.user, keyword=keyword
                )
                if not created:
                    # Если запрос уже существует, увеличиваем счетчик
                    search_entry.search_count = F('search_count') + 1
                    search_entry.save()

        # Аннотируем количество отзывов и средний рейтинг
        housing = Housing.objects.annotate(
            review_count=Count('reviews'),  # Подсчет количества отзывов
            average_rating=Avg('reviews__rating')
        )

        # Применяем фильтры
        filter = HousingFilter(request.GET, queryset=housing)
        filtered_housing = filter.qs

        # Получаем параметр сортировки
        sort_by = request.GET.get('sort_by')

        # Применение сортировки после фильтрации
        if sort_by == 'price_asc':
            filtered_housing = filtered_housing.order_by('price')
        elif sort_by == 'price_desc':
            filtered_housing = filtered_housing.order_by('-price')
        elif sort_by == 'rating_asc':
            filtered_housing = filtered_housing.order_by('average_rating')  # Сортировка по возрастанию рейтинга
        elif sort_by == 'rating_desc':
            filtered_housing = filtered_housing.order_by('-average_rating')  # Сортировка по убыванию рейтинга
        elif sort_by == 'date_newest':
            filtered_housing = filtered_housing.order_by('-created_at')
        elif sort_by == 'date_oldest':
            filtered_housing = filtered_housing.order_by('created_at')
        elif sort_by == 'rooms_asc':
            filtered_housing = filtered_housing.order_by('rooms')
        elif sort_by == 'rooms_desc':
            filtered_housing = filtered_housing.order_by('-rooms')
        elif sort_by == 'country_asc':
            filtered_housing = filtered_housing.order_by('country')
        elif sort_by == 'country_desc':
            filtered_housing = filtered_housing.order_by('-country')
        elif sort_by == 'city_asc':
            filtered_housing = filtered_housing.order_by('city')
        elif sort_by == 'city_desc':
            filtered_housing = filtered_housing.order_by('-city')
        elif sort_by == 'post_code_asc':
            filtered_housing = filtered_housing.order_by('post_code')
        elif sort_by == 'post_code_desc':
            filtered_housing = filtered_housing.order_by('-post_code')
        elif sort_by == 'views_desc':
            filtered_housing = filtered_housing.order_by('-views')  # Сортировка по просмотрам
        elif sort_by == 'review_count_desc':
            filtered_housing = filtered_housing.order_by('-review_count')  # Сортировка по количеству отзывов

        # Получение популярных запросов (по количеству запросов, сортировка по `search_count`)
        popular_searches = SearchHistory.objects.values('keyword').annotate(
            count=models.Count('keyword')
        ).order_by('-count')[:5]  # Выводим топ-5 популярных запросов

        # Получаем популярные объявления, отсортированные по количеству просмотров
        popular_housing_data = ViewHistory.objects.values('housing').annotate(
            total_views=Sum('view_count')
        ).order_by('-total_views')

        # Создаем список кортежей: (housing_object, total_views)
        popular_housing_list = [
            (Housing.objects.get(id=data['housing']), data['total_views'])
            for data in popular_housing_data
        ]

        # Передача данных в шаблон
        context = {
            'housing': filtered_housing,
            'filter': filter,
            'sort_by': sort_by,  # Передаем значение сортировки обратно в шаблон
            'keyword': keyword,
            'popular_searches': popular_searches,  # Передаем популярные запросы в шаблон
            'popular_housing_list': popular_housing_list, # Передаем список кортежей
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


class SearchViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookings to be viewed or edited.
    """
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)


class ViewHistoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookings to be viewed or edited.
    """
    queryset = ViewHistory.objects.all()
    serializer_class = ViewHistorySerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)


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

    def perform_create(self, serializer):
        """
        Устанавливает текущего пользователя как владельца
        """
        serializer.save(owner=self.request.user)


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
                    return redirect('index')  # Перенаправление на главную или нужную страницу
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
        return render(request, 'booking/message.html', {'error_message': str(e)})


def about(request):
    """
    Страница о программе и ее назначении - меню "О программе"
    """
    return render(request, 'booking/about.html')


@login_required
def create(request):
    """
    Регистрация и редактирование объекта недвижимости
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

    # Проверка, является ли текущий пользователь владельцем объекта
    if request.user == housing.owner:
        messages.error(request, 'Вы не можете забронировать свой собственный объект.')
        return redirect('message')  # Перенаправляем на страницу списка объектов

    reviews = Review.objects.filter(housing=housing).order_by('owner_id')

    # Получение всех занятых дат для данного объекта
    bookings = Booking.objects.filter(housing=housing)
    occupied_dates = []
    for booking in bookings:
        start_date = booking.date_from
        end_date = booking.date_to
        # Создаем список всех дат в диапазоне бронирования
        current_date = start_date
        while current_date <= end_date:
            occupied_dates.append(format(current_date, 'Y-m-d'))
            current_date += timedelta(days=1)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.owner = request.user  # Устанавливаем владельца бронирования
            booking.housing = housing  # Устанавливаем жилье для бронирования

            # Получаем даты из формы
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']

            # Проверка на даты в прошлом
            if date_from < now().date() or date_to < now().date():
                messages.error(request, 'Выбранные даты не могут быть в прошлом. Пожалуйста, выберите другие даты.')
                return render(request, 'booking/create_booking.html', {
                    'form': form,
                    'housing': housing
                })

            # Проверка на корректность порядка дат
            if date_from > date_to:
                messages.error(request, 'Дата начала не может быть позже даты окончания.')
                return render(request, 'booking/create_booking.html', {
                    'form': form,
                    'housing': housing
                })

            # Проверка на наличие пересекающихся бронирований
            overlapping_bookings = Booking.objects.filter(
                housing=housing,
                # Проверяем только подтвержденные и ожидающие подтверждения бронирования
                status__in=[Booking.BookingStatus.CONFIRMED, Booking.BookingStatus.PENDING]
            ).filter(
                # Проверка на пересечение дат
                Q(date_from__lte=date_to, date_to__gte=date_from)
            )

            if overlapping_bookings.exists():
                messages.error(request, 'На выбранные даты объект уже забронирован. Пожалуйста, выберите другие даты.')
                return render(request, 'booking/create_booking.html', {
                    'form': form,
                    'housing': housing
                })

            booking.save()
            messages.success(request, 'Бронирование успешно создано и ожидает подтверждения!')
            return redirect('my_bookings')  # Перенаправляем на страницу бронирования
    else:
        form = BookingForm()

    return render(request, 'booking/create_booking.html', {
        'form': form,
        'housing': housing,
        'reviews': reviews,
        'occupied_dates': occupied_dates,
    })


@login_required
def my_bookings(request):
    # Получение всех бронирований пользователя
    bookings = Booking.objects.filter(owner=request.user)

    # Получение всех отзывов пользователя
    reviews = Review.objects.filter(owner=request.user).select_related('housing')

    # Создание словаря отзывов по id жилья
    housing_reviews = {review.housing.id: review for review in reviews}

    # Добавление флага наличия отзыва в контексте
    context = {
        'bookings': bookings,
        'housing_reviews': housing_reviews,
    }
    return render(request, 'booking/my_bookings.html', context)


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
def housing_detail(request, housing_id):
    """
    Детальная страница объекта жилья
    """
    housing = get_object_or_404(Housing, pk=housing_id)
    reviews = Review.objects.filter(housing=housing)

    # Проверка, есть ли у пользователя запись о просмотре данного объявления
    if request.user.is_authenticated:
        view_entry, created = ViewHistory.objects.get_or_create(
            user=request.user,
            housing=housing
        )
        if not created:
            # Если запись о просмотре уже существует, увеличиваем счетчик просмотров
            view_entry.view_count = F('view_count') + 1
            view_entry.save()

    context = {
        'housing': housing,
        'reviews': reviews
    }
    return render(request, 'booking/housing_detail.html', context)


def message(request):
    """
    Форма вывода сообщения
    """
    return render(request, 'booking/message.html')


@login_required
def delete_housing(request, housing_id):
    """
    Удаление объекта владельцем (не сохраняется в базе)
    """
    housing = get_object_or_404(Housing, id=housing_id)

    # Проверяем, что пользователь является владельцем объекта
    if request.user == housing.owner or request.user.is_staff:
        housing.delete()
        messages.success(request, 'Объект был успешно удален.')
    else:
        messages.error(request, 'У вас нет прав для удаления этого объекта.')

    return redirect('index')


logger = logging.getLogger(__name__)


@login_required
def create_review(request, housing_id):
    """
    Функция оставления отзыва
    """
    housing = get_object_or_404(Housing, pk=housing_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.owner = request.user  # Устанавливаем владельца
            review.housing = housing  # Привязываем отзыв к жилью
            review.save()
            messages.success(request, 'Ваш отзыв успешно создан.')
            return redirect('housing_detail', housing_id=housing_id)
    else:
        form = ReviewForm()

    return render(request, 'booking/create_review.html', {
        'form': form,
        'housing': housing
    })


@login_required
def edit_review(request, review_id):
    """
    Редактирование отзыва
    """
    logger.info(f"Review ID: {review_id}, User: {request.user}")

    # Проверка наличия отзыва для текущего пользователя
    try:
        review = Review.objects.get(pk=review_id, owner=request.user)
    except Review.DoesNotExist:
        logger.error(f"No review found for user {request.user} with review_id {review_id}")
        messages.error(request, "Такого отзыва не существует или он вам не принадлежит.")
        return redirect('my_bookings')  # Перенаправление на страницу с бронированиями

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

