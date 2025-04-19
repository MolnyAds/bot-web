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
from aiogram.filters import BaseFilter
from aiogram.types import Message
import os
import re
import sqlite3
import time

API_TOKEN = ""
ADMIN = 123


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('copybot')

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
    kb = [
        [types.KeyboardButton(text="😨 Каталог стикеров❓"),],
    ]
    
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    photo = types.FSInputFile(r"photo/5.png")
    await bot.send_photo(chat_id=chat_id, photo=photo, caption="*Приветствую, выбери с чем бот может тебе помочь 🤝*\n\n👋 Этот бот может *копировать стикеры и эмодзи.*\n\nWelcome! 🤙🏻 *This bot can copy stickers and emojis.*\n\n[e4zybot](t.me/e4zybot) *x* [HelpLovBot](t.me/HelpLovBot)",parse_mode='Markdown', reply_markup=keyboard)

@router.chat_join_request()
async def start1(update: types.ChatJoinRequest):
    await update.approve()
    user_id = update.from_user.id
    await bot.send_message(chat_id=user_id, text=f"*Ваша заявка в {update.chat.title} одобрена, приятного времяпровождения 😈*", parse_mode='Markdown')
    await bot.send_message(ADMIN, f"👤 Новый пользователь присоединился в канал:\n{user_id}")
    await start(user_id, user_id)

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



@router.message(AdminFilter(), ChatTypeFilter(chat_type=["private"]), Command("addpack"))
async def add_my_pack(message: types.Message):
    find = re.search(r"t\.me/add(stickers|emoji)/(\w+) (.+)", message.text)
    if not find:
        await message.reply("🤬 Невалидная ссылка")
        return
    set_name = find[2]
    emoji_or_stickers = find[1]
    link_name = find[3]
    full_link = f"http://t.me/add{emoji_or_stickers}/{set_name}"
    # Получаем информацию о стикерпаке
    try: 
        sticker_set = await bot.get_sticker_set(set_name)
    except Exception as e:
        await message.reply("🤬 такого пака нет")
        return
    # Выполняем SQL-запрос для проверки наличия ссылки в базе данных
    cursor.execute("SELECT * FROM stickerlinks WHERE link_url=?", (full_link,))
    result = cursor.fetchone()

    if result is not None:
        await message.reply(f"🤬 Ссылка с URL '{full_link}' уже существует в базе данных.")
    else:
        cursor.execute("INSERT INTO stickerlinks (link_url, link_name) VALUES (?, ?)", (full_link, link_name))
        await message.reply(f"Ссылка {full_link} добавлена в базу данных")

@router.message(AdminFilter(), ChatTypeFilter(chat_type=["private"]), Command("delpack"))
async def del_pack(message: types.Message):
    find = re.search(r"t\.me/add(stickers|emoji)/(\w+)", message.text)
    if not find:
        await message.reply("🤬 Невалидная ссылка")
        return
    set_name = find[2]
    emoji_or_stickers = find[1]
    full_link = f"http://t.me/add{emoji_or_stickers}/{set_name}"
    # Получаем информацию о стикерпаке
    cursor.execute("DELETE FROM stickerlinks WHERE link_url=?", (full_link,))
    await message.reply(f"Ссылка {full_link} удалена из базы данных")




def create_pagination_keyboard(current_page=1, links_per_page=5):
    cursor.execute("SELECT link_url, link_name FROM stickerlinks LIMIT ? OFFSET ?", (links_per_page, (current_page - 1) * links_per_page))
    stickers = cursor.fetchall()
    builder = InlineKeyboardBuilder()
    btn_counter = 0
    for sticker_id in range(len(stickers)):
        sticker = stickers[sticker_id]
        sticker_link = sticker[0]
        sticker_name = sticker[1]
        if btn_counter == 2:
            btn_counter = 0
        if btn_counter == 0:
            builder.row(types.InlineKeyboardButton(text=sticker_name, url=sticker_link), width=2)
        else:
            builder.add(types.InlineKeyboardButton(text=sticker_name, url=sticker_link))
        btn_counter += 1
    next_button_callback = f'my_stickers_page{current_page+1}'
    back_button_callback = f'my_stickers_page{current_page-1}'
    if len(stickers) < links_per_page:
        next_button_callback = 'do_nothing'
    if current_page == 1:
        back_button_callback = 'do_nothing'
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=back_button_callback), types.InlineKeyboardButton(text="Вперёд ➡️", callback_data=next_button_callback))
    return builder.as_markup()


@router.message(ChatTypeFilter(chat_type=["private"]) and MessageTextFilter(message_text="😨 Каталог стикеров❓"), F.text)
async def all_my_stickers(message: types.message):
    kb = create_pagination_keyboard()
    await message.answer("Все мои стикеры:", reply_markup=kb)

@dp.callback_query(F.data.startswith("my_stickers_page"))
async def stickers_pagination(callback: types.CallbackQuery):
    res = re.search(r"-?\d+", callback.data)
    if res:
        res = res[0]
    else:
        return
    kb = create_pagination_keyboard(int(res))
    await callback.message.answer("Все мои стикеры:", reply_markup=kb)



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
