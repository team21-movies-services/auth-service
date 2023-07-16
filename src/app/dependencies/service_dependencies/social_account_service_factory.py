from dependencies.common import get_session
from dependencies.registrator import add_factory_to_mapper
from fastapi import Depends
from repositories import SocialAccountRepository, UserRepository
from services.social_account import SocialAccountService, SocialAccountServiceABC
from sqlalchemy.ext.asyncio import AsyncSession


@add_factory_to_mapper(SocialAccountServiceABC)
def create_social_account_service(
    session: AsyncSession = Depends(get_session),
):
    return SocialAccountService(
        SocialAccountRepository(session=session),
        UserRepository(session=session),
    )
