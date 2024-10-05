from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse
from pydantic import UUID4

from .schemas import Answer, Message
from .service import answer, get_speech_path, start, transcribe

router = APIRouter()


@router.post("/start", response_model=Message)
async def start_exam():
    msg = await start()
    response = {
        "id": msg.id,
        "text": msg.content,
        "thread_id": msg.thread.id,
    }
    return response


@router.post("/answer", response_model=Message)
async def answer_question(body: Answer):
    message = await answer(body.thread_id, body.text)
    response = {
        "id": str(message.id),
        "text": message.content,
        "thread_id": message.thread.id,
    }
    return response


@router.post("/answer/voice", response_model=Message)
async def answer_voice_question(
    file: Annotated[UploadFile, File()],
    thread_id: Annotated[UUID4, Form()],
):
    transcribed = transcribe(file)
    text = transcribed["text"]
    path = transcribed.get("path")

    msg = await answer(thread_id, text, path)

    response = Message(
        id=msg.id,
        text=msg.content,
        thread_id=msg.thread.id,
    )
    return response


@router.get("/speech/{id}", response_class=FileResponse)
async def get_speech(id: UUID4):
    return await get_speech_path(id)
