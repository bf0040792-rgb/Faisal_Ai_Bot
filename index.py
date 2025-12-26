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

# --- LINKS ---
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

# --- 1. ADMIN TO CHANNEL (Auto Post) ---
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

# --- 2. SUPER SMART REPLY (Anonymous + Group + Private) ---
# Ye handler har tarah ke message ko check karega
@bot.message_handler(func=lambda m: True)
def auto_reply(message):
    try:
        # Text nikalna (Chahe caption ho ya normal text)
        text = ""
        if message.text:
            text = message.text.lower()
        elif message.caption:
            text = message.caption.lower()
            
        if not text:
            return

        user_id = message.chat.id
        
        # Sirf Private me user save karein (Group me crash na ho)
        if message.chat.type == 'private':
            save_user(user_id)

        # --- LOGIC START (Order Change kiya hai taaki galti na ho) ---

        # 1. FACEBOOK (Priority 1)
        if "facebook" in text:
            bot.reply_to(message, f"👍 Facebook Page:\n{LINK_FACEBOOK}")
            return

        # 2. YOUTUBE (Priority 2)
        if "youtube" in text:
            bot.reply_to(message, f"📺 YouTube Channel:\n{LINK_YOUTUBE}")
            return

        # 3. HOPWEB (Priority 3)
        if "hopweb" in text:
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("⬇️ Download HopWeb", url="https://play.google.com/store/apps/details?id=com.hopweb")
            markup.add(btn)
            bot.reply_to(message, "HopWeb App yahan se download karein:", reply_markup=markup)
            return

        # 4. TELEGRAM/CHANNEL (Priority 4)
        if "telegram" in text or "channel" in text:
            bot.reply_to(message, f"📢 Telegram Channel:\n{LINK_TELEGRAM}")
            return

        # 5. COMMANDS
        if text == "/start":
            bot.reply_to(message, "Hello! Main Active hoon. \nLikhein: 'Facebook', 'YouTube' ya 'Hopweb'")

        if text == "/stats" and user_id == ADMIN_ID:
            users = get_users()
            bot.reply_to(message, f"📊 Total Bot Users: {len(users)}")

    except Exception as e:
        print(f"Error: {e}")

# --- START BOT ---
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(skip_pending=True)        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

    # 7. ADMIN COMMANDS
    if user_id == ADMIN_ID:
        if text == "/stats":
            users = get_users()
            bot.reply_to(message, f"📊 Total Bot Users: {len(users)}")
        elif text.startswith("/broadcast"):
            msg_parts = message.text.split(' ', 1)
            if len(msg_parts) > 1:
                text_to_send = msg_parts[1]
                users = get_users()
                count = 0
                for user in users:
                    try:
                        bot.send_message(int(user), text_to_send)
                        count += 1
                    except:
                        pass
                bot.reply_to(message, f"✅ Broadcast sent to {count} users.")

# --- START BOT ---
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
