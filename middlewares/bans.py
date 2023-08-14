from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, types
from aiogram.types import TelegramObject, Update, Message, CallbackQuery

ban_id = [1922763311]


class BansMiddlewareI(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if data['event_from_user'].id in ban_id:
            return await handler(event, data)


class BansMiddleware(BaseMiddleware):
    global ban_id

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        print(data['event_from_user'].id)
        if data['event_from_user'].id in ban_id:
            if data['event_from_user'].language_code == 'ru':
                await event.answer(
                    'Вы заблокированы.',
                    show_alert=True
                )
            else:
                await event.answer(
                    'You are blocked.',
                    show_alert=True
                )
        else:
            return await handler(event, data)
        return
