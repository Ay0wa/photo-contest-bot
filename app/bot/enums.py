from enum import StrEnum, auto


class PayloadButton(StrEnum):
    cancel_game = auto()
    start_game = auto()
    get_last_game = auto()
