import shutil
import time
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from openai import OpenAI
from src.config import Config

from ..models import Message, Thread

config = Config()

client = OpenAI(
    organization=config.openai_org,
    project=config.openai_project,
    api_key=config.openai_key,
)


assistant = client.beta.assistants.retrieve(config.openai_assistant)


async def ask(text: str, thread: Thread, path: str | None = None) -> Message:
    message = client.beta.threads.messages.create(
        thread_id=thread.name,
        role="user",
        content=text,
    )

    await Message.create(
        content=text,
        role="user",
        thread=thread,
        audio_path=path,
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.name,
        assistant_id=assistant.id,
    )

    for _ in range(100):
        time.sleep(0.1)
        if run.status == "completed":
            break
    else:
        raise HTTPException(status_code=500, detail="Timeout")

    msg = client.beta.threads.messages.list(thread_id=thread.name).data[0]

    ai_msg = await Message.create(
        content=msg.content[0].text.value,
        role="assistant",
        thread=thread,
    )

    return ai_msg


async def start() -> Message:
    t = client.beta.threads.create()

    thread = await Thread.create(name=t.id)

    msg = await ask("Let's start", thread)

    return msg


async def answer(thread_id: str, text: str, path: str | None = None) -> Message:
    thread = await Thread.get(id=thread_id)
    message = await ask(text, thread, path)
    return message


def speak(message: Message) -> str:
    Path("audios/assistant").mkdir(parents=True, exist_ok=True)

    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=message.content,
    )
    path = f"audios/assistant/{message.id}.mp3"
    response.stream_to_file(path)

    return path


def transcribe(file: UploadFile):
    Path("audios/user").mkdir(parents=True, exist_ok=True)
    file_name = f"audios/user/{uuid4()}.mp3"

    with open(file_name, "wb") as f:
        shutil.copyfileobj(file.file, f)

    f = open(file_name, "rb")

    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=f,
    )
    f.close()

    return {"text": response.text, "path": file_name}


async def get_speech_path(id: str) -> str:
    message = await Message.get_or_none(id=id)

    if message is None:
        raise HTTPException(status_code=404, detail="Not found")

    if message.audio_path is None:
        if message.role == "assistant":
            s = speak(message)
            message.audio_path = s
            await message.save()
        else:
            raise HTTPException(status_code=404, detail="Not found")

    return message.audio_path
