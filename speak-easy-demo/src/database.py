from tortoise import Tortoise


async def init():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3", modules={"models": ["src.models"]}
    )
    await Tortoise.generate_schemas()


async def close():
    await Tortoise.close_connections()
