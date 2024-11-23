from typing import TYPE_CHECKING

from sqlalchemy import select

from app.admin.models import AdminModel
from app.base.base_accessor import BaseAccessor

from .hash import hash_password

if TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        email = app.config.admin.email
        password = app.config.admin.password
        await self.create_admin(email, password)

    async def get_by_email(self, email: str) -> AdminModel | None:
        query = select(AdminModel).filter_by(email=email)

        async with self.app.database.session() as session:
            res = await session.execute(query)

            return res.scalars().first()

    async def create_admin(self, email: str, password: str) -> AdminModel:
        hashed_password = hash_password(password)
        admin = AdminModel(
            email=email,
            password=hashed_password,
        )
        async with self.app.database.session() as session:
            session.add(admin)
            await session.commit()

        return admin
