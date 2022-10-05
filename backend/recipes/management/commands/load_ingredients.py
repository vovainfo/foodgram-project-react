import json

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов'
    ingfilename = 'ingredients.json'

    def handle(self, *args, **options):
        try:
            n_load = 0
            with open(self.ingfilename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    try:
                        Ingredient.objects.create(name=item["name"],
                                                  measurement_unit=item[
                                                      "measurement_unit"])
                        n_load += 1
                    except IntegrityError:
                        print(f'Ингридиет {item["name"]} '
                              f'{item["measurement_unit"]} '
                              f'уже есть в базе')
            print(
                f'Из файла {self.ingfilename} загружено {n_load} ингредиентов'
            )

        except FileNotFoundError:
            print(f'{self.ingfilename} not found.')
