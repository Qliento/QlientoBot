import logging
import asyncio

from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions


from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json


from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from bot.settings import (BOT_TOKEN, HEROKU_APP_NAME,
                          WEBHOOK_URL, WEBHOOK_PATH,
                          WEBAPP_HOST, WEBAPP_PORT)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


button_hi = KeyboardButton('/help')

greet_kb = ReplyKeyboardMarkup()
greet_kb.add(button_hi)


greet_kb1 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_hi)

greet_kb2 = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_hi)

button1 = KeyboardButton('/исследования')
button2 = KeyboardButton('/новость')
button3 = KeyboardButton('/блог')

markup3 = ReplyKeyboardMarkup().add(
    button1).add(button2).add(button3)

greet_kb1= ReplyKeyboardMarkup(resize_keyboard=True).row(
    button1, button2, button3
).add(button_hi)

markup5 = ReplyKeyboardMarkup().row(
    button1, button2, button3
).add(KeyboardButton('Команды'))

button4 = KeyboardButton('4️⃣')
button5 = KeyboardButton('5️⃣')
button6 = KeyboardButton('6️⃣')
markup5.row(button4, button5)
markup5.insert(button6)

markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Отправить свой контакт ☎️', request_contact=True)
).add(
    KeyboardButton('Отправить свою локацию 🗺️', request_location=True)
)

markup_big = ReplyKeyboardMarkup()

markup_big.add(
    button1, button2, button3, button4, button5, button6
)
markup_big.row(
    button1, button2, button3, button4, button5, button6
)

markup_big.row(button4, button2)
markup_big.add(button3, button2)
markup_big.insert(button1)
markup_big.insert(button6)
markup_big.insert(KeyboardButton('9️⃣'))

import requests
import json



inline_kb_start = InlineKeyboardMarkup(row_width=2)
inline_btn_1 = InlineKeyboardButton('/research')
inline_btn_2 = InlineKeyboardButton('/news')
inline_btn_3 = InlineKeyboardButton('/post')

inline_kb_start.add(inline_btn_1, inline_btn_2, inline_btn_3)

inline_kb_full = InlineKeyboardMarkup(row_width=2)
inline_btn_3 = InlineKeyboardButton('кнопка 3', callback_data='btn3')
inline_btn_4 = InlineKeyboardButton('кнопка 4', callback_data='btn4')
inline_btn_5 = InlineKeyboardButton('кнопка 5', callback_data='btn5')


r = requests.get('https://back.qliento.com/research/')
data = json.loads(r.text)
inline_kb = []
for research in data:
	msg = research['name']
	url = 'https://qliento.com/market-research-detail/' + str(research['id'])
	inline = InlineKeyboardButton(research['name'],url=url)
	inline_kb_full.add(inline)

async def on_startup(dp):
    logging.warning(
        'Starting connection. ')
    await bot.set_webhook(WEBHOOK_URL,drop_pending_updates=True)

@dp.message_handler(commands=['новость'])
async def process_help_command(message: types.Message):
    r = requests.get('https://back.qliento.com/news/')
    data = json.loads(r.text)
    msg = data[0]
    picture = msg['image']
    msgg = text(bold(msg['name'])) + '\n' + text(italic(msg['description']))
    await message.reply(msgg, parse_mode=ParseMode.MARKDOWN)
    await bot.send_photo(message.chat.id, types.InputFile.from_url(picture))


@dp.message_handler(commands=['блог'])
async def process_help_command(message: types.Message):
    r = requests.get('https://back.qliento.com/blog/')
    data = json.loads(r.text)
    msg = data[0]
    msgg = text(bold(msg['header'])) + '\n' + text(italic(msg['description']))
    await message.reply(msgg, parse_mode=ParseMode.MARKDOWN)



@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Здравствуйте! Чтобы найти исследование, отправьте его название", reply_markup=greet_kb1)



@dp.message_handler(commands=['исследования'])
async def process_command_2(message: types.Message):
    await message.reply("Отправляю все возможные исследования",
                        reply_markup=inline_kb_full)

help_message = text(
    "/исследования - ссылки на все исследования",
    "/блог - самая свежая аналитика",
    "/новость - самая свежая новость",
    "Чтобы найти исследование, отправьте его название",
    sep="\n"
)

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(help_message)

@dp.message_handler()
async def echo(message: types.Message):
    url = 'https://back.qliento.com/researches/?name__icontains=' + message.text
    r = requests.get(url)
    data = json.loads(r.text)

    if len(data) != 0:
        inline_kb = []
        inline_kb_full = InlineKeyboardMarkup(row_width=2)
        for research in data:
            msg = research['name']
            url = 'https://qliento.com/market-research-detail/' + str(research['id'])
            inline = InlineKeyboardButton(research['name'],url=url)
            inline_kb_full.add(inline)
        await message.answer('Вот, что мне удалось найти: ', reply_markup=inline_kb_full)
    else:
        await message.answer('К сожалению, ничего не нашлось. Закажите ваше персональное исследование у нас на сайте:\nhttps://www.qliento.com/order-research')



async def on_shutdown(dp):
    logging.warning('Bye! Shutting down webhook connection')


def main():
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
