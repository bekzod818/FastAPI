from enum import Enum

from tortoise import fields
from tortoise.models import Model


class Role(str, Enum):
    user = "user"
    assistant = "assistant"


class Thread(Model):
    id = fields.UUIDField(primary_key=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    name = fields.CharField(max_length=200, unique=True)

    class Meta:
        table = "threads"


class Message(Model):
    id = fields.UUIDField(primary_key=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    content = fields.TextField()
    role = fields.CharEnumField(Role)
    thread = fields.ForeignKeyField("models.Thread", related_name="messages")
    audio_path = fields.CharField(max_length=200, null=True, default=None)

    class Meta:
        table = "messages"
