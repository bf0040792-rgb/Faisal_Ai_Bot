import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- CONFIGURATION (Sahi details yahan hain) ---
TOKEN = '8434658302:AAFTeNg0PDQIHWnNX2cYtk0yTk0UBWGAxT8'

# Galti yahan thi, ab maine isse thik kar diya hai (No quotes needed for numbers)
ADMIN_ID = 8190715241 

USER_FILE = "users.txt"

# Bot Initialize
bot = telebot.TeleBot(TOKEN)

# --- RENDER WEB SERVER (Bot ko zinda rakhne ke liye) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running! 🚀 Status: Online"

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
            print(f"New user saved: {chat_id}")

def get_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r") as f:
        return f.read().splitlines()

# --- BOT COMMANDS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    first_name = message.from_user.first_name
    
    # Save User
    save_user(user_id)

    # Welcome Text
    welcome_text = f"Hello {first_name}! 👋\n\nNiche diye gaye buttons par click karke mere social media channels ko join karein:"

    # Buttons
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_telegram = types.InlineKeyboardButton("📢 Join Telegram Channel", url="https://t.me/A1Android")
    btn_youtube = types.InlineKeyboardButton("📺 Subscribe YouTube", url="https://www.youtube.com/@Aiapplication1")
    btn_facebook = types.InlineKeyboardButton("👍 Follow Facebook", url="https://www.facebook.com/profile.php?id=61555961901782")
    
    markup.add(btn_telegram, btn_youtube, btn_facebook)
    
    # Admin Notification
    if user_id == ADMIN_ID:
        bot.send_message(user_id, "✅ Welcome Admin! Bot sahi se kaam kar raha hai.\n\nCommands:\n/stats - Check Users\n/broadcast [Message] - Send Message to All")

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# Admin Command: Stats
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id == ADMIN_ID:
        users = get_users()
        bot.reply_to(message, f"📊 Total Users: {len(users)}")

# Admin Command: Broadcast
@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.chat.id == ADMIN_ID:
        msg_text = message.text.split(' ', 1)
        if len(msg_text) > 1:
            text_to_send = msg_text[1]
            users = get_users()
            sent_count = 0
            fail_count = 0
            
            status_msg = bot.reply_to(message, f"🚀 Broadcasting to {len(users)} users...")
            
            for user in users:
                try:
                    bot.send_message(int(user), text_to_send)
                    sent_count += 1
                except:
                    fail_count += 1
            
            bot.edit_message_text(f"✅ Broadcast Complete!\nSuccess: {sent_count}\nFailed: {fail_count}", chat_id=ADMIN_ID, message_id=status_msg.message_id)
        else:
            bot.reply_to(message, "❌ Message likhna bhul gaye.\nAise likhein: `/broadcast Hello Sab log`")

# --- START BOT ---
if __name__ == "__main__":
    keep_alive()  # Web server start
    bot.infinity_polling()  # Telegram bot start
