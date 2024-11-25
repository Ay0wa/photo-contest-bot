from marshmallow import Schema, fields, validate

from app.games.models import GameStatus


class GameQuerySchema(Schema):
    chat_id = fields.Int(required=False, allow_none=True, description="ID чата")
    game_id = fields.Int(required=False, allow_none=True, description="ID игры")
    current_round = fields.Int(
        required=False, allow_none=True, description="Текущий раунд"
    )
    status = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf([status.value for status in GameStatus]),
        description="Статус игры. Возможные значения: 'in_progress', 'finished', 'canceled'",  # noqa: E501
    )


class GameSchema(Schema):
    id = fields.Int()

    current_round = fields.Int()
    status = fields.Str()

    created_at = fields.DateTime()

    finished_at = fields.DateTime(required=False)
    game_time = fields.DateTime(required=False)

    chat_id = fields.Int()


class ListGameSchema(Schema):
    games = fields.List(fields.Nested(GameSchema))
