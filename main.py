from aiogram import Bot, Dispatcher, types, html, F, Router
from aiogram.filters import Command, CommandObject
import sqlalchemy
import os
from random import randint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
from joke_bans import Joke, Bans
import asyncio
import pickle
from aiogram.utils.markdown import text, bold, italic, code, pre
# from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
import aiofiles
import aiohttp
from aiogram.types.input_file import InputFile
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder
from contextlib import suppress
import psutil

from settings import BOT_TOKEN, ID
import logging
from handlers import start, bansrouter
from middlewares.bans import BansMiddleware

TOKEN = BOT_TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

engine = sqlalchemy.create_engine('sqlite:///j.db')
Base = sqlalchemy.orm.declarative_base()


def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__


Session = sessionmaker(bind=engine)
session = Session()
ban_id = session.query(Bans).all()
session.commit()
ban_id = [x.user_id for x in ban_id]

"""Функция должна была считывать файл bans_user.pkl каждые 30 секунд
 и обновлять список ban_id"""


async def ban_ids_updater():
    global ban_id
    while True:
        async with aiofiles.open('files/ban_user.pkl', 'rb') as f:
            data = pickle.load(f)
        ban_id = data
        print(ban_id)
        await asyncio.sleep(30)


@dp.callback_query(F.text("translate_start"))
async def translate_start(call: types.CallbackQuery):
    """Функция, которая изменяет сообщение, отправляемое командой start."""
    with suppress(TelegramBadRequest):
        message_text = "I'm a joke bot, type /joke so I can send a joke. Type /add_joke <i>JOKE</i>" \
                       " to have me add the joke to the database. All added jokes are moderated."
        await call.message.edit_text(message_text, parse_mode="HTML")
        await call.answer()


# @dp.message(user_id=ban_id)  # Функция блокировки пользователя
# async def bans(message: types.Message):
#     """Нужно перезапускать программу для обновления заблокированных пользователей."""
#     from translate import translation
#     if message.from_user.language_code == 'ru':
#         await message.reply('Вы заблокированы.')
#     else:  # Перевод сообщения о блокировке на язык пользователя, установленный в Telegram.
#         try:
#             from googletrans import Translator
#             translator = Translator()
#             t = translator.translate('You are blocked.', dest=f'{message.from_user.language_code}')
#             await message.reply(t.text)
#         except Exception as e:  # Запасной переводчик
#             print(get_full_class_name(e), e)
#             await message.reply(translation('You are blocked.', message.from_user.language_code))


@dp.message(Command('help'))
async def help_(message: types.Message):
    """Команда для вывода справочной информации."""
    message_text = 'Напишите /joke, чтобы я отправил шутку.\nНапишите /add_joke <i>ШУТКА</i>,' \
                       ' чтобы я добавил шутку в базу данных. Все добавленные шутки проходят модерацию.'

    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text="In English", callback_data="translate_help"))
    await message.reply(message_text, parse_mode="HTML", reply_markup=keyboard.as_markup())


@dp.callback_query(F.text("translate_help"))
async def translate_help(call: types.CallbackQuery):
    """Функция, которая изменяет сообщение, отправляемое командой help."""
    with suppress(TelegramBadRequest):
        message_text = 'Type /joke so I can send a joke.\nType /add_joke <i>JOKE</i>' \
                       ' to have me add the joke to the database. All added jokes are moderated.'
        await call.message.edit_text(message_text, parse_mode="HTML")
        await call.answer()


@dp.message(Command('joke'))
async def joke(message: types.Message):
    """Функция отправляет шутку из базы данных."""
    from sqlalchemy.orm import sessionmaker
    from translate import translation
    global m
    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.query(Joke).filter(Joke.allowed == 'True').all()
    if not result:
        await message.reply('К сожалению, нет доступных шуток.')
        return
    m = result[randint(0, len(result) - 1)]
    if message.from_user.language_code == 'ru':
        await message.reply(m.joke)
    else:  # Перевод шутки на язык пользователя, установленный в Telegram.
        if m.english_joke:  # Проверка на наличие английского перевода шутки
            joke_to_translate = m.english_joke
        else:
            joke_to_translate = m.joke
        try:
            from googletrans import Translator
            translator = Translator()
            t = translator.translate(joke_to_translate, dest=f'{message.from_user.language_code}')
            keyboard = InlineKeyboardBuilder()
            keyboard.add(types.InlineKeyboardButton(text="Original joke", callback_data=f"original_joke_{m.id}"))
            await message.reply(t.text, reply_markup=keyboard.as_markup())
        except Exception as e:  # Запасной переводчик
            print(get_full_class_name(e), e)
            keyboard = InlineKeyboardBuilder()
            keyboard.add(types.InlineKeyboardButton(text="Original joke", callback_data=f"original_joke_{m.id}"))
            translated_text = await translation(joke_to_translate, message.from_user.language_code)
            await message.reply(translated_text, reply_markup=keyboard.as_markup())


