from fastapi import FastAPI, Request
from aiogram import types, Bot, Dispatcher
from app import bot, dp

app = FastAPI()

@app.post("/webhook")
async def handle_webhook(request: Request):
    updates = await request.json()
    update = types.Update(**updates)
    # # Handle the update data from Telegram here
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(update=update)
