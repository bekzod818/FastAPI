import asyncio

from api import get_posts


async def main():
    posts = await get_posts(page=2, limit=5)

    for post in posts:
        print(post.post_id)


if __name__ == "__main__":
    asyncio.run(main())
