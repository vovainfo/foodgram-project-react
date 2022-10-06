from django.contrib import admin
from django.contrib.admin import register

from recipes.models import Ingredient, Recipe, RecipeIngredientLink, Tag


class RecipeInlineTags(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1
    verbose_name = 'рецепт с этим тегом'
    verbose_name_plural = 'рецепты с этим тегом'


class RecipeInlineIngredients(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    verbose_name = 'рецепт с этим ингредиентом'
    verbose_name_plural = 'рецепты с этим ингредиентом'


class InlineIngredientsInRecipe(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


@register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit', )
    empty_value_display = '-пусто-'
    inlines = (RecipeInlineIngredients,)


@register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    search_fields = ('name', 'slug', 'color')
    empty_value_display = '-пусто-'
    inlines = (RecipeInlineTags,)


@register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'count_favorites')
    fields = ('name', 'author', 'cooking_time',
               'cart', 'tags', 'favorite', 'image')

    search_fields = ('name', )
    list_filter = ('tags', )
    empty_value_display = '-пусто-'
    inlines = (InlineIngredientsInRecipe,)

    def count_favorites(self, obj):
        return obj.favorite.count()


@register(RecipeIngredientLink)
class RecipeIngredientLinkAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredients', 'amount')
    search_fields = ('recipe__author__username', 'recipe__author__email')
    list_filter = ('recipe__tags',)
    empty_value_display = '-пусто-'
