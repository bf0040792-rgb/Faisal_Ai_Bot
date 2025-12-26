import telebot
from telebot import types
import os
import json
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
TOKEN = '8434658302:AAFTeNg0PDQIHWnNX2cYtk0yTk0UBWGAxT8' # Apna Token
ADMIN_ID = 8190715241 # Aapka ID
PIN_CODE = "7010" # Aapka PIN Password

# --- LINKS (Fixed Links) ---
LINK_FACEBOOK_MAIN = "https://www.facebook.com/profile.php?id=61555961901782"
LINK_YOUTUBE_MAIN = "https://www.youtube.com/@Aiapplication1"
LINK_TELEGRAM_MAIN = "https://t.me/A1Android"

# Files to store data
DATA_FILE = "memory.json"
ACCESS_FILE = "access.json"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- WEB SERVER ---
@app.route('/')
def home():
    return "Bot is Running with PIN System! 🚀"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- DATA HANDLING ---
def load_json(filename):
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

# --- 1. PIN SYSTEM CHECK ---
def check_access(user_id):
    # Admin ko PIN ki zaroorat nahi
    if user_id == ADMIN_ID:
        return True
    
    access_data = load_json(ACCESS_FILE)
    return str(user_id) in access_data

# --- 2. SAVE COMMAND (Admin Only) ---
# Example: /save facebook reels description
@bot.message_handler(commands=['save'])
def save_keyword(message):
    if message.chat.id != ADMIN_ID:
        return

    try:
        # Command se keyword nikalna (e.g. "facebook reels description")
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ Ghalat! Aise likhein:\nReply karke: `/save facebook reels description`")
            return

        keyword = command_parts[1].lower().strip()
        data = load_json(DATA_FILE)

        if message.reply_to_message:
            reply = message.reply_to_message
            
            # Data structure create karna
            content = {"caption": reply.caption if reply.caption else ""}
            
            if reply.document:
                content["type"] = "document"
                content["id"] = reply.document.file_id
            elif reply.video:
                content["type"] = "video"
                content["id"] = reply.video.file_id
            elif reply.photo:
                content["type"] = "photo"
                content["id"] = reply.photo[-1].file_id
            elif reply.text:
                content["type"] = "text"
                content["content"] = reply.text
            else:
                bot.reply_to(message, "❌ Main ye file save nahi kar sakta.")
                return
            
            data[keyword] = content
            save_json(DATA_FILE, data)
            bot.reply_to(message, f"✅ Saved as: **{keyword}**\nAb koi '{keyword}' likhega to ye milega.")
        else:
            bot.reply_to(message, "❌ Kisi message par Reply karna zaroori hai.")

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# --- 3. MAIN MESSAGE HANDLER ---
@bot.message_handler(func=lambda m: True, content_types=['text'])
@bot.channel_post_handler(func=lambda m: True, content_types=['text'])
def handle_message(message):
    try:
        user_id = message.chat.id
        text = message.text.lower().strip() if message.text else ""

        # --- STEP A: PIN CHECK (Sirf Private Chat me) ---
        if message.chat.type == 'private':
            if not check_access(user_id):
                # Agar user ne PIN bheja hai check karo
                if text == PIN_CODE:
                    access_data = load_json(ACCESS_FILE)
                    access_data[str(user_id)] = True
                    save_json(ACCESS_FILE, access_data)
                    bot.reply_to(message, "✅ **PIN Confirmed!**\nWelcome! Ab aap bot use kar sakte hain.\n\nType 'Facebook' or 'Youtube'.")
                    return
                else:
                    bot.reply_to(message, "🔒 **Bot Locked!**\nKripya sahi PIN code dalein aage badhne ke liye.")
                    return

        # --- STEP B: LOGIC START ---
        
        # 1. Start Command
        if text == "/start":
            bot.reply_to(message, "Hello! Bot Active hai.\nKuch search karein (eg: Facebook, Hopweb).")
            return

        saved_data = load_json(DATA_FILE)
        replied = False

        # --- STEP C: SMART FACEBOOK SEARCH ---
        # Agar user "Facebook" likhe, to Main Link + Saved Data dono milega
        
        if "facebook" in text:
            # 1. Main Link bhejo
            bot.reply_to(message, f"👍 **Facebook Main Channel:**\n{LINK_FACEBOOK_MAIN}")
            replied = True
            
            # 2. Check karo agar 'Facebook' se juda kuch save hai (jaise 'facebook reels description')
            # Agar user ne exact "facebook reels description" likha hai, wo niche exact match me pakda jayega.
            # Lekin agar usne sirf "facebook" likha, to hum milta-julta dhoondenge.
            
            if text == "facebook": # Agar sirf 'facebook' likha hai
                for key, content in saved_data.items():
                    if "facebook" in key:
                        # Saved item bhi bhej do
                        send_saved_content(message.chat.id, content)

        # Agar YouTube manga
        elif "youtube" in text:
             bot.reply_to(message, f"📺 **YouTube Main Channel:**\n{LINK_YOUTUBE_MAIN}")
             replied = True

        # --- STEP D: EXACT KEYWORD MATCH (Saved Data) ---
        # Agar user ne exact wohi likha jo aapne save kiya tha
        if text in saved_data:
            if not replied: # Agar upar Facebook wala reply nahi gaya, tab hi bhejo (duplicate se bachne ke liye)
                send_saved_content(message.chat.id, saved_data[text])
                replied = True
        
        # Agar kuch nahi mila aur user ne specific maanga tha
        if not replied and "hopweb" in text:
             bot.reply_to(message, "⬇️ Download HopWeb: https://play.google.com/store/apps/details?id=com.hopweb")

    except Exception as e:
        print(f"Error: {e}")

