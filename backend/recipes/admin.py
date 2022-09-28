from django.contrib import admin
from django.contrib.admin import register

from recipes.models import Ingredient, Recipe, RecipeIngredientLink, Tag


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


@register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'count_favorites')
    search_fields = ('name', )
    list_filter = ('tags', 'author')
    empty_value_display = '-пусто-'

    def count_favorites(self, obj):
        return obj.favorite.count()


@register(RecipeIngredientLink)
class RecipeIngredientLinkAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredients', 'amount')
    empty_value_display = '-пусто-'
