import pytest_asyncio
from faker import Faker

fake = Faker('ru_RU')


def fake_role() -> dict:
    return dict(name=fake.word(), description=fake.text()[:512])


@pytest_asyncio.fixture()
async def fake_role_form() -> dict:
    return fake_role()
