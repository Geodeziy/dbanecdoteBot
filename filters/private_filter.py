from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, ChatTypeFilter

from main import dp


@dp.message_handler(CommandStart(), ChatTypeFilter(chat_type=types.ChatType.PRIVATE))
async def bot_start(message: types.Message):
    message_text = 'Я бот-шутник, напишите /joke чтобы я отправил шутку. Напишите /add_joke <i>ШУТКА</i>,' \
                   ' чтобы я добавил шутку в базу данных. Все добавленные шутки проходят модерацию.'

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="In English", callback_data="translate_start"))
    await message.reply(message_text, parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
