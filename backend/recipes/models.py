from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Ингредиент', max_length=200)
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name', )
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_unit'
            ),
        )

    def __str__(self) -> str:
        return f'{self.name}; {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(verbose_name='Тэг', max_length=200, unique=True)
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=7,
        unique=True
    )
    slug = models.SlugField(verbose_name='Слаг', max_length=200)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name', )

    def __str__(self) -> str:
        return f'{self.name}, {self.color}'


class Recipe(models.Model):
    name = models.CharField(verbose_name='Название блюда', max_length=200)
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Состав блюда',
        related_name='recipes',
        through='RecipeIngredientLink'
    )
    favorite = models.ManyToManyField(
        User,
        verbose_name='Избранные рецепты',
        related_name='favorites',
        blank=True
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    cart = models.ManyToManyField(
        User,
        verbose_name='Список покупок',
        related_name='carts',
        blank=True
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    image = models.ImageField(verbose_name='Фото блюда', upload_to='images/')
    text = models.TextField(verbose_name='Описание блюда')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(MinValueValidator(settings.RECIPE_MIN_COOKING_TIME), )
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_name_author'
            ),
        )

    def __str__(self) -> str:
        return f'{self.name} Автор: {self.author.username}'


class RecipeIngredientLink(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты',
        related_name='ingredient',
        on_delete=models.CASCADE
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipe',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(MinValueValidator(settings.RECIPE_MIN_AMOUNT), )
    )

    class Meta:
        verbose_name = 'Ингридиенты в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'
        ordering = ('recipe', )
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredients'),
                name='unique_recipe_ingredients'
            ),
        )

    def __str__(self) -> str:
        return f'{self.ingredients} - {self.amount}'
