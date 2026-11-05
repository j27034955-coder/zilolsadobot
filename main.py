import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import threading
from flask import Flask

TOKEN = '9106888365:AAFZCBl_A5472y76m-Of2KIAV4MeCXL8WwA'
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@server.route('/')
def index():
    return "Zilolsado Music Bot is active!"

def run_bot():
    bot.infinity_polling(skip_pending=True)

threading.Thread(target=run_bot).start()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Zilolsado tezkor musiqa boti serverda ishga tushdi 🚀 Qo'shiq nomini yuboring:")

@bot.message_handler(func=lambda message: True)
def search_music(message):
    query = message.text
    msg = bot.reply_to(message, "🔍 Tezkor qidirilmoqda...")
    threading.Thread(target=process_search, args=(message, query, msg)).start()

def process_search(message, query, msg):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch3:{query}", download=False)['entries']

        if not results:
            bot.edit_message_text("Hech narsa topilmadi 😕", chat_id=message.chat.id, message_id=msg.message_id)
            return

        markup = InlineKeyboardMarkup()
        for video in results:
            title = video.get('title', 'Noma\'lum')[:30]
            video_id = video.get('id')
            markup.add(InlineKeyboardButton(text=f"🎵 {title}", callback_data=f"dl_{video_id}"))

        bot.edit_message_text("Topilgan musiqalar. Keraklisini tanlang:", 
                              chat_id=message.chat.id, 
                              message_id=msg.message_id, 
                              reply_markup=markup)
    except Exception as e:
        bot.edit_message_text("Qidirishda xatolik yuz berdi.", chat_id=message.chat.id, message_id=msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def download_music(call):
