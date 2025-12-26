import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
TOKEN = '8434658302:AAFTeNg0PDQIHWnNX2cYtk0yTk0UBWGAxT8'
ADMIN_ID = 8190715241  # Aapka ID
CHANNEL_USERNAME = "@A1Android" # Aapka Channel jahan post jayega
USER_FILE = "users.txt"

bot = telebot.TeleBot(TOKEN)

# --- WEB SERVER (Render ke liye) ---
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
# Sirf Admin jab private mein kuch bhejega, wo Channel pe jayega
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio'], func=lambda m: m.chat.id == ADMIN_ID and m.chat.type == 'private')
def forward_to_channel(message):
    try:
        # Message ko copy karke channel pe bhejta hai
        bot.copy_message(chat_id=CHANNEL_USERNAME, from_chat_id=message.chat.id, message_id=message.message_id)
        bot.reply_to(message, f"✅ Sent to {CHANNEL_USERNAME}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: Bot ko Channel me ADMIN banayein.\nError: {e}")

# --- 2. GROUP KEYWORDS (Hopweb Reply) ---
# Ye Group aur Private dono jagah kaam karega
@bot.message_handler(func=lambda m: True)
def auto_reply(message):
    text = message.text.lower() # Message ko chhota text banata hai check karne ke liye
    user_id = message.chat.id
    
    # User Save karna (Stats ke liye)
    if message.chat.type == 'private':
        save_user(user_id)

    # --- KEYWORD: HOPWEB ---
    if "hopweb" in text:
        # Option A: Link Bhejna (Sabse Aasan)
        markup = types.InlineKeyboardMarkup()
        btn_dl = types.InlineKeyboardButton("⬇️ Download HopWeb", url="https://play.google.com/store/apps/details?id=com.hopweb") # Yahan Link badal sakte hain
        markup.add(btn_dl)
        
        bot.reply_to(message, "Ye lijiye HopWeb App 👇", reply_markup=markup)
        
        # Option B: Agar Direct File bhejni hai (Advanced)
        # Niche wali line uncomment karein agar aapke paas File ID hai:
        # bot.send_document(message.chat.id, "FILE_ID_YAHAN_DALEIN")

    # --- COMMAND: START ---
    elif text == "/start":
        first_name = message.from_user.first_name
        welcome_text = f"Hello {first_name}! 👋\nSocial Media join karein:"
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_telegram = types.InlineKeyboardButton("📢 Join Telegram", url="https://t.me/A1Android")
        btn_youtube = types.InlineKeyboardButton("📺 Subscribe YouTube", url="https://www.youtube.com/@Aiapplication1")
        btn_facebook = types.InlineKeyboardButton("👍 Follow Facebook", url="https://www.facebook.com/profile.php?id=61555961901782")
        markup.add(btn_telegram, btn_youtube, btn_facebook)
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

    # --- COMMAND: STATS (Admin Only) ---
    elif text == "/stats" and user_id == ADMIN_ID:
        users = get_users()
        bot.reply_to(message, f"📊 Total Users: {len(users)}")

    # --- COMMAND: BROADCAST (Admin Only) ---
    elif text.startswith("/broadcast") and user_id == ADMIN_ID:
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
            bot.reply_to(message, f"✅ Sent to {count} users.")

# --- START BOT ---
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
