# Cars API

## Описание проекта

Cars API — это RESTful API для торговой площадки автомобилей, включающий как новые, так и подержанные автомобили. Проект построен с использованием принципов чистой архитектуры и предоставляет надежную систему аутентификации и авторизации пользователей с JWT-токенами.

## Технологический стек

- **Python 3.12+**
- **FastAPI** — быстрый и современный веб-фреймворк
- **PostgreSQL** — реляционная база данных
- **SQLAlchemy** — ORM для работы с базой данных
- **Alembic** — инструмент для миграций базы данных
- **JWT** — для аутентификации и авторизации
- **Pydantic** — для валидации данных и управления настройками
- **Docker** — для контейнеризации приложения

## Архитектура проекта

Проект построен с использованием принципов чистой архитектуры и состоит из следующих слоев:

- **Interface** — содержит контроллеры API, схемы данных и зависимости
- **Core** — содержит бизнес-логику и доменные модели
- **Infrastructure** — содержит репозитории и модели данных

## Установка и запуск

### Предварительные требования

- Python 3.12 или выше
- PostgreSQL
- Виртуальное окружение Python

### Шаги по установке

1. Клонируйте репозиторий:

```bash
git clone https://github.com/username/cars_v2.0.git
cd cars_v2.0
```

2. Создайте и активируйте виртуальное окружение:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/MacOS
# или
.venv\Scripts\activate  # Windows
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения (или используйте файл `.env`):

```bash
cp src/.env.example src/.env
# Отредактируйте файл .env в соответствии с вашими настройками
```

5. Запустите миграции:

```bash
cd src
alembic upgrade head
```

6. Запустите сервер:

```bash
python main.py
```

После запуска API будет доступен по адресу http://localhost:8010

## Структура проекта

```
src/
├── core/                  # Бизнес-логика и доменные модели
│   ├── entites/           # Доменные модели
│   │   ├── car.py         # Модели для автомобилей, брендов и т.д.
│   │   └── auth.py        # Модели для аутентификации
│   ├── exceptions.py      # Пользовательские исключения
│   ├── InterfaceRepositories/ # Интерфейсы репозиториев
│   │   ├── IAuth.py       # Интерфейс репозитория аутентификации
│   │   └── ICar.py        # Интерфейс репозитория автомобилей
│   └── services/          # Сервисы бизнес-логики
│       ├── auth.py        # Сервис аутентификации
│       └── car.py         # Сервис автомобилей
├── infrastructure/        # Слой инфраструктуры
│   ├── models/            # Модели SQLAlchemy
│   │   ├── auth.py        # Модели для аутентификации
│   │   ├── car.py         # Модели для автомобилей
│   │   └── base.py        # Базовые классы моделей
│   ├── postgres_db.py     # Настройки базы данных
│   └── repositories/      # Реализации репозиториев
│       ├── auth.py        # Репозиторий аутентификации
│       └── car.py         # Репозиторий автомобилей
├── interface/             # API и веб-интерфейс
│   ├── dependencies.py    # Зависимости FastAPI
│   ├── main.py            # Главное приложение FastAPI
│   ├── routers/           # Маршруты API
│   │   ├── secured/       # Защищенные маршруты (требуют авторизацию)
│   │   │   ├── user.py    # Маршруты пользователей
│   │   │   ├── car.py     # Маршруты автомобилей
│   │   │   ├── admin_car.py # Маршруты администрирования автомобилей
│   │   │   └── auth.py    # Маршруты управления правами
│   │   └── public/        # Публичные маршруты
│   │       ├── auth.py    # Публичные маршруты аутентификации
│   │       └── car.py     # Публичные маршруты автомобилей
│   └── schemas/           # Pydantic-схемы
│       ├── auth.py        # Схемы аутентификации
│       └── car.py         # Схемы автомобилей
├── migrations/            # Миграции Alembic
├── alembic.ini            # Конфигурация Alembic
├── logger.py              # Настройка логирования
├── main.py                # Точка входа в приложение
└── settings.py            # Настройки приложения
```

## API эндпоинты

### Аутентификация

