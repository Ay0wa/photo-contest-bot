from aiohttp_apispec import querystring_schema, response_schema

from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response

from .schemas import ChatIdSchema, ChatSchema, ListChatSchema


class ChatListView(AuthRequiredMixin, View):
    @querystring_schema(ChatIdSchema)
    @response_schema(ListChatSchema, 200)
    async def get(self):
        query_params = ChatIdSchema().load(self.request.query)
        if query_params.get("chat_id"):
            chat = await self.store.chats.get_by_chat_id(
                chat_id=int(query_params.get("chat_id")),
            )
            return json_response(data=ChatSchema().dump(chat))
        chats = {"chats": await self.store.chats.list_chats()}
        return json_response(data=ListChatSchema().dump(chats))
