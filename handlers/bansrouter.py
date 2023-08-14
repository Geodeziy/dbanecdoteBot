from aiogram import Router, F
from aiogram.filters import MagicData
from aiogram.types import Message, CallbackQuery

from middlewares.bans import BansMiddlewareI

router = Router()
router.message.filter(F.chat.type == "private")
router.message.middleware(BansMiddlewareI())


@router.message(F.text)
async def bans_f(message: Message):
    if message.from_user.language_code == 'ru':
        await message.answer('Вы заблокированы.')
    else:
        await message.answer('You are blocked.')