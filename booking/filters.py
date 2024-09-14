from django_filters import *
from rest_framework import filters
from .models import *
from django.db.models import Q


class FilterByKeywords:
    """
    Класс для фильтрации queryset по ключевым словам через указанные поля.
    При необходимости, его можно использовать в других фильтрах,
    просто передав нужные поля.
    """

    # Поля, по которым будет производиться поиск:
    keyword_fields = []

    def filter(self, queryset, value):
        """
        Фильтрует queryset по указанным полям, используя ключевое слово.
        """
        if not value or not self.keyword_fields:
            return queryset

        query = Q()

        # Создание динамического запроса
        # для фильтрации по ключевым словам в нескольких полях модели.
        # В self.keyword_fields содержатся названия полей модели,
        # по которым будет осуществляться поиск.
        for field in self.keyword_fields:

            # Сложный запрос с использованием ИЛИ(|) на основе множества полей,
            # который проверяет на содержание value в поле, независимо от регистра
            query |= Q(**{f"{field}__icontains": value})

        return queryset.filter(query)


class HousingFilter(FilterSet):
    # Переменная для диапазона цен:
    price_range = CharFilter(
        method='filter_by_price_range',
        label='Диапазон цен: минимальная, максимальная'
    )

    # Фильтры для модели Housing:
    type = ChoiceFilter(
        field_name="type",
        choices=Housing.HousingType.choices,
        label="Выберите тип объекта:"
    )
    price_min = NumberFilter(
        field_name="price",
        lookup_expr='gte',
        label="Введите нижний предел стоимости за сутки: "
    )
    price_max = NumberFilter(
        field_name="price",
        lookup_expr='lte',
        label="Введите верхний предел стоимости за сутки: "
    )
    rooms = NumberFilter(
        field_name="rooms",
        label="Введите желаемое число комнат: "
    )

    # Используем FilterByKeywords для фильтрации по ключевым словам
    keyword = CharFilter(
        method='filter_by_keyword',
        label='Поиск по ключевым словам, Введите слово или его часть в названии объекта, описании, адреса или '
              'индекса населенного пункта: ',
    )

    class Meta:
        model = Housing
        fields = ['type', 'price_range', 'price_min', 'price_max', 'rooms', 'keyword']

    def filter_by_keyword(self, queryset, name, value):
        """
        Использует FilterByKeywords для фильтрации по ключевым словам.
        """
        keyword_filter = FilterByKeywords()

        # Список полей, по которым производится поиск, задается в фильтре HousingFilter.
        keyword_filter.keyword_fields = [
            'name',
            'description',
            'country',
            'city',
            'street',
            'postal_code'
        ]
        return keyword_filter.filter(queryset, value)

    def filter_by_price_range(self, queryset, name, value):
        """
        Фильтрует по диапазону цен, переданному в формате 'min, max'.
        """
        if value:
            try:
                min_price, max_price = map(float, value.split(','))
                return queryset.filter(price__gte=min_price, price__lte=max_price)
            except ValueError:
                # Если не удалось преобразовать значения, возвращаем пустой QuerySet
                return queryset.none()
        return queryset

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем сортировку по умолчанию здесь:
        self.queryset = self.queryset.order_by('-id')




