from fastapi import Depends, FastAPI
from sqlmodel import Session, select

from .db import get_session, init_db
from .models import Song, SongCreate

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


@app.get("/songs", response_model=list[Song])
def get_songs(session: Session = Depends(get_session)):
    result = session.execute(select(Song))
    songs = result.scalars().all()
    return [Song(name=song.name, artist=song.artist, id=song.id) for song in songs]


@app.post("/songs")
def add_song(song: SongCreate, session: Session = Depends(get_session)):
    song = Song(name=song.name, artist=song.artist)
    session.add(song)
    session.commit()
    session.refresh(song)
    return song
