from django.contrib import admin
from django.contrib.admin import register

from recipes.models import Ingredient


@register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')

    search_fields = ('name',)
    list_filter = ('measurement_unit', )

    empty_value_display = '-пусто-'
