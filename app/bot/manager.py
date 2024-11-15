import typing
from logging import getLogger

from app.vk_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]) -> None:
        for update in updates:
            if update.object.message.text == "ava":
                await self.handle_start()
            elif len(update.object.message.text) > 0:
                await self.handle_message(update)
            elif update.object.message.action:
                await self.handle_action(update)

    async def handle_message(self, update: Update) -> None:
        await self.app.store.vk_api.send_message(
            Message(
                user_id=update.object.message.from_id,
                text=update.object.message.text,
            )
        )

    async def handle_action(self, update: Update) -> None:
        if update.object.message.action == "chat_invite_user":
            await self.handle_start()

    async def handle_start(self):
        members = await self.app.store.vk_api.get_chat_members()

        for member in members:
            upload_photo = await self.app.store.vk_api.upload_photo(
                image_url=member.photo
            )
            photo_data = await self.app.store.vk_api.save_photo(upload_photo)
            await self.app.store.vk_api.send_avatar(photo_data)
