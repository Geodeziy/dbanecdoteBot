![https://img.shields.io/badge/Python-3.9.6-brightgreen](https://img.shields.io/badge/Python-3.9.6-brightgreen)

# dbanectodeBot
Телеграм-бот, написанный на Python с помощью библиотеки aiogram.

  `main.py` - основной файл бота, в нём происходят запуск и работа команд бота.
  
  `translate.py` - запасная функция перевода сообщений на язык пользователся, установленный в Telegram.
  
  `joke_bans.py` - классы таблиц для sqlalchemy.
  
  `joke_check.py` - функция первичной модерации добавляемых шуток.
  
  `about_s.py`- функции составления информации о системе, на которой запущен бот, и ёё печати.
  
  `updatinglists.py` - функция для обновления списка заблокированных пользователей.
  
  `settings.py` - файл с ключами API:
```python
BOT_TOKEN = "BOT_TOKEN"  # токен бота
UNSPLASH_TOKEN = "UNSPLASH_TOKEN"  # ключ API для получения картинок
RapidAPI_Key = "RapidAPI_Key"  # ключ API для доступа к переводчику Microsoft
ID = 1234567890  # id пользователя Telegram, для доступа к запуску функции /restart
```
   
   В папке `filters` хранится файл `private_filter.py`, который разрешает использование команды /start только в личных сообщениях.    
   В папке `files` хранятся `ban_roots.json` - файл с запрещёнными корнями, `ban_words.json` - файл с запрещёнными словами и файл `ban_user.pkl`, который создаёт функция `updatinglists.py`
