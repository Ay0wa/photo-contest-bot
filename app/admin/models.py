import bcrypt
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class AdminModel(BaseModel):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    password: Mapped[str]

    @staticmethod
    def check_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
