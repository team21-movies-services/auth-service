from faker import Faker
import pytest_asyncio
from faker.providers import user_agent

fake = Faker('ru_RU')
fake.add_provider(user_agent)


@pytest_asyncio.fixture()
def fake_user_agent():
    return fake.user_agent()