# Function to send saved content
def send_saved_content(chat_id, content):
    try:
        if content['type'] == 'text':
            bot.send_message(chat_id, content['content'])
        elif content['type'] == 'document':
            bot.send_document(chat_id, content['id'], caption=content.get('caption', ''))
        elif content['type'] == 'video':
            bot.send_video(chat_id, content['id'], caption=content.get('caption', ''))
        elif content['type'] == 'photo':
            bot.send_photo(chat_id, content['id'], caption=content.get('caption', ''))
    except Exception as e:
        print(f"Send Error: {e}")

# --- START BOT ---
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(skip_pending=True)
# --- 3. AUTO REPLY (Dynamic + Fixed) ---
@bot.message_handler(func=lambda m: True, content_types=['text'])
@bot.channel_post_handler(func=lambda m: True, content_types=['text']) 
def smart_reply(message):
    try:
        # Message text nikalo
        text = ""
        if message.text:
            text = message.text.lower()
        elif message.caption:
            text = message.caption.lower()
            
        if not text:
            return

        # Start Command
        if text == "/start":
            bot.reply_to(message, "Hello! Main Active hoon.")
            return

        # --- DYNAMIC DATA CHECK ---
        data = load_data()
        
        # Check karein agar message me koi saved keyword hai
        found_reply = False
        
        # Hum check karenge ki user ke message me keyword hai ya nahi
        for keyword, content in data.items():
            if keyword in text:
                # Agar mil gaya, to bhej do
                if content['type'] == 'text':
                    bot.reply_to(message, content['content'])
                
                elif content['type'] == 'document':
                    bot.send_document(message.chat.id, content['id'], caption=content['caption'])
                
                elif content['type'] == 'video':
                    bot.send_video(message.chat.id, content['id'], caption=content['caption'])
                    
                elif content['type'] == 'photo':
                    bot.send_photo(message.chat.id, content['id'], caption=content['caption'])
                
                found_reply = True
                return # Ek reply karke ruk jao

        # --- HARDCODED BACKUP (Jo aapne pehle maanga tha) ---
        if not found_reply:
            if "facebook" in text:
                bot.reply_to(message, "👍 Facebook: https://www.facebook.com/profile.php?id=61555961901782")
            elif "youtube" in text:
                bot.reply_to(message, "📺 YouTube: https://www.youtube.com/@Aiapplication1")

    except Exception as e:
        print(f"Error: {e}")

# --- START BOT ---
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(skip_pending=True)if __name__ == "__main__":
    keep_alive()
    # 'none_stop=True' zaroori hai taaki bot ruke nahi
    bot.infinity_polling(skip_pending=True)
