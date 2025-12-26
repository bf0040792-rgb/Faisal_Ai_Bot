import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- CONFIGURATION (Apna Token aur ID Check karein) ---
TOKEN = '8434658302:AAFTeNg0PDQIHWnNX2cYtk0yTk0UBWGAxT8'
ADMIN_ID = 8190715241  # Aapka Admin ID
CHANNEL_USERNAME = "@A1Android" 
USER_FILE = "users.txt"

# --- LINKS (Yahan wo links hain jo Bot reply karega) ---
LINK_YOUTUBE = "https://www.youtube.com/@Aiapplication1"
LINK_TELEGRAM = "https://t.me/A1Android"
LINK_FACEBOOK = "https://www.facebook.com/profile.php?id=61555961901782"

bot = telebot.TeleBot(TOKEN)

# --- WEB SERVER (Render ke liye zaroori) ---
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
# Admin private me jo bhejega wo Channel pe jayega
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio'], func=lambda m: m.chat.id == ADMIN_ID and m.chat.type == 'private')
def forward_to_channel(message):
    # Agar Admin commands use kar raha hai to post mat karo
    if message.text and message.text.startswith('/'):
        pass # Command handler niche deal karega
    else:
        try:
            bot.copy_message(chat_id=CHANNEL_USERNAME, from_chat_id=message.chat.id, message_id=message.message_id)
            bot.reply_to(message, f"✅ Post Sent to {CHANNEL_USERNAME}")
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {e}")

# --- 2. GROUP & USER AUTO REPLY (Smart Features) ---
@bot.message_handler(func=lambda m: True)
def auto_reply(message):
    text = message.text.lower() # Message ko chhota text banata hai check karne ke liye
    user_id = message.chat.id
    
    # User Save (Sirf Private Chat me)
    if message.chat.type == 'private':
        save_user(user_id)

    # --- LOGIC START ---

    # 1. YOUTUBE MAANGA?
    if "youtube" in text:
        bot.reply_to(message, f"📺 Ye lijiye YouTube Channel ka link:\n{LINK_YOUTUBE}")

    # 2. TELEGRAM/CHANNEL MAANGA?
    elif "telegram" in text or "channel" in text:
        bot.reply_to(message, f"📢 Ye raha hamara Telegram Channel:\n{LINK_TELEGRAM}")

    # 3. FACEBOOK MAANGA?
    elif "facebook" in text:
        bot.reply_to(message, f"👍 Facebook Page:\n{LINK_FACEBOOK}")

    # 4. HOPWEB MAANGA?
    elif "hopweb" in text:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("⬇️ Download HopWeb", url="https://play.google.com/store/apps/details?id=com.hopweb")
        markup.add(btn)
        bot.reply_to(message, "HopWeb App yahan se download karein:", reply_markup=markup)

    # 5. SIRF "LINK" MAANGA? (Sab dikhao)
    elif text == "link" or text == "links":
        markup = types.InlineKeyboardMarkup(row_width=1)
        b1 = types.InlineKeyboardButton("📺 YouTube", url=LINK_YOUTUBE)
        b2 = types.InlineKeyboardButton("📢 Telegram", url=LINK_TELEGRAM)
        b3 = types.InlineKeyboardButton("👍 Facebook", url=LINK_FACEBOOK)
        markup.add(b1, b2, b3)
        bot.reply_to(message, "📌 Yahan hamare saare links hain:", reply_markup=markup)

    # 6. COMMAND: /START
    elif text == "/start":
        first_name = message.from_user.first_name
        welcome_text = f"Hello {first_name}! 👋\nMain A1Android ka Assistant hun.\n\nAap Group me likh sakte hain:\n- 'YouTube link'\n- 'Channel link'\n- 'Hopweb'"
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=LINK_TELEGRAM))
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

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
