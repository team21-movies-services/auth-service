from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.registrator import add_factory_to_mapper
from dependencies.common import get_session
from services.user import UserServiceABC, UserService

from repositories import UserRepository


@add_factory_to_mapper(UserServiceABC)
def create_user_service(
    session: AsyncSession = Depends(get_session),
):
    return UserService(
        UserRepository(session=session),
    )
