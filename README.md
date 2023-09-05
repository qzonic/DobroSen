# CI/CD
![Workflow](https://github.com/qzonic/DobroSen/actions/workflows/main.yml/badge.svg)

# Стек
<img src="https://img.shields.io/badge/Python-4169E1?style=for-the-badge"/><img src="https://img.shields.io/badge/Django-008000?style=for-the-badge"/> <img src="https://img.shields.io/badge/DRF-800000?style=for-the-badge"/> <img src="https://img.shields.io/badge/Docker-00BFFF?style=for-the-badge"/> <img src="https://img.shields.io/badge/PostgreSQL-87CEEB?style=for-the-badge"/> <img src="https://img.shields.io/badge/Nginx-67c273?style=for-the-badge"/> <img src="https://img.shields.io/badge/Gunicorn-06bd1e?style=for-the-badge"/><img src="https://img.shields.io/badge/Redis-800000?style=for-the-badge"/> <img src="https://img.shields.io/badge/Celery-06bd1e?style=for-the-badge"/>

# Описание проекта:

**Проект ToDo**

Проект представляет из себя расширенный функционал ToDo-списка, добавлена возможность присваивать задачам категории и поддержку пользовательских аккаунтов.
Дополнительно было реализоавнно:
* При создании задачи, полбзователь, который указан в `assigned_to`, получает уведомление на почту.
* Возможность прикрепления файлов к задачам.
* Сортировка и пагинация для списка задач.
* Возможность устанавливать срок выполнения для задачи.
* Возможность создавать подзадачи.
* Добавлен приоритет к задачам и сортировка по нему.
* Добавлена возможность проанализировать выполнение своих задач.
* Тесты для основного функционала приложения.

Открыть проект в интернете [тык](http://94.228.124.37/api/v1/).


# Реализация

1. Фреймворки: проект основан на фреймворках Django и Django Rest.
2. Модели: реализованы модели `Category`, `Task`, `Subtask`.
3. Работа с категориями: новую категорию может создать только авторизованный пользователь.
3. Работа с задачами: пользователь может взаимодействовать только с теми задачами, которые он создал.
4. Тесты: в проекте написаны тесты, которые находятся в приложении `api`, для проверки реализованного функционала.
5. Инфраструктура: для упрощения работы с проектом были реализованы следующие пункты:
   * проект развернут в докере, используется `Dockerfile` и `docker-compose.yml`;
   * образ проекта хранится в `DockerHub`;
   * для упрощения деплоя настроена автоматизации в `CI/CD`.

# Как запустить проект:

*Клонировать репозиторий и перейти в него в командной строке:*
```
https://github.com/qzonic/DobroSen.git
```
```
cd DobroSen/
```

В директории Dobro нужно создать .env файл, в котором указывается 
SECRET_KEY, HOST, DB_NAME, POSTGRES_USER, POSTGRES_PASSWORD, DB_HOST, DB_PORT,
REDIS_HOST, REDIS_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD.
Например:
```
SECRET_KEY='django-insecure-w2rvabrrx4_u=qfar0k*%zumx3l*d8@+v==%0o-i8k3(&9ut^='
DEBUG=True
HOST=94.228.117.21

DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

EMAIL_HOST_USER='test@mail.ru'
EMAIL_HOST_PASSWORD='fdsfsf3r33r3wssdf3r'
```

*Теперь необходимо собрать Docker-контейнеры:*
```
docker-compose up -d
```

*После сборки контейнеров, нужно прописать следующие команды по очереди:*
```
docker-compose exec web python3 manage.py migrate
```

```
docker-compose exec web python3 manage.py createsuperuser
```

```
docker-compose exec web python3 manage.py collectstatic --no-input
```

*Теперь проект доступен по адресу:*
```
http://127.0.0.1/
```

*Эндпоинты для взаимодействия с API можно посмотреть в документации по адресу:*
```
/api/v1/redoc/
```

### Автор
[![telegram](https://img.shields.io/badge/Telegram-Join-blue)](https://t.me/qzonic)
