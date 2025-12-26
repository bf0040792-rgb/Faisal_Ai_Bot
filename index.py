import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
TOKEN = '8434658302:AAFTeNg0PDQIHWnNX2cYtk0yTk0UBWGAxT8'
ADMIN_ID = 8190715241
CHANNEL_USERNAME = "@A1Android"
USER_FILE = "users.txt"

# --- HARDCODED LINKS (Bot inko yaad rakhta hai) ---
LINK_YOUTUBE = "https://www.youtube.com/@Aiapplication1"
LINK_TELEGRAM = "https://t.me/A1Android"
LINK_FACEBOOK = "https://www.facebook.com/profile.php?id=61555961901782"

bot = telebot.TeleBot(TOKEN)

# --- WEB SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running! 🚀"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- HELPER FUNCTIONS ---
def save_user(chat_id):
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            pass
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    if str(chat_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(str(chat_id) + "\n")

def get_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r") as f:
        return f.read().splitlines()

# --- 1. ADMIN POSTING SYSTEM ---
# Admin jab Bot ko private me bhejega, Bot channel pe forward karega
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio'], func=lambda m: m.chat.id == ADMIN_ID and m.chat.type == 'private')
def handle_admin_post(message):
    # Commands ko ignore karein
    if message.text and message.text.startswith('/'):
        return

    try:
        # Channel par bhejo
        bot.copy_message(chat_id=CHANNEL_USERNAME, from_chat_id=message.chat.id, message_id=message.message_id)
        bot.reply_to(message, f"✅ Post Sent to {CHANNEL_USERNAME}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# --- 2. GROUP AUTO REPLY (Discussion Group Support) ---
# Ye handler har tarah ke text message ko padhega (Replies included)
@bot.message_handler(func=lambda m: True, content_types=['text'])
def smart_reply(message):
    try:
        text = message.text.lower()
        
        # Logs me print karega ki bot ne message dekha ya nahi (Render Logs check kar sakte hain)
        print(f"Message received from {message.from_user.first_name}: {text}")

        # Agar Private chat hai to User save karo
        if message.chat.type == 'private':
            save_user(message.chat.id)

        # --- KEYWORD MATCHING ---
        
        # Agar koi FACEBOOK maange
        if "facebook" in text:
            bot.reply_to(message, f"👍 Facebook Link:\n{LINK_FACEBOOK}")
            return

        # Agar koi YOUTUBE maange
        if "youtube" in text:
            bot.reply_to(message, f"📺 YouTube Link:\n{LINK_YOUTUBE}")
            return

        # Agar koi HOPWEB maange
        if "hopweb" in text:
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("⬇️ Download HopWeb", url="https://play.google.com/store/apps/details?id=com.hopweb")
            markup.add(btn)
            bot.reply_to(message, "Ye lijiye HopWeb App 👇", reply_markup=markup)
            return

        # Agar koi TELEGRAM maange
        if "telegram" in text or "channel" in text:
            bot.reply_to(message, f"📢 Telegram Channel:\n{LINK_TELEGRAM}")
            return
            
        # Commands
        if text == "/start":
            bot.reply_to(message, "Hello! Main Active hoon.\nKeywords try karein: 'Facebook', 'Hopweb', 'YouTube'")
            
    except Exception as e:
        print(f"Error handling message: {e}")

# --- START BOT ---
if __name__ == "__main__":
    keep_alive()
    # 'none_stop=True' zaroori hai taaki bot ruke nahi
    bot.infinity_polling(skip_pending=True)
