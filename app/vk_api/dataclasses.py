from dataclasses import dataclass


@dataclass
class Message:
    user_id: int
    text: str


@dataclass
class UpdateMessage:
    from_id: int
    text: str
    id: int
    action: str | None = None


@dataclass
class UpdateObject:
    message: UpdateMessage


@dataclass
class Update:
    type: str
    object: UpdateObject


@dataclass
class Profile:
    id: int
    screen_name: str
    photo: str


@dataclass
class Photo:
    album_id: int
    id: int
    owner_id: int


@dataclass
class UploadPhoto:
    server: int
    photo: str
    hash_photo: str
