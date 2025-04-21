import logging
import asyncio
from aiogram import Bot, types, Dispatcher, Router, F, BaseMiddleware
from aiogram import exceptions
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import Command
from typing import Union
from aiogram.utils.keyboard import InlineKeyboardBuilder
from cachetools import TTLCache
from aiogram.dispatcher.flags import get_flag
from typing import Any, Awaitable, Callable, Dict, MutableMapping, Optional
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER, ADMINISTRATOR, KICKED
from aiogram.filters import BaseFilter
from aiogram.types import ChatMemberUpdated, Message, CallbackQuery, WebAppData
import os
import re
import sqlite3
import time

API_TOKEN = ""
ADMIN = 470208396

TEST_CHAT_ID = -1002641661606
CHANNEL_WITH_POSTS = -1002505296360


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('molnyabot')

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# бд
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, chat_id INTEGER)')
cursor.execute('CREATE TABLE IF NOT EXISTS stickerlinks (link_id INTEGER PRIMARY KEY AUTOINCREMENT, link_url TEXT NOT NULL, link_name TEXT)')

# тротлинг антифлуд

DEFAULT_TTL = 0.5
DEFAULT_KEY = "default"


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple throttling middleware using TTLCache
    This is just an example and does not need to be combined with AlbumMiddleware

    Usage example:
    router.message.middleware(ThrottlingMiddleware(spin=2.0))

    And then:
        @router.message(Command("dice"))
        @flags.throttling_key("spin")
        async def dice(message: Message) -> Any:
            pass
    """

    def __init__(
            self,
            *,
            default_key: Optional[str] = DEFAULT_KEY,
            default_ttl: float = DEFAULT_TTL,
            **ttl_map: float,
    ) -> None:
        """
        :param default_key: The cache key to be used by default.
        Set to None to disable throttling by default.
        :param default_ttl: The TTL in default cache
        :param ttl_map: Creates additional cache instances with different TTL
        """
        if default_key:
            ttl_map[default_key] = default_ttl

        self.default_key = default_key
        self.caches: Dict[str, MutableMapping[int, None]] = {}

        for name, ttl in ttl_map.items():
            self.caches[name] = TTLCache(maxsize=10_000, ttl=ttl)

    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: types.TelegramObject,
            data: Dict[str, Any],
    ) -> Optional[Any]:
        user: Optional[types.User] = data.get("event_from_user", None)

        if user is not None:
            throttling_key = get_flag(data, "throttling_key", default=self.default_key)
            if throttling_key and user.id in self.caches[throttling_key]:
                return None
            self.caches[throttling_key][user.id] = None

        return await handler(event, data)


# тип чата
class ChatTypeFilter(BaseFilter):  # [1]
    def __init__(self, chat_type: Union[str, list]):  # [2]
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:  # [3]
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type

class MessageTextFilter(BaseFilter):  # [1]
    def __init__(self, message_text: Union[str, list]): # [2]
        self.message_text = message_text

    async def __call__(self, message: Message) -> bool:  # [3]
        if isinstance(message.text, str):
            return self.message_text in message.text.strip()
        else:
            return False

class AdminFilter(BaseFilter):  # [1]
    async def __call__(self, message: Message) -> bool:  # [3]
        return message.from_user.id == ADMIN


class ForwardFilter(BaseFilter):  # [1]
    async def __call__(self, message: Message) -> bool:  # [3]
        if message.forward_from is not None:
            return True
        return False


router = Router()
dp.include_routers(router)
#dp.message.middleware(ThrottlingMiddleware())


async def start(user_id, chat_id):
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    existing_user = cursor.fetchone()
    if existing_user is None:
        cursor.execute('INSERT INTO users (id, chat_id) VALUES (?, ?)', (user_id, chat_id))
        conn.commit()
        await bot.send_message(ADMIN, f"👤 Новый пользователь в боте:\n{user_id}")

    keyboard = types.InlineKeyboardMarkup(
    inline_keyboard=[[
        types.InlineKeyboardButton(
            text="😎 WEB APP",
            web_app=types.WebAppInfo(url=f"https://tydu4.github.io/start")
        )
    ]]
    )
    photo = types.FSInputFile(r"photo/5.jpg")
    await bot.send_photo(chat_id=chat_id, photo=photo, caption="*Салам* 🐉",parse_mode='Markdown', reply_markup=keyboard)



class GetUserAdPost(StatesGroup):
    wait_for_post = State()
    confirm_post = State()

@router.message(Command("post"), ChatTypeFilter(chat_type=["private"]))
async def ask_for_post(message: Message, state: FSMContext):
    await message.reply("Скинь пост мне, деньги нужны мне", parse_mode='Markdown')
    await state.set_state(GetUserAdPost.wait_for_post)

@router.message(GetUserAdPost.wait_for_post, F)
async def receive_post_and_ask_confirm(message: Message, state: FSMContext):
    await state.update_data(post_id=message.message_id)

    await bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id, message_id=message.message_id)

    kb = [
        [types.KeyboardButton(text=r"️Иди на хуй")],
        [types.KeyboardButton(text=r"️-")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await bot.send_message(chat_id=message.chat.id, text="Подходит?", reply_markup=keyboard)
    await state.set_state(GetUserAdPost.confirm_post)

@router.message(GetUserAdPost.confirm_post, F.text)
async def process_confirmation(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    post_id = data.get('post_id')

    if "Иди на хуй" in text:
        await bot.send_message(chat_id=message.chat.id, text="Сообщение сохранено", reply_markup=types.ReplyKeyboardRemove())
        await bot.copy_message(chat_id=CHANNEL_WITH_POSTS, from_chat_id=message.chat.id, message_id=post_id)
        await state.clear()
    else:
        await bot.send_message(chat_id=message.chat.id, text="Тогда отправь пост заново", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(GetUserAdPost.wait_for_post)


    

@router.chat_join_request()
async def start1(update: types.ChatJoinRequest):
    await update.approve()
    user_id = update.from_user.id
    await bot.send_message(chat_id=user_id, text=f"*Ваша заявка в {update.chat.title} одобрена, приятного времяпровождения 😈*", parse_mode='Markdown')
    await bot.send_message(ADMIN, f"👤 Новый пользователь присоединился в канал:\n{user_id}")
    await start(user_id, user_id)

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=ADMINISTRATOR))
async def bot_added_as_admin(event: ChatMemberUpdated):
    # if event.chat.type == "channel" то это канал его ток хенлдить
    await bot.send_message(chat_id=TEST_CHAT_ID, text=f"Я админ {event.chat.type} ID чата: {event.chat.id}")

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def bot_added_as_admin_from_member(event: ChatMemberUpdated):
    await bot.send_message(chat_id=TEST_CHAT_ID, text=f"Я мембер {event.chat.type} ID чата: {event.chat.id}")

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER))
async def bot_added_as_member(event: ChatMemberUpdated):
    await bot.send_message(chat_id=TEST_CHAT_ID, text=f"Я не мембер {event.chat.type} ID чата: {event.chat.id}")

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_unblocked_bot(event: ChatMemberUpdated):
    await bot.send_message(chat_id=TEST_CHAT_ID, text=f"Меня кикнули {event.chat.type} ID чата: {event.chat.id}")


@router.message(ChatTypeFilter(chat_type=["private", "group", "supergroup"]), Command(r"start"))
async def start_command(message: types.Message):
    await start(message.from_user.id, message.chat.id)

@router.message(AdminFilter(), ChatTypeFilter(chat_type=["private"]), Command("database"))
async def send_database(message: types.Message):
    doc = types.FSInputFile("users.db")
    await bot.send_document(message.chat.id, doc)


# Обработчик команды для получения количества пользователей
@router.message(AdminFilter(), ChatTypeFilter(chat_type=["private"]), Command("count"))
async def count_users(message: types.Message):
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    await message.reply(f"🔐 В базе данных {count} пользователей.")



@router.message(AdminFilter(), ForwardFilter(), ChatTypeFilter(chat_type=["private"]))
async def send_message(message: types.Message):
    blocked = 0
    sent = 0
    cursor.execute('SELECT chat_id FROM users')
    chat_ids = cursor.fetchall()
    await bot.send_message(ADMIN, "📥 Началась рассылка!")
    for chat_id in chat_ids:
        try:
            await bot.forward_message(chat_id[0], message.chat.id, message.message_id)
            sent += 1
        except Exception as e:
            blocked += 1
    await bot.send_message(ADMIN,
                           f"📤 Рассылка закончилась.\n✅ Было отправлено {sent} сообщений\n🚫 Бот заблокирован у {blocked} пользователей")


@router.message(ChatTypeFilter(chat_type=["private"]), F.text)
async def ask_pack_link(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await start(user_id, user_id)

@router.errors()
async def send_errors(event: types.ErrorEvent):
    await bot.send_message(ADMIN, f"❌ Ошибка в router errors:\n{event}")

async def main():
    # Запускаем Dispatcher и выполняем функцию on_startup
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    # Запускаем цикл событий (event loop) и выполняем функцию main
    asyncio.run(main())
