from aiohttp.web import HTTPForbidden
from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemas import AdminSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        email = self.data["email"]
        password = self.data["password"]

        admin = await self.store.admins.get_by_email(email)
        if not admin or not admin.check_password(password, admin.password):
            raise HTTPForbidden

        admin_data = AdminSchema().dump(admin)
        session = await new_session(self.request)
        session["admin"] = admin_data

        return json_response(data=admin_data)


class AdminCurrentView(AuthRequiredMixin, View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        return json_response(data=AdminSchema().dump(self.request.admin))
