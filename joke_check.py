import json
from transliterate import translit
from googletrans import Translator
from pymorphy2 import MorphAnalyzer
from re import sub, search
import asyncio

morph = MorphAnalyzer()
translator = Translator()
with open('files/ban_words.json', encoding='UTF-8') as f:
    ban_words = [d['word'] for d in json.load(f)]

with open('files/ban_roots.json', encoding='UTF-8') as f:
    ban_roots = [val for sublist in json.load(f).values() for val in sublist]


def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__


def remove_duplicate_letters(word):
    return ''.join(letter.lower() for i, letter in enumerate(str(word)) if i == 0 or letter != str(word)[i - 1])


async def joke_check(joke):
    try:
        joke_words = [remove_duplicate_letters(word) for word in sub(r'[^A-Za-z0-9А-Яа-я]', ' ', joke).split()]
        for word in joke_words:
            if word == 'спам':
                continue
            translit_word = translit(word, 'ru')
            if any(elem in ban_words for elem in [word, translit_word] + list(translit_word.replace('ё', 'е'))):
                return True
            if not search('[а-яА-Я]', word):
                if any(elem in ban_words for elem in [translator.translate(word, 'ru').text] +
                                                     morph.normal_forms(translator.translate(word, 'ru').text)):
                    return True

    except Exception as e:
        print(get_full_class_name(e), e)


# async def main():
#     tasks = [
#         asyncio.create_task(joke_check(''))
#     ]
#     c = await asyncio.gather(*tasks)
#     print(c)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
