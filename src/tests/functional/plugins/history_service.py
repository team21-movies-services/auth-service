from random import SystemRandom
from typing import List
import pytest_asyncio

from models import AuthUser
from models.history import AuthHistory, ActionType
from repositories import HistoryRepository, DeviceRepository


@pytest_asyncio.fixture(scope='session')
async def history_repository(db_session):
    yield HistoryRepository(session=db_session)


@pytest_asyncio.fixture(scope='session')
async def device_repository(db_session):
    yield DeviceRepository(session=db_session)


@pytest_asyncio.fixture()
async def device(device_repository: DeviceRepository, fake_user_agent):
    return await device_repository.get_or_create(user_agent=fake_user_agent)


@pytest_asyncio.fixture()
async def user_history(request, auth_user: AuthUser, db_session, device) -> List[AuthHistory]:
    cryptogen = SystemRandom()
    history_db = [
        AuthHistory(user_id=auth_user.id, device_id=device.id, action_type=cryptogen.choice(list(ActionType)))
        for _ in range(request.param)
    ]
    db_session.add_all(history_db)
    await db_session.commit()
    return history_db
