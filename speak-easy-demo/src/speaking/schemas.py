from pydantic import UUID4, BaseModel


class Answer(BaseModel):
    text: str
    thread_id: UUID4


class Message(BaseModel):
    id: UUID4
    text: str
    thread_id: UUID4
