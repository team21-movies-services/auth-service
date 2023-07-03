from pydantic.types import conint


class PaginationRequestType:
    page = conint(gt=0)
    size = conint(gt=1)
