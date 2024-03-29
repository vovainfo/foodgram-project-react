from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (CurrentUserDefault, ModelSerializer,
                                        SerializerMethodField, ValidationError)
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, Recipe, RecipeIngredientLink, Tag

User = get_user_model()


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField(method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'password')
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return user.subscribe.filter(id=obj.id).exists()

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('name', 'measurement_unit')
        validators = (
            UniqueTogetherValidator(
                queryset=Ingredient.objects.all(),
                fields=('name', 'measurement_unit')
            ),
        )


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('name', 'color', 'slug')


class RecipeLiteSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    author = UserSerializer(read_only=True, default=CurrentUserDefault())
    ingredients = SerializerMethodField(method_name='get_ingredients')
    is_favorited = SerializerMethodField(method_name='get_is_favorited')
    is_in_shopping_cart = SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('is_favorite', 'is_shopping_cart', 'author')
        validators = (
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'author')
            ),
        )

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.carts.filter(id=obj.id).exists()

    def validate(self, data):  # noqa: max-complexity: 11
        name = self.initial_data.get('name')
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')

        if not isinstance(tags, list):
            raise ValidationError('Некорректный список тэгов')
        if not isinstance(ingredients, list):
            raise ValidationError('Некорректный список ингредиентов')

        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise ValidationError(f'некорректный тэг {tag}')

        cooking_time = str(self.initial_data.get('cooking_time'))
        if not cooking_time.isdigit():
            raise ValidationError(
                'Время приготовления не является целым числом'
            )
        if int(cooking_time) < settings.RECIPE_MIN_COOKING_TIME:
            raise ValidationError(
                f'Время приготовления менее {settings.RECIPE_MIN_COOKING_TIME}'
            )

        valid_ingredient = []
        for ingr in ingredients:
            ingr_id = ingr.get('id')
            ingredient_queryset = Ingredient.objects.filter(id=ingr_id)
            if not ingredient_queryset.exists():
                raise ValidationError(f'некорректный ингредиент {ingr}')
            ingredient = ingredient_queryset[0]

            amount = str(ingr.get('amount'))
            if not amount.isdigit():
                raise ValidationError(
                    f'Кол-во у <{ingredient.name}> не является целым числом'
                )
            if int(amount) < settings.RECIPE_MIN_AMOUNT:
                raise ValidationError(
                    f'Кол-во у <{ingredient.name}> меньше '
                    f'{settings.RECIPE_MIN_AMOUNT}'
                )

            ingr_exist = filter(
                lambda item: item['ingredient'] == ingredient, valid_ingredient
            )
            if len(list(ingr_exist)) != 0:
                raise ValidationError(
                    f'<{ingredient.name}> повторяется в рецепте'
                )

            valid_ingredient.append(
                {'ingredient': ingredient, 'amount': amount}
            )

        data['name'] = name
        data['tags'] = tags
        data['ingredients'] = valid_ingredient
        data['author'] = self.context.get('request').user
        return data

    @transaction.atomic
    def create(self, validated_data):
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            RecipeIngredientLink.objects.get_or_create(
                recipe=recipe,
                ingredients=ingredient['ingredient'],
                amount=ingredient['amount']
            )

        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')

        recipe.image = validated_data.get('image', recipe.image)
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time
        )

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            for ingredient in ingredients:
                RecipeIngredientLink.objects.get_or_create(
                    recipe=recipe,
                    ingredients=ingredient['ingredient'],
                    amount=ingredient['amount']
                )
        recipe.save()
        return recipe


class UserSubscribeSerializer(UserSerializer):
    recipes = RecipeLiteSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField(method_name='get_recipes_count')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name', 'is_subscribed', 'recipes',
                            'recipes_count')

    def get_is_subscribed(*args):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()
