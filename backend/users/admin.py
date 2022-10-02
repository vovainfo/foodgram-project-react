from django.contrib import admin
from django.contrib.admin import register

from recipes.models import Recipe
from users.models import User


class RecipeInlineCart(admin.TabularInline):
    model = Recipe.cart.through
    extra = 1
    verbose_name_plural = 'рецепты в корзине юзера'


class RecipeInlineFavorite(admin.TabularInline):
    model = Recipe.favorite.through
    extra = 1
    verbose_name_plural = 'рецепты в избранном у юзеру'


@register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')

    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'
    inlines = (RecipeInlineCart, RecipeInlineFavorite)
