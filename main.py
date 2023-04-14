from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import sqlalchemy
import os
from random import randint, choice
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
from joke_bans import Joke, Bans
import asyncio
import pickle
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions
import aiosqlite
from sqlalchemy.ext.asyncio import create_async_engine
import aiofiles
import aiohttp
from aiogram.types.input_file import InputFile
from settings import BOT_TOKEN, ID

TOKEN = BOT_TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

engine = sqlalchemy.create_engine('sqlite:///j.db')
Base = sqlalchemy.orm.declarative_base()


def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__


# ban_id = []

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


@dp.message_handler(user_id=ban_id)  # Функция блокировки пользователя
async def bans(message: types.Message):
    """Нужно перезапускать программу для обновления заблокированных пользователей"""
    from translate import translation
    if message.from_user.locale == 'ru':
        await message.reply('Вы заблокированы.')
    else:  # Перевод сообщения о блокировке на язык пользователя, установленный в Telegram.
        try:
            from googletrans import Translator
            translator = Translator()
            t = translator.translate('You are blocked.', dest=f'{message.from_user.locale}')
            await message.reply(t.text)
        except Exception as e:  # Запасной переводчик
            print(get_full_class_name(e), e)
            await message.reply(translation('You are blocked.', message.from_user.locale))


@dp.message_handler(commands=['help'])
async def help_(message: types.Message):
    if message.from_user.locale == 'ru':
        message_text = 'Напишите /joke, чтобы я отправил шутку.\nНапишите /add_joke <i>ШУТКА</i>,' \
                       ' чтобы я добавил шутку в базу данных. Все добавленные шутки проходят модерацию.'
        await message.reply(message_text, parse_mode=types.ParseMode.HTML)
    else:
        message_text = 'Type /joke so I can send a joke.\nType /add_joke <i>JOKE</i>' \
                       ' to have me add the joke to the database. All added jokes are moderated.'
        await message.reply(message_text, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['joke'])
async def joke(message: types.Message):
    from sqlalchemy.orm import sessionmaker
    from translate import translation
    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.query(Joke).filter(Joke.allowed == 'True').all()
    if not result:
        await message.reply('К сожалению, нет доступных шуток.')
        return
    m = result[randint(0, len(result) - 1)]
    if message.from_user.locale == 'ru':
        await message.reply(m.joke)
    else:  # Перевод шутки на язык пользователя, установленный в Telegram.
        try:
            from googletrans import Translator
            translator = Translator()
            t = translator.translate(m.joke, dest=f'{message.from_user.locale}')
            await message.reply(t.text)
        except Exception as e:  # Запасной переводчик
            print(get_full_class_name(e), e)
            await message.reply(translation(m.joke, message.from_user.locale))


@dp.message_handler(commands=['add_joke'])
async def add_joke(message: types.Message):
    from sqlalchemy.orm import sessionmaker
    from joke_check import joke_check
    Session = sessionmaker(bind=engine)
    session = Session()
    s = message.get_args()
    if not s:
        await message.reply('Шутка не передана.')
    else:
        if await joke_check(s):
            await message.reply('В вашей шутке содержится обсценная лексика.')
        else:
            joke = Joke()
            joke.joke = s
            joke.user_id = message.from_user.id
            joke.allowed = 'False'  # Одобрение происходит вручную
            session.add(joke)
            session.commit()
            await message.reply('Шутка добавлена в базу данных, и будет промодерирована.')


async def download_image(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()


@dp.message_handler(commands=['capybara'])
async def send_random_kapibara(message: types.Message):
    import requests
    from settings import UNSPLASH_TOKEN
    try:
        access_key = UNSPLASH_TOKEN
        query = "capybara"
        orientation = "landscape"
        # URL для запроса
        url = f"https://api.unsplash.com/search/photos?query={query}&orientation={orientation}"
        # Заголовки для авторизации запроса
        headers = {
            "Authorization": f"Client-ID {access_key}"
        }
        # Отправка запроса
        response = requests.get(url, headers=headers)
        # Получение результатов
        results = json.loads(response.text)["results"]
        # Получение URL первой фотографии
        photo_url = results[randint(0, len(results) - 1)]["urls"]["regular"]
        await bot.send_photo(chat_id=message.from_user.id, photo=photo_url, reply_to_message_id=message.message_id)
    except Exception as e:
        print(e)
        photo = open('capybara.png', 'rb')
        await bot.send_photo(message.from_user.id, photo=photo, caption='Изображения не нашлись,'
                                                                        ' но есть такая картинка капибары в космосе.',
                             reply_to_message_id=message.message_id)


@dp.message_handler(commands=['comp_info'])
async def comp_info(message: types.Message):
    from about_s import creating_file, await_info, correct_size
    dict_info = await creating_file()
    await message.reply((await_info(dict_info) + f'[+] Размер базы данных\n\
                          \t- Размер: {correct_size(os.path.getsize(os.path.join(".", "j.db")))}\n'))


@dp.message_handler(commands=['restart'], user_id=ID)
async def restart(message: types.Message):
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


# async def main():
#     while True:
#         await read_bans()
#         print(ban_id)
#         await asyncio.sleep(10)
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.create_task(main())
#     executor.start_polling(dp)

if __name__ == '__main__':
    from filters import dp

    executor.start_polling(dp, skip_updates=True)
