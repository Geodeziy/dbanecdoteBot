from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.chat_type import ChatTypeFilter

router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


@router.message(Command("start"))
async def cmd_dice_in_group(message: Message):
    message_text = 'Я бот-шутник, напишите /joke чтобы я отправил шутку. Напишите /add_joke <i>ШУТКА</i>,' \
                   ' чтобы я добавил шутку в базу данных. Все добавленные шутки проходят модерацию.'

    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text="In English", callback_data="translate_help"))
    await message.reply(message_text, parse_mode="HTML", reply_markup=keyboard.as_markup())

