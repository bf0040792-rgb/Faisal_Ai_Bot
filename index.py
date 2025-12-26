import telebot
from telebot import types
import os
import json
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
TOKEN = '8434658302:AAFTeNg0PDQIHWnNX2cYtk0yTk0UBWGAxT8'
ADMIN_ID = 8190715241
PIN_CODE = "7010"
CHANNEL_USERNAME = "@A1Android"

# --- MAIN LINKS ---
LINK_FACEBOOK_MAIN = "https://www.facebook.com/profile.php?id=61555961901782"
LINK_YOUTUBE_MAIN = "https://www.youtube.com/@Aiapplication1"
LINK_TELEGRAM_MAIN = "https://t.me/A1Android"

DATA_FILE = "memory.json"
ACCESS_FILE = "access.json"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- WEB SERVER (For Render) ---
@app.route('/')
def home():
    return "Bot is Running! 🚀"

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

# --- 1. PIN SYSTEM ---
def check_access(user_id):
    if user_id == ADMIN_ID:
        return True
    access_data = load_json(ACCESS_FILE)
    return str(user_id) in access_data

# --- 2. SAVE COMMAND (Save + Post to Channel) ---
@bot.message_handler(commands=['save'])
def save_keyword(message):
    if message.chat.id != ADMIN_ID:
        return

    try:
        # Command format: /save keyword
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ **Incorrect Format!**\nReply to a message/file and write:\n`/save keyword`\nExample: `/save facebook reels`")
            return

        keyword = command_parts[1].lower().strip()
        data = load_json(DATA_FILE)

        if message.reply_to_message:
            reply = message.reply_to_message
            
            # --- PREPARE DATA ---
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
                bot.reply_to(message, "❌ Unsupported file type.")
                return
            
            # Save to memory
            data[keyword] = content
            save_json(DATA_FILE, data)
            
            # --- POST TO CHANNEL (Only now) ---
            try:
                bot.copy_message(chat_id=CHANNEL_USERNAME, from_chat_id=message.chat.id, message_id=reply.message_id)
                bot.reply_to(message, f"✅ **Success!**\n1. Saved as keyword: `{keyword}`\n2. Posted to {CHANNEL_USERNAME}")
            except Exception as e:
                bot.reply_to(message, f"✅ Saved locally, but failed to post to channel.\nError: {e}")
                
        else:
            bot.reply_to(message, "❌ You must REPLY to a message to save it.")

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# --- 3. UNIVERSAL MESSAGE HANDLER ---
# Handles Group, Private, Channel Posts, Anonymous Admins
@bot.message_handler(func=lambda m: True, content_types=['text'])
@bot.channel_post_handler(func=lambda m: True, content_types=['text'])
def handle_message(message):
    try:
        # Extract Text
        text = ""
        if message.text:
            text = message.text.lower().strip()
        elif message.caption:
            text = message.caption.lower().strip()
            
        if not text:
            return

        user_id = message.chat.id

        # --- PRIVATE CHAT (PIN SECURITY) ---
        if message.chat.type == 'private':
            if not check_access(user_id):
                if text == PIN_CODE:
                    d = load_json(ACCESS_FILE)
                    d[str(user_id)] = True
                    save_json(ACCESS_FILE, d)
                    bot.reply_to(message, "✅ **Access Granted!**\nWelcome. You can now use the bot.")
                    return
                else:
                    bot.reply_to(message, "🔒 **Bot Locked!**\nPlease enter the correct PIN to continue.")
                    return

        # --- GROUP/CHANNEL LOGIC ---
        
        # Start Command
        if text == "/start":
            if message.chat.type == 'private':
                 bot.reply_to(message, "Hello! Bot is Active.")
            return

        saved_data = load_json(DATA_FILE)
        replied = False

        # 1. SMART SEARCH: FACEBOOK
        if "facebook" in text:
            # Always send main link
            bot.reply_to(message, f"👍 **Facebook Main Channel:**\n{LINK_FACEBOOK_MAIN}")
            replied = True
            
            # If user typed ONLY "facebook", search for related saved items (like 'facebook reels')
            if text == "facebook":
                for key, content in saved_data.items():
                    if "facebook" in key:
                        send_saved_content(message.chat.id, content)

        # 2. SMART SEARCH: YOUTUBE
        elif "youtube" in text:
             bot.reply_to(message, f"📺 **YouTube Main Channel:**\n{LINK_YOUTUBE_MAIN}")
             replied = True

        # 3. EXACT KEYWORD MATCH (From Saved Data)
        if text in saved_data:
            if not replied: # Avoid double reply if logic overlapped
                send_saved_content(message.chat.id, saved_data[text])
                replied = True
        
        # 4. HOPWEB FALLBACK
        if not replied and "hopweb" in text:
             bot.reply_to(message, "⬇️ HopWeb App: https://play.google.com/store/apps/details?id=com.hopweb")

    except Exception as e:
        print(f"Error: {e}")

# Function to send saved content based on type
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
