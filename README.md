# Foodgram - сервис публикации рецептов
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Как запустить проект

### Клонируйте репозиторий:
Склонировать репозиторий на локальную машину:
```
git clone https://github.com/vovainfo/foodgram-project-react
```
### Подготовьте docker образ для frontend
Из директории \frontend выполните:
```
docker login -u <имя пользователя DockerHub
docker build -t <имя пользователя DockerHub>/foodgram_frontend:latest .
docker push <имя пользователя DockerHub>/foodgram_frontend:latest
```

### Подготовьте docker образ для backend
В корневой директории проекта выполните:
```
docker login -u <имя пользователя DockerHub
docker build -t <имя пользователя DockerHub>/foodgram_backend:latest .
docker push <имя пользователя DockerHub>/foodgram_backend:latest
```

### Подготовка работы на удаленном сервером (ubuntu):
Установите docker и docker-compose на сервер:
```
sudo apt install docker.io
sudo curl -SL https://github.com/docker/compose/releases/download/v2.11.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
Для проверки установки введите: 
```
sudo docker-compose --version
```

* Отредактируйте файл infra/nginx.conf, в строке server_name впишите IP своего сервера
* Скопируйте этот файл на сервер в /home/<username>/nginx.conf
* Скопируйте файл docker-compose.yml с корневой директории на сервер в /home/<username>/
* Файл backend/.env скопируйте в папку /home/<username>/ и отредайтируйте (например, задав свой SECRET_KEY и POSTGRES_PASSWORD)* 

### Запуск приложения в контейнерах
Подключитесь к серверу по ssh и выполните
```
sudo docker-compose up -d
```

#### Соберите статические файлы
```
sudo docker-compose exec -T backend python manage.py collectstatic --no-input
```
#### Выполните миграции:
```
sudo docker-compose exec -T backend python manage.py migrate --noinput
```
#### Загрузите фикстуры ингредиентов
```
sudo docker-compose exec -T backend python manage.py load_ingredients
```
#### Создайте суперпользователя Django
```
sudo docker-compose exec backend python manage.py createsuperuser
```

## Автор:
- [Владимир Гуменников](https://github.com/vovainfo)


## Адреса сервера с работающим приложением
* http://51.250.92.225/ - приложение
* http://51.250.92.225/admin/ - панель администратора
* логин администратора: msn
* пароль администратора: 1