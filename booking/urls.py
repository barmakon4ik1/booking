from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from django.contrib.auth import views as auth_views


router = DefaultRouter()
router.register('housings', HousingViewSet, basename='housings')
router.register('booking', BookingViewSet, basename='booking')
router.register('reviews', ReviewViewSet, basename='reviews')
router.register('users', UserViewSet, basename='users')
router.register('views', ViewHistoryViewSet, basename='views')
router.register('search', SearchViewSet, basename='search')

urlpatterns = [
    path('housing_list/', housing_list, name='housing_list'),
    path('housing/edit/<int:housing_id>/', edit_housing, name='edit_housing'),
    path('housing/delete/<int:housing_id>/', delete_housing, name='delete_housing'),
    path('message/', message, name='message'),
    path('delete/<int:housing_id>/', delete_housing, name='delete_housing'),

    path('booking/create/<int:housing_id>/', create_booking, name='create_booking'),
    path('my_bookings/', my_bookings, name='my_bookings'),
    path('my_confirmation/', my_confirmation, name='my_confirmation'),
    path('cancel-booking/<int:booking_id>/', cancel_booking, name='cancel_booking'),
    path('booking/edit/<int:booking_id>/', edit_booking, name='edit_booking'),
    path('housing/<int:housing_id>/', housing_detail, name='housing_detail'),
    path('booking/<int:booking_id>/change-status/', change_booking_status, name='change_booking_status'),
    path('booking-details/', BookingDetailListCreateView.as_view(), name='booking-details-list'),
    path('bookings/<int:pk>', BookingDetailListRetrieveUpdateView.as_view(), name='bookings-retrieve-update-delete'),

    path('review/create/<int:housing_id>/', create_review, name='create_review'),
    path('review/edit/<int:review_id>/', edit_review, name='edit_review'),

    path('', index, name='index'),
    path('about', about, name='about'),
    path('create/', create, name='create'),

    path('login', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),

    # Страница для запроса сброса пароля
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    # Страница для подтверждения сброса пароля
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),

    # Страница, куда приходит пользователь по ссылке сброса
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Страница успешного завершения сброса
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('api/', include(router.urls)),
]
