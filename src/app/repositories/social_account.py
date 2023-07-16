import logging

from sqlalchemy.exc import IntegrityError

from common.exceptions.social_account import SocialAccountAlreadyExists
from models.social_account import SocialAccount
from repositories.base import SQLAlchemyRepository

logger = logging.getLogger(__name__)


class SocialAccountRepository(SQLAlchemyRepository[SocialAccount]):
    model = SocialAccount

    async def create_social(self, **fields) -> SocialAccount:
        """Создание пользователя в БД postgres."""
        social_db = self.model(**fields)
        self.session.add(social_db)
        try:
            await self.session.commit()
        except IntegrityError:
            raise SocialAccountAlreadyExists()
        return social_db
