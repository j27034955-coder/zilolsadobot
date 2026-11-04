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
    video_id = call.data.split('_')[1]
    bot.answer_callback_query(call.id, "Yuklab olinmoqda...")
    threading.Thread(target=process_download, args=(call.message, video_id)).start()

def process_download(message, video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    sent_msg = bot.send_message(message.chat.id, "📥 Musiqa tayyorlanmoqda, kuting...")

    file_path = f"{video_id}.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': video_id,  # <-- TO'G'RILANDI: kengaytmasiz yozildi, ffmpeg o'zi .mp3 qiladi
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(file_path):
            raise Exception("Fayl topilmadi")

        with open(file_path, 'rb') as audio:
            bot.send_audio(message.chat.id, audio)

        if os.path.exists(file_path):
            os.remove(file_path)

        bot.delete_message(message.chat.id, sent_msg.message_id)
    except Exception as e:
        bot.send_message(message.chat.id, "Afsuski, qo'shiqni yuklab bo'lmadi.")

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
