from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.permissions import AdminOrReadOnly, OwnerAndAdminOrReadOnly
from api.serializers import (IngredientSerializer, RecipeLiteSerializer,
                             RecipeSerializer, TagSerializer, UserSerializer,
                             UserSubscribeSerializer)
from recipes.models import Ingredient, Recipe, RecipeIngredientLink, Tag

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    permission_classes = (IsAuthenticated,)

    @action(methods=('get', 'post', 'delete'), detail=True)
    def subscribe(self, request, id):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        obj = get_object_or_404(self.queryset, id=id)
        serializer = UserSerializer(
            obj, context={'request': self.request}
        )
        is_obj_exist = user.subscribe.filter(id=id).exists()

        if (self.request.method in ('GET', 'POST')) and not is_obj_exist:
            user.subscribe.add(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if (self.request.method == 'DELETE') and is_obj_exist:
            user.subscribe.remove(obj)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('get',), detail=False)
    def subscriptions(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        authors = user.subscribe.all()
        pages = self.paginate_queryset(authors)
        serializer = UserSubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    permission_classes = (AdminOrReadOnly,)
    serializer_class = IngredientSerializer

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return self.queryset.filter(name__contains=name)
        return self.queryset


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = (AdminOrReadOnly,)
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (OwnerAndAdminOrReadOnly,)

    def get_queryset(self):
        queryset = self.queryset

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        user = self.request.user
        if user.is_anonymous:
            return queryset

        is_in_shopping = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping == '1':
            queryset = queryset.filter(cart=user.id)
        elif is_in_shopping == '0':
            queryset = queryset.exclude(cart=user.id)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1':
            queryset = queryset.filter(favorite=user.id)
        if is_favorited == '0':
            queryset = queryset.exclude(favorite=user.id)

        return queryset  # noqa: R504

    def __add_del_m2m(self, pk, m2m) -> Response:
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        obj = get_object_or_404(self.queryset, id=pk)
        serializer = RecipeLiteSerializer(
            obj, context={'request': self.request}
        )
        obj_exist = m2m.filter(id=pk).exists()

        if (self.request.method in ('GET', 'POST')) and not obj_exist:
            m2m.add(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if (self.request.method == 'DELETE') and obj_exist:
            m2m.remove(obj)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('get', 'post', 'delete'), detail=True)
    def favorite(self, request, pk):
        return self.__add_del_m2m(pk, self.request.user.favorites)

    @action(methods=('get', 'post', 'delete'), detail=True)
    def shopping_cart(self, request, pk):
        return self.__add_del_m2m(pk, self.request.user.carts)

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = RecipeIngredientLink.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            ing=F('ingredients__name'),
            unit=F('ingredients__measurement_unit')
        ).annotate(cnt=Sum('amount')).order_by()

        rows = [f'{i["ing"]} ({i["unit"]}) - {i["cnt"]}' for i in ingredients]
        shopping_text = f'Список покупок {str(user)}\n\n' + '\n'.join(rows)

        response = HttpResponse(shopping_text, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=list.txt'
        return response
