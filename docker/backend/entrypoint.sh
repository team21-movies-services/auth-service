#!/bin/sh

poetry run alembic upgrade head

exec "$@"
