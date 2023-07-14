from dependencies.common import get_session, get_redis_client
from functional.settings import get_settings
from main import app
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.sql import text as sa_text
from models.base import BaseModel, metadata

settings = get_settings()


@pytest_asyncio.fixture(name='db_session', scope='session')
async def session_fixture():
    engine = create_async_engine(settings.postgres.database_url, echo=settings.postgres.echo_log)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
    )
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def clean_db(db_session):
    meta = metadata
    clear_table_sql = 'TRUNCATE {} CASCADE;'.format(
        ','.join(f'auth.{table.name}' for table in reversed(meta.sorted_tables))
    )
    await db_session.execute(sa_text(clear_table_sql))
    await db_session.commit()


@pytest_asyncio.fixture(name="api_client", scope='session')
async def client_fixture(db_session, redis_client):
    def get_session_override():
        return db_session

    def get_redis_override():
        return redis_client

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_redis_client] = get_redis_override
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def refresh_object(db_session):
    async def inner(obj):
        try:
            await db_session.refresh(obj)
        except InvalidRequestError:
            return None
        return obj

    return inner
