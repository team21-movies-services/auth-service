import pytest_asyncio
from passlib.context import CryptContext
from repositories import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"])


@pytest_asyncio.fixture(scope='session')
async def user_repository(db_session):
    yield UserRepository(session=db_session)


async def create_user(user_repository: UserRepository, **user_data):
    user_data['password'] = pwd_context.encrypt(user_data['password'])
    return await user_repository.create_user(**user_data)


@pytest_asyncio.fixture()
async def auth_user(fake_user: dict, user_repository: UserRepository) -> dict:
    return await create_user(user_repository, **fake_user)


@pytest_asyncio.fixture()
async def auth_admin_user(fake_admin_user: dict, user_repository: UserRepository) -> dict:
    return await create_user(user_repository, **fake_admin_user)
