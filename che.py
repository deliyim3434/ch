import os
import pymongo
import time
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from flask import Flask, request, render_template

# Bot & Database Config
API_ID = 21017005
API_HASH = "031173130fa724e7ecded16064724d96"
BOT_TOKEN = "7940182890:AAFpu-UoIxGYaCIUrzwO9D6hdE403LNaKuA"
MONGO_URI = "mongodb+srv://areszyn:CVft6qaxIkf9rOiR@areszyn.zcmfu.mongodb.net/?retryWrites=true&w=majority&appName=areszyn"
OWNER_ID =  8016828914 # Replace with your Telegram ID
LOG_CHANNEL = -1002337387015 # Log Channel

# Initialize bot & MongoDB
bot = Client("banbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = pymongo.MongoClient(MONGO_URI)["BanBot"]
banned_users = db["banned"]

# Flask Admin Panel
app = Flask(__name__)

@app.route("/")
def home():
    return "BanBot Admin Panel Running!"

# ✅ Ban a User
@bot.on_message(filters.command("ban") & filters.group)
def ban_user(client, message):
    if not message.reply_to_message:
        message.reply("Reply to a user to ban them!")
        return

    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id

    # Prevent banning bot owner
    if user_id == OWNER_ID:
        message.reply("You cannot ban my owner! 😡")
        return

    client.ban_chat_member(chat_id, user_id)
    banned_users.insert_one({"chat_id": chat_id, "user_id": user_id, "timestamp": time.time()})
    message.reply(f"User {user_id} has been banned.")

    # Log ban
    client.send_message(LOG_CHANNEL, f"User {user_id} banned in {chat_id}")

# ✅ Unban a User
@bot.on_message(filters.command("unban") & filters.group)
def unban_user(client, message):
    if not message.reply_to_message:
        message.reply("Reply to a user to unban them!")
        return

    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id

    client.unban_chat_member(chat_id, user_id)
    banned_users.delete_one({"chat_id": chat_id, "user_id": user_id})
    message.reply(f"User {user_id} has been unbanned.")

# ✅ Ban All Members (Except Owner)
@bot.on_message(filters.command("banall") & filters.private)
def ban_all(client, message):
    args = message.text.split()
    if len(args) < 2:
        message.reply("Usage: /banall chat_id")
        return
    
    chat_id = int(args[1])
    members = client.get_chat_members(chat_id)

    for member in members:
        if member.user.id != OWNER_ID:
            client.ban_chat_member(chat_id, member.user.id)
            banned_users.insert_one({"chat_id": chat_id, "user_id": member.user.id, "timestamp": time.time()})
    
    message.reply(f"All members banned from {chat_id}!")

# ✅ Unban All Members
@bot.on_message(filters.command("unbanall") & filters.private)
def unban_all(client, message):
    args = message.text.split()
    if len(args) < 2:
        message.reply("Usage: /unbanall chat_id")
        return
    
    chat_id = int(args[1])
    users = banned_users.find({"chat_id": chat_id})
    
    for user in users:
        client.unban_chat_member(chat_id, user["user_id"])
        banned_users.delete_one({"chat_id": chat_id, "user_id": user["user_id"]})
    
    message.reply(f"All members unbanned from {chat_id}!")

# ✅ Send Special Welcome to Owner
@bot.on_chat_member_updated()
def welcome_owner(client, event):
    if event.new_chat_member.user.id == OWNER_ID and event.new_chat_member.status in ["member", "administrator"]:
        client.send_message(event.chat.id, "🔥 **My Owner has joined! Respect!** 🔥")

# ✅ Web Panel
@app.route("/banlist/<int:chat_id>")
def get_banlist(chat_id):
    users = list(banned_users.find({"chat_id": chat_id}, {"_id": 0, "user_id": 1}))
    return {"banned_users": [user["user_id"] for user in users]}

@app.route("/ban", methods=["POST"])
def web_ban():
    data = request.json
    chat_id = data.get("chat_id")
    user_id = data.get("user_id")
    
    if chat_id and user_id:
        bot.ban_chat_member(chat_id, user_id)
        banned_users.insert_one({"chat_id": chat_id, "user_id": user_id, "timestamp": time.time()})
        return {"status": "banned"}
    
    return {"error": "Missing chat_id or user_id"}

@app.route("/unban", methods=["POST"])
def web_unban():
    data = request.json
    chat_id = data.get("chat_id")
    user_id = data.get("user_id")

    if chat_id and user_id:
        bot.unban_chat_member(chat_id, user_id)
        banned_users.delete_one({"chat_id": chat_id, "user_id": user_id})
        return {"status": "unbanned"}
    
    return {"error": "Missing chat_id or user_id"}

if __name__ == "__main__":
    bot.start()
    app.run(host="0.0.0.0", port=5000)
