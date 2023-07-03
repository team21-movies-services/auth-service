from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import mapped_column
from sqlalchemy.types import TypeDecorator, String

Column = mapped_column

metadata = MetaData()

BaseModel = declarative_base(metadata=metadata)


class StrEnum(TypeDecorator):
    impl = String

    def __init__(self, enumtype, *args, **kwargs):
        super(StrEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            return value

        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)
