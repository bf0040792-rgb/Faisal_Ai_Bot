import telebot
from telebot import types
import os
import json
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
TOKEN = '8434658302:AAFTeNg0PDQIHWnNX2cYtk0yTk0UBWGAxT8'
ADMIN_ID = 8190715241
CHANNEL_USERNAME = "@A1Android"
DATA_FILE = "memory.json" # Yahan bot data save karega

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

# --- MEMORY SYSTEM (Data Save/Load) ---
# Ye functions bot ko cheezein yaad rakhne me madad karte hain
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# --- 1. NEW FEATURE: ADD KEYWORDS (Admin Only) ---
# Command: /save [keyword]
# Tareeka: Kisi File/Link/Text par reply karke likhein: /save pubg
@bot.message_handler(commands=['save'])
def save_keyword(message):
    if message.chat.id != ADMIN_ID:
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ Ghalat tareeka!\nAise use karein:\nKisi file/message pe Reply karein aur likhein: `/save keyword`\nExample: `/save pubg`")
            return

        keyword = command_parts[1].lower() # Keyword (e.g., 'pubg')
        data = load_data()

        # Check karein Admin ne kis cheez pe reply kiya hai
        if message.reply_to_message:
            reply = message.reply_to_message
            
            # Agar Document/File hai
            if reply.document:
                data[keyword] = {"type": "document", "id": reply.document.file_id, "caption": reply.caption}
            # Agar Video hai
            elif reply.video:
                data[keyword] = {"type": "video", "id": reply.video.file_id, "caption": reply.caption}
            # Agar Photo hai
            elif reply.photo:
                data[keyword] = {"type": "photo", "id": reply.photo[-1].file_id, "caption": reply.caption}
            # Agar Sirf Text/Link hai
            elif reply.text:
                data[keyword] = {"type": "text", "content": reply.text}
            else:
                bot.reply_to(message, "❌ Main is type ki file save nahi kar sakta.")
                return
            
            save_data(data)
            bot.reply_to(message, f"✅ Saved!\nAb group me koi **'{keyword}'** likhega to ye milega.")
            
            # Channel par bhi forward kar do (Optional)
            try:
                bot.copy_message(chat_id=CHANNEL_USERNAME, from_chat_id=message.chat.id, message_id=reply.message_id)
            except:
                pass

        else:
            bot.reply_to(message, "❌ Please kisi message ya file par Reply karke command likhein.")

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# --- 2. DELETE KEYWORD ---
@bot.message_handler(commands=['delete'])
def delete_keyword(message):
    if message.chat.id != ADMIN_ID:
        return
    try:
        key = message.text.split()[1].lower()
        data = load_data()
        if key in data:
            del data[key]
            save_data(data)
            bot.reply_to(message, f"🗑 Deleted keyword: {key}")
        else:
            bot.reply_to(message, "⚠️ Ye keyword exist nahi karta.")
    except:
        bot.reply_to(message, "Use: /delete keyword")

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
