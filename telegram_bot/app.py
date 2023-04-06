import logging
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook


API_TOKEN = '5068827742:AAFQimcPnXNmz0jEZ5TqTnMwb0cqKybr2aE'

# webhook settings
WEBHOOK_HOST = 'https://30b6-213-230-87-180.eu.ngrok.io'
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = 'localhost'  # or ip
WEBAPP_PORT = 3001

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=["start"])
async def greeting(message: types.Message):
    user = message.from_user.full_name
    await message.answer(f"Hello, {user}!")

@dp.message_handler()
async def echo(message: types.Message):
    # Regular request
    await bot.send_message(message.chat.id, message.text)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')
    # insert code here to run it before shutdown
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp, 
        webhook_path=WEBHOOK_PATH, 
        on_startup=on_startup, 
        on_shutdown=on_shutdown,
        skip_updates=True, 
        host=WEBAPP_HOST, 
        port=WEBAPP_PORT
)