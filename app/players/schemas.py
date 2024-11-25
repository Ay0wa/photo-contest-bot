from marshmallow import Schema, fields, validate

from app.players.models import PlayerStatus


class PlayerQuerySchema(Schema):
    id = fields.Int(required=False, allow_none=True, description="ID игрока")
    user_id = fields.Int(
        required=False, allow_none=True, description="ID vk-юзера"
    )
    game_id = fields.Int(required=False, allow_none=True, description="ID игры")
    status = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf([status.value for status in PlayerStatus]),
        description="Статус игрока. Возможные значения: 'winner', 'loser', 'in_game', 'voting",  # noqa: E501
    )
    username = fields.Str(
        required=False, allow_none=True, description="Username игрока"
    )
    is_voted = fields.Boolean(
        required=False, allow_none=True, description="Голос игрока"
    )
    votes = fields.Int(
        required=False,
        allow_none=True,
        description="Количество голосов за игрока",
    )


class PlayerSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()

    username = fields.Str()
    avatar_url = fields.Str()

    votes = fields.Int()
    is_voted = fields.Boolean()

    status = fields.Str()

    created_at = fields.DateTime()

    game_id = fields.Int()


class ListPlayerSchema(Schema):
    players = fields.List(fields.Nested(PlayerSchema))
