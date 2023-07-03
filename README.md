# auth-service

* link =

# Стек технологий
- Frontend (Nginx) - маршрутизация запросов
- Backend (Fastapi) - получение и обработка запросов пользователя
- SQL СУБД (Postgres) - хранение информации о пользователях, истории входов в ЛК, роли + привилегии
- NOSQL БД (Redis) - хранение недействительных access-токенов, (хранение refresh-токенов?)

## backend библиотеки
* `fastapi` - основной backend фреймворк
* `pydantic` - валидация входящих данных api
* `uvicorn` - локальный запуск проекта, `gunicorn` - запуск в прод. окружении
* `redis` - библиотека для работы с redis
* `sqlalchemy` - ORM
* `asyncpg` - асинхронный драйвер для `sqlalchemy`
* `alembic` - миграция моделей в БД postgres
* `psycopg2-binary` - синхронный драйвер для миграций
* `pyjwt` - библиотека для работы с jwt


### Линтеры
* flake8, mypy, bandit

# Init development

1) init poetry and pre-commit
```bash
poetry install --no-root
```

```bash
poetry run pre-commit install
```

2) env
```bash
cp ./.env.template ./.env
```
* `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` - пользователь, пароль, название БД с которыми будет создана БД в postgres.

```bash
cp ./src/.env.template ./src/.env
```

* `SQL_USER`, `SQL_PASSWORD`, `SQL_DATABASE`, `SQL_HOST`, `SQL_PORT` - настройки подключения к БД postgres
* `JWT_SECRET_KEY`, `YANDEX_CLIENT_ID`, `YANDEX_CLIENT_SECRET`, etc - секреты

3) build and up docker local
```bash
make build-local
make up-local
```
