from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, ChatTypeFilter

from main import dp


@dp.message_handler(CommandStart(), ChatTypeFilter(chat_type=types.ChatType.PRIVATE))
async def bot_start(message: types.Message):
    if message.from_user.locale == 'ru':
        message_text = 'Я бот-шутник, напишите /joke чтобы я отправил шутку. Напишите /add_joke <i>ШУТКА</i>,'\
                            ' чтобы я добавил шутку в базу данных. Все добавленные шутки проходят модерацию.'
        await message.reply(message_text, parse_mode=types.ParseMode.HTML)
    else:
        message_text = "I'm a joke bot, type /joke so I can send a joke. Type /add_joke <i>JOKE</i>"\
                            " to have me add the joke to the database. All added jokes are moderated."
        await message.reply(message_text, parse_mode=types.ParseMode.HTML)
