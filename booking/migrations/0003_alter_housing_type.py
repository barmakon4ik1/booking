# Generated by Django 5.1.1 on 2024-09-16 16:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("booking", "0002_rename_user_review_owner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="housing",
            name="type",
            field=models.CharField(
                choices=[
                    ("APARTMENT", "Квартира"),
                    ("HOUSE", "Дом"),
                    ("STUDIO", "Студия"),
                    ("CASTLE", "Замок"),
                    ("HOTEL", "Гостиница"),
                    ("VILLA", "Вилла"),
                    ("COTTAGE", "Коттедж"),
                ],
                default="APARTMENT",
                max_length=20,
                verbose_name="Type of object",
            ),
        ),
    ]
