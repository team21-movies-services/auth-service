import logging

from models.device import AuthDevice
from repositories.base import SQLAlchemyRepository

logger = logging.getLogger(__name__)


class DeviceRepository(SQLAlchemyRepository):
    model = AuthDevice
