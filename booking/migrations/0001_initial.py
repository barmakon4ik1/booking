# Generated by Django 5.1.1 on 2024-09-19 07:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Housing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name of object')),
                ('type', models.CharField(choices=[('APARTMENT', 'Квартира'), ('HOUSE', 'Дом'), ('STUDIO', 'Студия'), ('CASTLE', 'Замок'), ('HOTEL', 'Гостиница'), ('VILLA', 'Вилла'), ('COTTAGE', 'Коттедж')], default='APARTMENT', max_length=20, verbose_name='Type of object')),
                ('country', models.CharField(max_length=50, verbose_name='Country')),
                ('post_code', models.CharField(max_length=10, verbose_name='Postal code')),
                ('city', models.CharField(max_length=50, verbose_name='City')),
                ('street', models.CharField(blank=True, max_length=50, null=True, verbose_name='Street')),
                ('house_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='House number')),
                ('rooms', models.IntegerField(verbose_name='Number of rooms')),
                ('description', models.TextField(verbose_name='Description')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Price')),
                ('is_visible', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('views', models.IntegerField(default=0)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner_housings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'housing',
                'verbose_name_plural': 'housings',
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('CONFIRMED', 'Confirmed'), ('PENDING', 'Pending confirmation'), ('CANCELED', 'Canceled'), ('UNCONFIRMED', 'Unconfirmed')], default='UNCONFIRMED', max_length=20, verbose_name='Status')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('date_from', models.DateField(blank=True, null=True, verbose_name='Booking from')),
                ('date_to', models.DateField(blank=True, null=True, verbose_name='Booking to')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL)),
                ('housing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='booking.housing')),
            ],
            options={
                'verbose_name': 'booking',
                'verbose_name_plural': 'bookings',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(verbose_name='Rating')),
                ('text', models.TextField(verbose_name='Review')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('housing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='booking.housing')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'review',
                'verbose_name_plural': 'reviews',
            },
        ),
        migrations.CreateModel(
            name='SearchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=255)),
                ('search_count', models.PositiveIntegerField(default=1)),
                ('last_searched_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ViewHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view_count', models.PositiveIntegerField(default=1)),
                ('last_viewed_at', models.DateTimeField(auto_now=True)),
                ('housing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.housing')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='housing',
            index=models.Index(fields=['type'], name='booking_hou_type_3d5e2c_idx'),
        ),
        migrations.AddIndex(
            model_name='housing',
            index=models.Index(fields=['price'], name='booking_hou_price_718d97_idx'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['status'], name='booking_boo_status_e01616_idx'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['date_from', 'date_to'], name='booking_boo_date_fr_00dee4_idx'),
        ),
    ]
