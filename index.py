import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
TOKEN = '8434658302:AAFTeNg0PDQIHWnNX2cYtk0yTk0UBWGAxT8'
ADMIN_ID =`8190715241'
USER_FILE = "users.txt"

bot = telebot.TeleBot(TOKEN)

# --- WEB SERVER (RENDER KE LIYE) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running! 🚀"

def run():
    # Render environment se PORT leta hai, default 8080
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
    save_user(user_id)

    welcome_text = f"Hello {first_name}! 👋\n\nNiche diye gaye buttons par click karke mere social media channels ko join karein:"

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_telegram = types.InlineKeyboardButton("📢 Join Telegram Channel", url="https://t.me/A1Android")
    btn_youtube = types.InlineKeyboardButton("📺 Subscribe YouTube", url="https://www.youtube.com/@Aiapplication1")
    btn_facebook = types.InlineKeyboardButton("👍 Follow Facebook", url="https://www.facebook.com/profile.php?id=61555961901782")
    
    markup.add(btn_telegram, btn_youtube, btn_facebook)
    
    if user_id == ADMIN_ID:
        bot.send_message(user_id, "Welcome Boss! Aap Admin hain. \n/stats - Users check karein\n/broadcast [msg] - Message bhejein")

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id == ADMIN_ID:
        users = get_users()
        bot.reply_to(message, f"📊 Total Users: {len(users)}")

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.chat.id == ADMIN_ID:
        msg_text = message.text.split(' ', 1)
        if len(msg_text) > 1:
            text_to_send = msg_text[1]
            users = get_users()
            sent_count = 0
            for user in users:
                try:
                    bot.send_message(int(user), text_to_send)
                    sent_count += 1
                except:
                    pass
            bot.reply_to(message, f"✅ Message sent to {sent_count} users.")
        else:
            bot.reply_to(message, "Likhein: /broadcast Hello")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    keep_alive()  # Server start karega
    bot.infinity_polling() # Bot start karega
