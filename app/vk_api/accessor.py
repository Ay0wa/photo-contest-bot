import json
import random
import typing
from urllib.parse import urlencode, urljoin

from aiohttp import FormData, TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor

from .dataclasses import (
    Message,
    Photo,
    Poll,
    UploadPhoto,
)
from .errors import VkApiError
from .poller import Poller
from .schemas import (
    PhotoSchema,
    ProfileListSchema,
    ProfileSchema,
    UpdateSchema,
    UploadPhotoSchema,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_PATH = "https://api.vk.com/method/"
API_VERSION = "5.131"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None
        self.album_id: int | None = None
        self.upload_server: str | None = None

    async def connect(self, app: "Application") -> None:
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))

        try:
            await self._get_long_poll_service()
            await self._get_messages_upload_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)

        self.poller = Poller(app.store)
        self.logger.info("start polling")
        self.poller.start()

    async def disconnect(self, app: "Application") -> None:
        if self.session:
            await self.session.close()

        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def _get_long_poll_service(self) -> None:
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="groups.getLongPollServer",
                params={
                    "group_id": self.app.config.bot.group_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as response:
            data = (await response.json())["response"]
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]

    async def _get_messages_upload_service(self) -> None:
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="photos.getMessagesUploadServer",
                params={
                    "group_id": self.app.config.bot.group_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as response:
            data = (await response.json())["response"]
            self.album_id = data["album_id"]
            self.upload_server = data["upload_url"]

    async def poll(self):
        async with self.session.get(
            self._build_query(
                host=self.server,
                method="",
                params={
                    "act": "a_check",
                    "key": self.key,
                    "ts": self.ts,
                    "wait": 30,
                },
            )
        ) as response:
            data = await response.json()
            self.logger.info(data)
            self.ts = data["ts"]
            updates = [
                UpdateSchema().load(update)
                for update in data.get(
                    "updates",
                    [],
                )
            ]

            if updates:
                await self.app.store.bots_manager.handle_updates(updates)

    async def get_chat_members(self, peer_id: int) -> list[ProfileSchema]:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.getConversationMembers",
                params={
                    "peer_id": peer_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as response:
            data = await response.json()
            profiles = ProfileListSchema().load(data)
            self.logger.info(data)
        return profiles

    async def upload_photo(self, image_url) -> UploadPhoto:
        image_file = await self.upload_file(image_url)
        form = FormData()
        form.add_field(
            "photo", image_file, filename="photo.jpg", content_type="image/jpeg"
        )

        async with self.session.post(self.upload_server, data=form) as response:
            data = await response.json()
            upload_photo = UploadPhotoSchema().load(data)
            self.logger.info(upload_photo)
            return UploadPhotoSchema().load(data)

    async def upload_file(self, image_url):
        async with self.session.get(image_url) as response:
            return await response.read()

    async def save_photo(self, upload_photo: UploadPhoto) -> Photo:
        photo = upload_photo.photo
        server = upload_photo.server
        hash_photo = upload_photo.hash

        async with self.session.get(
            self._build_query(
                API_PATH,
                "photos.saveMessagesPhoto",
                params={
                    "access_token": self.app.config.bot.token,
                    "photo": photo,
                    "server": server,
                    "hash": hash_photo,
                },
            )
        ) as response:
            data = await response.json()
            self.logger.info(photo)
        return PhotoSchema().load(data)

    async def send_message(self, message: Message, peer_id: int) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "random_id": random.randint(1, 2**32),
                    "peer_id": peer_id,
                    "message": message.text,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as response:
            data = await response.json()
            if "response" in data:
                self.logger.info(data)
            elif "error" in data:
                self.logger.error(data)
                raise VkApiError(data)
            elif "warning" in data:
                self.logger.warning(data)
                raise VkApiError(data)

    async def send_photo(self, photo: Photo, peer_id: int) -> None:
        owner_id = photo.owner_id
        photo_id = photo.id

        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "access_token": self.app.config.bot.token,
                    "attachment": f"photo{owner_id}_{photo_id}",
                    "peer_id": peer_id,
                    "message": "",
                    "random_id": random.randint(1, 2**32),
                },
            )
        ) as response:
            data = await response.json()
            if "response" in data:
                self.logger.info(data)
            elif "error" in data:
                self.logger.error(data)
                raise VkApiError(data)
            elif "warning" in data:
                self.logger.warning(data)
                raise VkApiError(data)

    async def send_photos(self, list_photos: list[Photo], peer_id: int):
        owner1_id = list_photos[0].owner_id
        photo1_id = list_photos[0].id

        owner2_id = list_photos[1].owner_id
        photo2_id = list_photos[1].id

        photos = f"photo{owner1_id}_{photo1_id},photo{owner2_id}_{photo2_id}"

        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "access_token": self.app.config.bot.token,
                    "attachment": photos,
                    "peer_id": peer_id,
                    "message": "",
                    "random_id": random.randint(1, 2**32),
                },
            )
        ) as response:
            data = await response.json()
            if "response" in data:
                self.logger.info(data)
            elif "error" in data:
                self.logger.error(data)
                raise VkApiError(data)
            elif "warning" in data:
                self.logger.warning(data)
                raise VkApiError(data)

    async def create_poll(
        self,
        peer_id: int,
        question: str,
        answers: list[str],
        is_anonymous: bool = False,
    ) -> dict:
        answers = ["1", "2"]
        async with self.session.get(
            self._build_query(
                self.API_PATH,
                "polls.create",
                params={
                    "question": question,
                    "add_answers": str(answers).replace("'", '"'),
                    "is_anonymous": int(is_anonymous),
                    "owner_id": peer_id,
                    "access_token": self.app.config.bot.token,
                    "v": "5.131",
                },
            )
        ) as response:
            data = await response.json()
            if "response" in data:
                self.logger.info(data)
            elif "error" in data:
                self.logger.error(data)
                raise VkApiError(data)
            elif "warning" in data:
                self.logger.warning(data)
                raise VkApiError(data)
            return data["response"]

    async def send_poll(self, poll: Poll, peer_id: int) -> None:
        owner_id = poll.owner_id
        poll_id = poll.id

        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "access_token": self.app.config.bot.token,
                    "attachment": f"poll{owner_id}_{poll_id}",
                    "peer_id": peer_id,
                    "message": "",
                    "random_id": random.randint(1, 2**32),
                },
            )
        ) as response:
            data = await response.json()
            if "response" in data:
                self.logger.info(data)
            elif "error" in data:
                self.logger.error(data)
                raise VkApiError(data)
            elif "warning" in data:
                self.logger.warning(data)
                raise VkApiError(data)

    async def send_keyboard(self, peer_id: int, message: str):
        keyboard = {
            "one_time": False,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "callback",
                            "payload": '{"button": "start_game"}',
                            "label": "Начать игру",
                        },
                        "color": "negative",
                    }
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "payload": '{"button": "get_last_game"}',
                            "label": "Показать последнюю игру",
                        },
                        "color": "positive",
                    }
                ],
            ],
        }

        json_keyboard = json.dumps(keyboard, ensure_ascii=False)
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "access_token": self.app.config.bot.token,
                    "peer_id": peer_id,
                    "message": message,
                    "keyboard": json_keyboard,
                    "random_id": random.randint(1, 2**32),
                },
            )
        ) as response:
            data = await response.json()
            if "response" in data:
                self.logger.info(data)
            elif "error" in data:
                self.logger.error(data)
                raise VkApiError(data)
            elif "warning" in data:
                self.logger.warning(data)
                raise VkApiError(data)
