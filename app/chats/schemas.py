from marshmallow import Schema, fields


class ChatIdSchema(Schema):
    chat_id = fields.Int()


class ChatSchema(Schema):
    chat_id = fields.Int()
    bot_state = fields.Str()
    created_at = fields.DateTime()


class ListChatSchema(Schema):
    chats = fields.List(fields.Nested(ChatSchema))
