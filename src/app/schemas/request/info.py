from pydantic.main import BaseModel
from schemas.request.common import PaginationRequestType


class HistoryRequest(BaseModel):
    page: PaginationRequestType.page = 1
    size: PaginationRequestType.size = 10

    @property
    def offset(self):
        return (self.page - 1) * self.size

    @property
    def limit(self):
        return self.size