# @dp.callback_query(Text(str(lambda c: c.data.startswith('original_joke_'))))
@dp.callback_query(F.text(startswith='original_joke_'))
async def original_joke(callback: types.CallbackQuery):
    """Функция меняет переведённую шутку на записанную в базу данных."""
    with suppress(TelegramBadRequest):
        joke_id = callback.data.split('_')[-1]
        Session = sessionmaker(bind=engine)
        session = Session()
        joke = session.query(Joke).filter(Joke.id == joke_id).one()
        message_text = joke.joke
        await callback.message.edit_text(message_text, parse_mode="HTML")
        await callback.answer()


@dp.message(Command('add_joke'))
async def add_joke(message: types.Message, command: CommandObject):
    """Функция добавляет шутку в базу данных."""
    from sqlalchemy.orm import sessionmaker
    from joke_check import joke_check
    Session = sessionmaker(bind=engine)
    session = Session()
    s = command.args
    if not s:
        if message.from_user.language_code == 'ru':
            await message.reply('Шутка не передана.')
        else:
            await message.reply('The joke was not sent.')
    else:
        if await joke_check(s):
            if message.from_user.language_code == 'ru':
                await message.reply('В вашей шутке содержится обсценная лексика.')
            else:
                await message.reply('Your joke contains obscene language.')
        else:
            joke = Joke()
            joke.joke = s
            joke.user_id = message.from_user.id
            joke.allowed = 'False'  # Одобрение происходит вручную
            session.add(joke)
            session.commit()
            if message.from_user.language_code == 'ru':
                await message.reply('Шутка добавлена в базу данных, и будет промодерирована.')
            else:
                await message.reply('The joke has been added to the database and will be moderated.')


@dp.message(Command('capybara'))
async def send_random_capybara(message: types.Message):
    """Вывод изображения капибары."""
    import requests
    from settings import UNSPLASH_TOKEN
    try:
        access_key = UNSPLASH_TOKEN
        query = "capybara"
        orientation = "landscape"
        # URL для запроса
        url = f"https://api.unsplash.com/search/photos?query={query}&orientation={orientation}"
        headers = {
            "Authorization": f"Client-ID {access_key}"
        }
        # Отправка запроса
        response = requests.get(url, headers=headers)
        # Получение результатов
        results = json.loads(response.text)["results"]
        # Получение URL случайной фотографии
        photo = results[randint(0, len(results) - 1)]
        photo_url = photo["urls"]["regular"]
        photographer_name = photo["user"]["name"]
        # Отправка сообщения с фотографией и информацией об авторе
        await bot.send_photo(chat_id=message.from_user.id, photo=photo_url,
                             caption=f'Photo by {photographer_name} on <a href="https://unsplash.com/">Unsplash</a>.',
                             reply_to_message_id=message.message_id, parse_mode="HTML")

    except Exception as e:  # Если произошла ошибка, то выводим заранее заготовленное изображение
        print(e)
        photo = FSInputFile('capybara.png', 'rb')
        if message.from_user.language_code == 'ru':
            c = 'Изображения не нашлись, но есть такая картинка капибары в космосе.'
        else:
            c = 'Images were not found, but there is such a picture of a capybara in space.'
        await bot.send_photo(message.from_user.id, photo=photo, caption=c, reply_to_message_id=message.message_id)


@dp.message(Command('comp_info'))
async def comp_info(message: types.Message):
    """Вывод информации о системе, на которой запущена программа."""
    from about_s import creating_file, await_info, correct_size
    dict_info = await creating_file()
    if os.name == 'posix':
        temperature = psutil.sensors_temperatures()
        await message.reply((await_info(dict_info) + f'[+] Размер базы данных\n\
                                  \t- Размер: {correct_size(os.path.getsize(os.path.join(".", "j.db")))}\n' +
                             f'[+] Температура процессора\n\
                             \t- Температура: {temperature["cpu_thermal"][0].current}°C'))
    else:
        await message.reply((await_info(dict_info) + f'[+] Размер базы данных\n\
                          \t- Размер: {correct_size(os.path.getsize(os.path.join(".", "j.db")))}\n'))


@dp.message(Command('restart'))
async def restart(message: types.Message, user_id=ID):
    """Нужно запускать программу с помощью командной строки или терминала"""
    import sys
    import subprocess
    await message.reply('Перезагрузка...')
    script_path = os.path.abspath(sys.argv[0])
    if os.name == 'posix':
        subprocess.Popen(['python3', script_path])
    else:
        subprocess.Popen(['python', script_path])
    sys.exit()


async def main():
    dp.include_router(start.router)
    dp.include_router(bansrouter.router)
    dp.callback_query.outer_middleware(BansMiddleware())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
