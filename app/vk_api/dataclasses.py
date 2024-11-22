from dataclasses import dataclass


@dataclass
class Message:
    text: str
    user_id: int | None = None


@dataclass
class Payload:
    button: str


@dataclass
class Event:
    event_id: int
    peer_id: int
    from_id: int
    payload: Payload


@dataclass
class Action:
    type: str
    payload: str | None = None
    label: str | None = None
    member_id: int | None = None


@dataclass
class UpdateMessage:
    from_id: int
    text: str
    id: int
    peer_id: int
    action: Action | None = None


@dataclass
class UpdateObject:
    message: UpdateMessage | None = None

    event_id: str | None = None
    user_id: int | None = None
    peer_id: int | None = None
    payload: str | None = None


@dataclass
class Update:
    type: str
    object: UpdateObject


@dataclass
class Profile:
    id: int
    screen_name: str
    photo_100: str


@dataclass
class ProfileList:
    profiles: list[Profile]


@dataclass
class Photo:
    album_id: int
    id: int
    owner_id: int


@dataclass
class UploadPhoto:
    server: int
    photo: str
    hash: str


# @dataclass
# class Answer:
#     id: int
#     text: str
#     votes: int
#     rate: float

# @dataclass
# class Poll:
#     id: int
#     owner_id: int
#     answers: list[Answer]
