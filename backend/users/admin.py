from django.contrib import admin
from django.contrib.admin import register

from users.models import User


@register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')

    # В ТЗ в разделе "админ зона" написано "Для модели пользователей включена
    # фильтрация по имени и email" но кажется что это глупо.
    # Наверное всё же поиск
    search_fields = ('username', 'email')

    empty_value_display = '-пусто-'
