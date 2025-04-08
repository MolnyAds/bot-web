import asyncio
import logging
from datetime import datetime, timedelta

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

from environs import Env
from config import ENDPOINT
from web_app import safe_parse_webapp_init_data

# Environment
env = Env()
env.read_env()
BOT_TOKEN = env.str("BOT_TOKEN")

# Logging
logging.basicConfig(level=logging.ERROR)

# Bot and Dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

# Flood prevention storage
SEND_MESSAGE_DELTA: dict[int, datetime] = {}

# HTTP handlers
async def web_start(request: Request) -> web.Response:
    return await aiohttp_jinja2.render_template_async(
        '/', request, {}
    )

async def web_check_user_data(request: Request) -> web.Response:
    data = await request.post()
    payload = safe_parse_webapp_init_data(BOT_TOKEN, data.get("_auth"))
    return json_response({"ok": True, "user": payload.as_json()})

async def web_send_message(request: Request) -> web.Response:
    data = await request.post()
    try:
        payload = safe_parse_webapp_init_data(BOT_TOKEN, data.get("_auth"))
    except ValueError:
        return json_response({"ok": False, "error": "Unauthorized"}, status=401)

    user_id = payload.user.id
    last = SEND_MESSAGE_DELTA.get(user_id, datetime.utcnow() - timedelta(seconds=100))
    if (datetime.utcnow() - last) < timedelta(seconds=5):
        return json_response({"ok": False, "error": "🥶 You're too fast. Wait 5 seconds"})

    target_id = data.get("user_id")
    text = data.get("text")
    if not target_id or not text:
        return json_response({"ok": False, "error": "💁‍♂️ user_id and text are required"})

    try:
        await bot.send_message(chat_id=int(target_id), text=text)
        SEND_MESSAGE_DELTA[user_id] = datetime.utcnow()
    except Exception as e:
        logging.error(f"Send message error: {e}")
        return json_response({"ok": False, "error": "Internal Error"})

    return json_response({"ok": True})

# Setup aiohttp app
app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('web'), enable_async=True)
app.add_routes([
    web.get('/', web_start),
    web.post('/checkUserData', web_check_user_data),
    web.post('/sendMessage', web_send_message),
])

async def on_startup() -> None:
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=45678)
    await site.start()

async def on_shutdown() -> None:
    await storage.close()
    await storage.wait_closed()
    await bot.session.close()

@dp.message(CommandStart())
async def cmd_start(msg: types.Message) -> None:
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[
            types.InlineKeyboardButton(
                text="😎 WEB APP",
                web_app=types.WebAppInfo(url=f"{ENDPOINT}/start")
            )
        ]]
    )
    await msg.reply("TEST WEB APP", reply_markup=keyboard)

async def main() -> None:
    # Start web server
    await on_startup()
    # Start bot polling with bot instance passed explicitly
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Polling error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
