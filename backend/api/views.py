from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientSearchFilter, RecipeFilter
from api.permissions import AdminOrReadOnly, OwnerAndAdminOrReadOnly
from api.serializers import (IngredientSerializer, RecipeLiteSerializer,
                             RecipeSerializer, TagSerializer, UserSerializer,
                             UserSubscribeSerializer)
from recipes.models import Ingredient, Recipe, RecipeIngredientLink, Tag

User = get_user_model()
CONTENT_TYPE_SHOPPING_FILE = 'text/plain'


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
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = (AdminOrReadOnly,)
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (OwnerAndAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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

        response = HttpResponse(shopping_text,
                                content_type=CONTENT_TYPE_SHOPPING_FILE)
        response['Content-Disposition'] = (
            f'attachment; filename={settings.SHOPPING_FILE}'
        )
        return response
