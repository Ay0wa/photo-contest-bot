import json
import random
import typing
from urllib.parse import urlencode, urljoin

from aiohttp import FormData, TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor

from .dataclasses import Message, Photo, UploadPhoto
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

    async def _api_request(self, method: str, params: dict) -> dict:
        url = self._build_query(API_PATH, method, params)
        try:
            async with self.session.get(url) as response:
                data = await response.json()
                if "error" in data:
                    self.logger.error(
                        f"Ошибка VK API: {data['error']['error_msg']} "
                        f"(код: {data['error']['error_code']})"
                    )
                    raise VkApiError(data)
                if "warning" in data:
                    self.logger.warning(
                        f"""Предупреждение VK API:
                        {data.get('warning', 'Нет деталей')}"""
                    )
                return data
        except VkApiError:
            raise
        except Exception as e:
            self.logger.error(f"Неизвестная ошибка при запросе к VK API: {e}")
            raise

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
        params = {
            "peer_id": peer_id,
            "access_token": self.app.config.bot.token,
        }
        try:
            data = await self._api_request(
                "messages.getConversationMembers", params
            )
            profiles = ProfileListSchema().load(data)
            self.logger.info(f"Участники чата {peer_id} успешно получены.")
            return profiles
        except Exception as e:
            self.logger.error(
                f"Ошибка при получении участников чата {peer_id}: {e}"
            )
            return []

    async def upload_photo(self, image_url) -> UploadPhoto:
        image_file = await self.upload_file(image_url)
        form = FormData()
        form.add_field(
            "photo", image_file, filename="photo.jpg", content_type="image/jpeg"
        )
        try:
            async with self.session.post(
                self.upload_server, data=form
            ) as response:
                data = await response.json()
                if "error" in data:
                    self.logger.error(f"Ошибка загрузки фото: {data}")
                    raise VkApiError(data)
                photo = UploadPhotoSchema().load(data)
                self.logger.info(f"Фотография успешно загружена.")
                return photo
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке фото: {e}")
            raise

    async def upload_file(self, image_url):
        async with self.session.get(image_url) as response:
            return await response.read()

    async def save_photo(self, upload_photo: UploadPhoto) -> Photo:
        params = {
            "access_token": self.app.config.bot.token,
            "photo": upload_photo.photo,
            "server": upload_photo.server,
            "hash": upload_photo.hash,
        }

        try:
            photo_data = await self._api_request(
                "photos.saveMessagesPhoto", params
            )
            photo = PhotoSchema().load(photo_data)
            self.logger.info(f"Фотография успешно сохранена: {photo}")
            return photo
        except VkApiError as vk_error:
            self.logger.error(
                f"Ошибка VK API при сохранении фотографии: {vk_error}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Неизвестная ошибка при сохранении фотографии: {e}"
            )
            raise

    async def send_message(
        self,
        message: Message,
        peer_id: int,
        keyboard={},
    ) -> None:
        json_keyboard = json.dumps(keyboard, ensure_ascii=False)
        params = {
            "random_id": random.randint(1, 2**32),
            "peer_id": peer_id,
            "message": message.text,
            "access_token": self.app.config.bot.token,
            "keyboard": json_keyboard,
        }
        try:
            await self._api_request("messages.send", params)
            self.logger.info(f"Сообщение успешно отправлено в чат {peer_id}.")
        except Exception as e:
            self.logger.error(
                f"Ошибка при отправке сообщения в чат {peer_id}: {e}"
            )
            raise

    async def send_photo(self, photo: Photo, peer_id: int) -> None:
        params = {
            "access_token": self.app.config.bot.token,
            "attachment": f"photo{photo.owner_id}_{photo.id}",
            "peer_id": peer_id,
            "message": "",
            "random_id": random.randint(1, 2**32),
        }
        try:
            await self._api_request("messages.send", params)
            self.logger.info(
                f"Фотография {photo.id} успешно отправлена в чат {peer_id}."
            )
        except Exception as e:
            self.logger.error(
                f"Ошибка при отправке фотографии в чат {peer_id}: {e}"
            )
            raise

    async def send_photos(self, list_photos: list[Photo], peer_id: int):
        if len(list_photos) < 2:
            self.logger.error("Для отправки требуется минимум две фотографии.")
            raise ValueError(
                "Список фотографий должен содержать минимум две фотографии."
            )

        photos = ",".join(
            [f"photo{photo.owner_id}_{photo.id}" for photo in list_photos[:2]]
        )

        params = {
            "access_token": self.app.config.bot.token,
            "attachment": photos,
            "peer_id": peer_id,
            "message": "",
            "random_id": random.randint(1, 2**32),
        }

        try:
            response = await self._api_request("messages.send", params)
            self.logger.info(
                f"""Фотографии {photos} успешно отправлены в чат {peer_id}. 
                Ответ: {response}"""
            )
        except VkApiError as vk_error:
            self.logger.error(
                f"""Ошибка VK API при отправке фотографий {photos}
                в чат {peer_id}: {vk_error}"""
            )
            raise
        except Exception as e:
            self.logger.error(
                f"""Неизвестная ошибка при отправке фотографий
                {photos} в чат {peer_id}: {e}"""
            )
            raise