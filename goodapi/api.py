import aiohttp
from config import API_URL
from models import Post
from pydantic import TypeAdapter


async def get_posts(page: int = 1, limit: int = 10) -> list[Post]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=API_URL.format(page=page, limit=limit)) as response:
            adapter = TypeAdapter(list[Post])
            return adapter.validate_python(await response.json())
