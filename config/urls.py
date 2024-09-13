from django.contrib import admin
from django.urls import path, include

import booking

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('booking.urls')),
]
