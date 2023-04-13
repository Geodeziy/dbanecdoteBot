import json
from transliterate import translit
from googletrans import Translator
from pymorphy2 import MorphAnalyzer
from re import sub, search

morph = MorphAnalyzer()
translator = Translator()
with open('files/ban_words.json') as f:
    ban_words = [d['word'] for d in json.load(f)]

with open('files/ban_roots.json') as f:
    ban_roots = json.load(f)


def simplify_word(word: str) -> str:
    last_letter = ''
    result = ''
    for letter in word:
        if letter != last_letter:
            last_letter = letter
            result += letter
    return result.lower()


async def joke_check(message: str) -> bool:
    msg_words = [simplify_word(word) for word in sub('[^A-Za-zА-Яа-яёЁ]+', ' ', message).split()]
    for word in msg_words:
        if word == 'спам':
            continue
        word_r = translit(word, 'ru')
        if word in ban_words or word_r in ban_words:
            return True
        for form in morph.normal_forms(word_r):
            if form in ban_words:
                return True
        word_re = word_r.replace('ё', 'е')
        if 'ё' in word_r:
            for form in morph.normal_forms(word_re):
                if form in ban_words:
                    return True
        for root in ban_roots:
            if root in word or root in word_re:
                return True
        try:
            if not search('[а-яА-Я]', word):
                word_t = translator.translate(word, 'ru').text
                if word_t in ban_words:
                    return True
                for form in morph.normal_forms(word_t):
                    if form in ban_words:
                        return True
                word_rt = word_r.replace('ё', 'е')
                if 'ё' in word_r:
                    for form in morph.normal_forms(word_rt):
                        if form in ban_words:
                            return True
                for root in ban_roots:
                    if root in word_t or root in word_rt:
                        return True
            else:
                word_t = word
        except Exception as e:
            print('translate_error', e.__traceback__)
            word_t = word
            print(morph.normal_forms(word_t), morph.normal_forms(word_r), word_t, word_r, word)
