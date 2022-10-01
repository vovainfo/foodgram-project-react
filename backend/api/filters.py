from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe

User = get_user_model()


class RecipeFilter(FilterSet):
    # По твоему указанию попробовал сделать с фильтрами а не с кучей кода
    # фильтрации в get_queryset вьюсета. Всё почти ок, но есть нюанс.
    # Проблема с тегами. Если в базе нет записей для какого-то тега,
    # присутствующего в фильтре, то выпадает ошибка. Например, в справочнике
    # тегов есть tag1 и tag2. И пусть в базе есть рецепты только с tag1.
    # Тогда запрос рецептов tags=tag1&tags=tag2 выдасть 400 ошибку.
    # {"tags": ["Select a valid choice. tag2 is not one of the available
    # choices."]}
    # Я нагуглил несколько обсуждений такой проблемы, но решения никто не
    # предоставил.
    # Например https://github.com/carltongibson/django-filter/issues/922
    # Означает ли это, что теги нельзя так фильтровать? Иль можно предположить,
    # что таких тегов не будет (по хорошему, фронт должен сначала запросить
    # список допустимых тегов и потом только позволять по ним фильтровать)?

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorite=self.request.user.id)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(cart=self.request.user.id)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
