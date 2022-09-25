from django.contrib import admin
from django.contrib.admin import register

from recipes.models import Ingredient, Tag


@register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')

    search_fields = ('name',)
    list_filter = ('measurement_unit', )

    empty_value_display = '-пусто-'


@register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')

    search_fields = ('name', 'slug', 'color')

    empty_value_display = '-пусто-'
