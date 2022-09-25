from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, UserViewSet, TagViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, 'users')
router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('tags', TagViewSet, 'tags')

urlpatterns = (
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
)
