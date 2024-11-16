import datetime

from sqlalchemy.orm import DeclarativeBase
from typing import Annotated

from sqlalchemy.orm import mapped_column

from sqlalchemy import text

created_at = Annotated[
    datetime.datetime,
    mapped_column(server_default=text("TIMEZONE('utc', now())"))
]

class BaseModel(DeclarativeBase):
    pass