- `POST /api/public/auth/login` — Вход в систему
- `GET /api/public/auth/logout` — Выход из системы
- `GET /api/public/auth/refresh` — Обновление JWT-токена

### Пользователи

- `POST /api/secured/user/create` — Создание нового пользователя
- `GET /api/secured/user/get/{user_id}` — Получение информации о пользователе

### Управление правами доступа

- `POST /api/secured/auth/users/{user_id}/scopes` — Добавление прав пользователю
- `PUT /api/secured/auth/users/{user_id}/scopes` — Полное обновление прав пользователя
- `DELETE /api/secured/auth/users/{user_id}/scopes` — Удаление прав у пользователя
- `GET /api/secured/auth/users/{user_id}/scopes` — Получение списка прав пользователя
- `GET /api/secured/auth/me/scopes` — Получение своих прав

### Публичные эндпоинты автомобилей

- `GET /api/public/cars` — Получение списка автомобилей
- `GET /api/public/cars/{car_id}` — Получение информации об автомобиле
- `GET /api/public/cars/brands` — Получение списка брендов
- `GET /api/public/cars/brands/{brand_id}` — Получение информации о бренде
- `GET /api/public/cars/models` — Получение списка моделей
- `GET /api/public/cars/models/{model_id}` — Получение информации о модели

### Пользовательские эндпоинты автомобилей

- `POST /api/secured/cars` — Создание объявления о продаже автомобиля
- `PUT /api/secured/cars/{car_id}` — Обновление своего объявления
- `DELETE /api/secured/cars/{car_id}` — Удаление своего объявления
- `GET /api/secured/cars/my` — Получение списка своих объявлений

### Административные эндпоинты автомобилей

- `POST /api/secured/admin/cars/brands` — Создание нового бренда
- `PUT /api/secured/admin/cars/brands/{brand_id}` — Обновление информации о бренде
- `DELETE /api/secured/admin/cars/brands/{brand_id}` — Удаление бренда
- `POST /api/secured/admin/cars/models` — Создание новой модели
- `PUT /api/secured/admin/cars/models/{model_id}` — Обновление информации о модели
- `DELETE /api/secured/admin/cars/models/{model_id}` — Удаление модели
- `PUT /api/secured/admin/cars/listings/{car_id}` — Администрирование объявления
- `DELETE /api/secured/admin/cars/listings/{car_id}` — Удаление любого объявления

## Система прав доступа

В приложении используется гибкая система прав доступа на основе JWT-токенов. Каждый пользователь имеет набор прав (scopes), определяющих его возможности:

- `user:read` — Чтение информации о пользователях
- `user:update` — Изменение информации о пользователях
- `car:read` — Чтение информации об автомобилях
- `car:create` — Создание объявлений
- `car:update` — Обновление своих объявлений
- `car:delete` — Удаление своих объявлений
- `admin` — Полный доступ ко всем функциям
- `admin:car:create` — Создание брендов и моделей
- `admin:car:update` — Обновление брендов и моделей
- `admin:car:delete` — Удаление брендов, моделей и любых объявлений

## Работа с миграциями

Для управления схемой базы данных используется Alembic.

### Создание новой миграции:

```bash
alembic revision --autogenerate -m "описание миграции"
```

### Применение миграций:

```bash
alembic upgrade head
```

### Откат миграции:

```bash
alembic downgrade -1
```

## Разработка и тестирование

### Запуск в режиме разработки:

```bash
python main.py
```

### Доступ к документации API:

После запуска сервера документация API доступна по адресу:

- Swagger UI: http://localhost:8010/docs
- ReDoc: http://localhost:8010/redoc

## Модели данных

### Автомобили

- **Brand** — бренд автомобиля (например, Toyota, BMW)
- **Model** — модель автомобиля (например, Camry, X5)
- **Car** — объявление о продаже автомобиля с подробной информацией

### Перечисления

- **FuelType** — тип топлива (бензин, дизель, электро, гибрид)
- **TransmissionType** — тип коробки передач (механика, автомат, робот, вариатор)
- **DriveType** — привод (передний, задний, полный)
- **CarCondition** — состояние автомобиля (новый, с пробегом)
