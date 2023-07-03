```bash
.
├── src/backend
│   ├── app
│   │    ├── deps -- fastapi depends
│   │    │   ├── role.py
│   │    │   ├── users.py
│   │    │   └── auth
│   │    │       └── jwthandler.py -- jwt хендлер
│   │    ├── models -- модели алхимии
│   │    │   ├── __init__.py
│   │    │   ├── database.py
│   │    │   ├── role.py
│   │    │   └── users.py
│   │    ├── repositories -- репозитории на read и write
│   │    │   ├── base.py
│   │    │   ├── role.py
│   │    │   └── users.py
│   │    ├── routers -- апи методы
│   │    │   ├── api
│   │    │   │   └── v1
│   │    │   │       ├── role.py
│   │    │   │       ├── jwt.py
│   │    │   │       └── users.py
│   │    │   ├── __init__.py
│   │    │   └── root.py
│   │    ├── schemas -- схемы запросов на валидацию
│   │    │   ├── base.py
│   │    │   ├── role.py
│   │    │   ├── token.py
│   │    │   └── users.py
│   │    ├── scripts -- разного рода скрипты
│   │    │   └── create_superusers.py
│   │    ├── services -- сервисы
│   │    │   ├── role.py
│   │    │   └── users.py
│   │    ├── settings.py -- основной конфиг приложения
│   │    └── main.py -- точка запуска
│   ├── tests
│   │    └── app
│   ├── migrations -- миграции алембика
│   │   ├── env.py
│   │   ├── README
│   │   ├── script.py.mako
│   │   └── versions -- ревизии
│   ├── alembic.ini
│   └── Dockerfile
├── env
│   ├── docker.env
│   └── local.env
├── docker-compose.yaml
├── poetry.lock
├── pyproject.toml -- poetry конфиг
├── Makefile
└── Readme.md
```
