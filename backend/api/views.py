from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.paginators import PageNumberLimitPagination
from api.permissions import AdminOrReadOnly
from api.serializers import IngredientSerializer, TagSerializer, UserSerializer
from recipes.models import Ingredient, Tag

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
        serializer = UserSerializer(
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
