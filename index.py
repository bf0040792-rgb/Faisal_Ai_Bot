import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread
import time

# --- CONFIGURATION ---
TOKEN = '8434658302:AAFTeNg0PDQIHWnNX2cYtk0yTk0UBWGAxT8'
ADMIN_ID = 8190715241
CHANNEL_USERNAME = "@A1Android"
USER_FILE = "users.txt"

# --- LINKS ---
LINK_YOUTUBE = "https://www.youtube.com/@Aiapplication1"
LINK_TELEGRAM = "https://t.me/A1Android"
LINK_FACEBOOK = "https://www.facebook.com/profile.php?id=61555961901782"

bot = telebot.TeleBot(TOKEN)

# --- WEB SERVER (Render Keep Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running! 🚀"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 1. ADMIN TO CHANNEL (Forwarding) ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio'], func=lambda m: m.chat.id == ADMIN_ID and m.chat.type == 'private')
def forward_to_channel(message):
    if message.text and message.text.startswith('/'):
        pass
    else:
        try:
            bot.copy_message(chat_id=CHANNEL_USERNAME, from_chat_id=message.chat.id, message_id=message.message_id)
            bot.reply_to(message, f"✅ Post Sent to {CHANNEL_USERNAME}")
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {e}")

# --- 2. UNIVERSAL AUTO REPLY (User + Anonymous Admin) ---
# YAHAN BADLAV HAI: @bot.channel_post_handler add kiya hai
@bot.message_handler(func=lambda m: True)
@bot.channel_post_handler(func=lambda m: True) 
def auto_reply(message):
    try:
        # Text nikalo (Text ya Caption)
        text = ""
        if message.text:
            text = message.text.lower()
        elif message.caption:
            text = message.caption.lower()
            
        if not text:
            return

        # Agar command hai to ignore karo (taki loop na bane)
        if text.startswith('/'):
            if text == "/start":
                # Start command ka reply
                bot.reply_to(message, "Hello! Main Active hoon. \nTry: 'Facebook', 'YouTube' or 'Hopweb'")
            return

        # --- KEYWORD CHECKING ---

        # 1. FACEBOOK
        if "facebook" in text:
            bot.reply_to(message, f"👍 Facebook Page Link:\n{LINK_FACEBOOK}")
            return

        # 2. YOUTUBE
        if "youtube" in text:
            bot.reply_to(message, f"📺 YouTube Channel Link:\n{LINK_YOUTUBE}")
            return

        # 3. HOPWEB
        if "hopweb" in text:
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("⬇️ Download HopWeb", url="https://play.google.com/store/apps/details?id=com.hopweb")
            markup.add(btn)
            bot.reply_to(message, "HopWeb App yahan se download karein:", reply_markup=markup)
            return

        # 4. TELEGRAM/CHANNEL
        if "telegram" in text or "channel" in text:
            bot.reply_to(message, f"📢 Telegram Channel:\n{LINK_TELEGRAM}")
            return

    except Exception as e:
        print(f"Error: {e}")

# --- START BOT ---
if __name__ == "__main__":
    keep_alive()
    # Skip pending messages to avoid crash on start
    bot.infinity_polling(skip_pending=True)
