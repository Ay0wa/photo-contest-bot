from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    post_load,
    pre_load,
    validates,
)

from .dataclasses import (
    Action,
    Payload,
    Photo,
    Profile,
    ProfileList,
    Update,
    UpdateMessage,
    UpdateObject,
    UploadPhoto,
)


class ProfileSchema(Schema):
    id = fields.Int()
    screen_name = fields.Str()
    photo_100 = fields.Url()

    @post_load
    def make_profile(self, data, **kwargs):
        return Profile(**data)

    class Meta:
        unknown = EXCLUDE


class ProfileListSchema(Schema):
    profiles = fields.List(fields.Nested(ProfileSchema))

    @post_load
    def make_profile_list(self, data, **kwargs):
        return ProfileList(**data)

    @pre_load
    def validate_response(self, data, **kwargs):
        if "response" not in data:
            raise ValidationError("Cant find response in data")

        return data.get("response")

    class Meta:
        unknown = EXCLUDE


class PhotoSchema(Schema):
    album_id = fields.Int()
    id = fields.Int()
    owner_id = fields.Int()

    @post_load
    def make_photo(self, data, **kwargs):
        return Photo(**data)

    @pre_load
    def validate_response(self, data, **kwargs):
        if "response" not in data:
            raise ValidationError("Cant find response in data")

        return data.get("response")[0]

    class Meta:
        unknown = EXCLUDE


class UploadPhotoSchema(Schema):
    server = fields.Int()
    photo = fields.Str()
    hash = fields.Str()

    @post_load
    def make_upload_photo(self, data, **kwargs):
        return UploadPhoto(**data)

    @validates("photo")
    def validate_photo_format(self, photo):
        if photo == []:
            raise ValidationError("Error image format")

    class Meta:
        unknown = EXCLUDE


class PayloadSchema(Schema):
    button = fields.Str()

    @post_load
    def make_payload(self, data, **kwargs):
        return Payload(**data)

    class Meta:
        unknown = EXCLUDE


class ActionSchema(Schema):
    type = fields.Str()
    member_id = fields.Int(required=False, allow_none=True)

    @post_load
    def make_action(self, data, **kwargs):
        return Action(**data)

    class Meta:
        unknown = EXCLUDE


class UpdateMessageSchema(Schema):
    from_id = fields.Int()
    text = fields.Str()
    id = fields.Int()
    peer_id = fields.Int()
    action = fields.Nested(ActionSchema, required=False)

    @post_load
    def make_update_message(self, data, **kwargs):
        return UpdateMessage(**data)

    class Meta:
        unknown = EXCLUDE


class UpdateObjectSchema(Schema):
    message = fields.Nested(UpdateMessageSchema, required=False)

    user_id = fields.Int(required=False)
    peer_id = fields.Int(required=False)
    payload = fields.Nested(PayloadSchema, required=False)

    @post_load
    def make_update_object(self, data, **kwargs):
        return UpdateObject(**data)

    class Meta:
        unknown = EXCLUDE


class UpdateSchema(Schema):
    type = fields.Str()
    object = fields.Nested(UpdateObjectSchema)

    @post_load
    def make_update(self, data, **kwargs):
        return Update(**data)

    class Meta:
        unknown = EXCLUDE


# class AnswerSchema:
#     id = fields.Int()
#     text = fields.Str()
#     votes = fields.Int()
#     rate = fields.Number()

#     @post_load
#     def make_poll(self, data, **kwargs):
#         return Answer(**data)


# class PollSchema(Schema):
#     id = fields.Int()
#     owner_id = fields.Int()
#     answers = fields.List(fields.Nested(AnswerSchema))

#     @post_load
#     def make_poll(self, data, **kwargs):
#         return Poll(**data)

#     class Meta:
#         unknown = EXCLUDE
