import pytest_asyncio
from faker import Faker
from faker.providers import profile

fake = Faker('ru_RU')
fake.add_provider(profile)


def fake_user_info() -> dict:
    return dict(first_name=fake.first_name_male(), last_name=fake.last_name_male())


def fake_user_data():
    password = fake.password(length=10, special_chars=False, digits=True, upper_case=True, lower_case=True)
    return dict(
        email=fake.email(),
        password=password,
        **fake_user_info(),
    )


@pytest_asyncio.fixture()
async def fake_user() -> dict:
    return fake_user_data()


@pytest_asyncio.fixture()
async def fake_admin_user() -> dict:
    user_data = fake_user_data()
    user_data['is_superuser'] = True
    return user_data


@pytest_asyncio.fixture()
async def fake_user_form_registration(fake_user) -> dict:
    fake_user['password_confirm'] = fake_user['password']
    return fake_user


@pytest_asyncio.fixture()
async def fake_user_form_login(fake_user) -> dict:
    return dict(email=fake_user['email'], password=fake_user['password'])


@pytest_asyncio.fixture()
async def password_change_form(fake_user):
    new_password = fake.password(length=10, special_chars=False, digits=True, upper_case=True, lower_case=True)
    return dict(password=fake_user['password'], new_password=new_password, new_password_confirm=new_password)
