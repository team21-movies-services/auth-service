from pydantic.main import BaseModel
from pydantic.types import conint


class HistoryRequest(BaseModel):
    page: conint(gt=0) = 1
    size: conint(gt=1) = 10

    @property
    def offset(self):
        return (self.page - 1) * self.size

    @property
    def limit(self):
        return self.size
