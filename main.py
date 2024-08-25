# -*- coding: utf-8 -*-

__updated__ = "2024-07-15 02:19:39"


import logging
import asyncio
from random import choice
from pyrogram import Client, filters
from pymongo import MongoClient
import random
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
    User,
    ChatMemberUpdated,
    ChatMember,
)

import cachetools
import tgcrypto
import pydantic
import aiogram
import fluent.runtime
import pymongo
from datetime import datetime, timedelta



#-------------------------------------------------------------------#

BOT_ID = 7454035971
OWNER_ID = 7242000752
WINNERS = [7242000752] #Sürekli Kazanan
LOG_GROUP_ID = -1002231459610


#-------------------------------------------------------------------#



initial_balance = 25000


user_balances = {}


richest_users = []


start_message = """
__Merhaba! {} 🎰 Slot botuna hoş geldiniz.__

**Ben bir slot botuyum! Hemen oynamaya başlamak için aşağıdaki butonları kullanarak gruba ekleyebilirsiniz.** 🤩

**Komutlarımı görmek için lütfen aşağıdaki butonu kullanın. İyi eğlenceler!** 🥳
"""

komutlar = """
🎰 **Komutlar**

• **/cash - Slot oyununu oynamak için.** 🎰
   Örnek: `/cash 50` veya `/cash 50 2x`
   ❌ NOT: `/cash 50 3x` yaptığınızda, çarpan kadar paranız gider.

• **/fcash - Futbol oyununu oynamak için.** ⚽️
   Örnek: `/fcash 100` veya `/fcash 100 3x`

• **/bcash - Basketbol oyununu oynamak için.** 🏀
   Örnek: `/bcash 50` veya `/bcash 50 2x`

• **/gunluk - Günlük alacağınız bonus.** 🤩

• **/bakiye - Bakiyenizi kontrol etmek için.** 💰

• **/borc - Birine borç göndermek için.** 💸
   Örnek: `/borc [Miktar] [Kullanıcı İD]` veya Mesajı Yanıtla.

• **/zenginler - En zengin kullanıcıları görmek için.** 🤑

🆘 NOT: `/cash`, `/fcash` ve `/bcash` komutları sadece gruplarda çalışır.

"""

#-------------------------------------------------------------------#
API_ID = 24054192
API_HASH = "ed9a8a61a1b4a1ad0915cbe87ba490ed"
BOT_TOKEN = "7454035971:AAGxuve68QgndANHQr71qGWUc1m19UwnCpo"

#-------------------------------------------------------------------#

mongo_client = MongoClient("mongodb+srv://mongoguess:guessmongo@cluster0.zcwklzz.mongodb.net/?retryWrites=true&w=majority")
db = mongo_client["slot_bot_db"]
balances_collection = db["balances"]
richest_collection = db["richest"]
blocked_collection = db["blocked"] 
collection = db['user_bonus_times']  
groups_collection = db["groups"]
users_collection = db["users"]


#-------------------------------------------------------------------#

logging.basicConfig(filename='bot.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

app = Client("slot_bot", 
             api_id=API_ID, 
             api_hash=API_HASH, 
             bot_token=BOT_TOKEN
        )


#-------------------------------------------------------------------#



def load_balances():
    global user_balances
    user_balances = {doc["user_id"]: doc["balance"] for doc in balances_collection.find()}


def save_balance(user_id, balance):
    balances_collection.update_one({"user_id": user_id}, {"$set": {"balance": balance}}, upsert=True)


def load_richest_users():
    global richest_users
    richest_users = [doc["user_id"] for doc in richest_collection.find().sort("balance", -1).limit(10)]


def save_richest_users():
    richest_collection.delete_many({})
    for user_id in richest_users:
        richest_collection.insert_one({"user_id": user_id, "balance": user_balances[user_id]})


def is_user_blocked(user_id):
    return blocked_collection.find_one({"user_id": user_id}) is not None


def block_user(user_id):
    blocked_collection.update_one({"user_id": user_id}, {"$set": {"blocked": True}}, upsert=True)


def unblock_user(user_id):
    blocked_collection.delete_one({"user_id": user_id})

#-------------------------------------------------------------------#


def connect_to_database(db_path):
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            conn = sqlite3.connect(db_path)
            return conn
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print("Veritabanı kilitli. Bekleniyor...")
                time.sleep(1)  
                retry_count += 1
            else:
                raise e

    raise Exception("Veritabanına bağlanırken hata oluştu: Veritabanı kilitli.")

#-------------------------------------------------------------------#

bonus_interval_hours = 5  

user_last_bonus_time = {}

user_last_cash_time = {}

load_balances()
load_richest_users()

#-------------------------------------------------------------------#



@app.on_message(filters.command("start") & filters.private)
async def start(bot: Client, message: Message):
    chat_id = message.chat.id
    first_name = message.from_user.mention
    user_id = message.from_user.id

    
    if user_id not in user_balances:
        user_balances[user_id] = initial_balance
        save_balance(user_id, initial_balance)

    
    users_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "first_name": first_name,
                "username": message.from_user.username
            }
        },
        upsert=True
    )

    await bot.send_message(LOG_GROUP_ID, f"""
#ÖZELDEN START VERDİ#

🤖 **Kullanıcı:** {first_name}
📛 **Kullanıcı Adı:** @{message.from_user.username}
🆔 **Kullanıcı ID:** `{message.from_user.id}`
""")
    msg = await message.reply_text("✨ **Lütfen Bekleyin...**")
    await asyncio.sleep(2)
    await msg.delete()
    await bot.send_message(
        chat_id,
        start_message.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📚 Komutlar", callback_data="cvv"),
                ],
                [
                    InlineKeyboardButton("🗯 Delular", url=f"https://t.me/DelularSohbet"),
                    InlineKeyboardButton("➕ Beni Grubuna Ekle", url=f"https://t.me/Casino_Cash_Money_Bot?startgroup=a"),
                ],
                [
                    InlineKeyboardButton("❤️‍🔥 Geliştirici", user_id=OWNER_ID),
                ]
            ]
        ),
        disable_web_page_preview=True,
    )



@app.on_callback_query(filters.regex("cvv"))
async def handler(bot: Client, query: CallbackQuery):
    await query.edit_message_text(
        komutlar,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔙 Geri", 
                        callback_data="goktug"),                                            
                ],
            ],
        ),
        disable_web_page_preview=True,
    )


# Başlanğıc Button
@app.on_callback_query(filters.regex(r'^goktug$'))
async def _start(bot: Client, query: CallbackQuery):
    await query.edit_message_text(
        start_message.format(query.from_user.mention),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📚 Komutlar", callback_data="cvv"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🗯 Kanal", url=f"https://t.me/DelularSohbet"
                    ),

                    InlineKeyboardButton(
                        "➕ Beni Grubuna Ekle" , url=f"https://t.me/Casino_Cash_Money_Bot?startgroup=a"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "❤️‍🔥 Geliştirici", user_id=OWNER_ID
                    ),
                ]
            ],
        ),
        disable_web_page_preview=True,
    )   






@app.on_message(filters.command(["zenginler", "zengolar"]))
async def get_richest(client: Client, message: Message):
    user_id = message.from_user.id
    is_group = message.chat.type in ["supergroup", "group"]
    
    if is_group:
        try:
            users = await client.get_chat_members(message.chat.id)
            user_ids = [user.user.id for user in users]
            users = [user_id for user_id in user_balances if user_id in user_ids]
            users.sort(key=lambda user_id: user_balances[user_id], reverse=True)
            richest_users_list = users[:10]
            text = "🏆 **Bu grup için en zengin kullanıcılar:**\n\n"
            for i, user_id in enumerate(richest_users_list[:3], start=1):
                try:
                    user = await client.get_users(user_id)
                    if i == 1:
                        text += f"🥇 **1.** {user.first_name}  ➔  `{user_balances[user_id]}` **TL**\n"
                    elif i == 2:
                        text += f"🥈 **2.** {user.first_name}  ➔  `{user_balances[user_id]}` **TL**\n"
                    elif i == 3:
                        text += f"🥉 **3.** {user.first_name}  ➔  `{user_balances[user_id]}` **TL**\n"
                except Exception as e:
                    text += f"❌ Kullanıcı bulunamadı\n"
            
            for i, user_id in enumerate(richest_users_list[3:], start=4):
                try:
                    user = await client.get_users(user_id)
                    text += f"▫️ **{i}.** {user.first_name}  ➔  `{user_balances[user_id]}` **TL**\n"
                except Exception as e:
                    text += f"❌ Kullanıcı bulunamadı\n"
                    
        except Exception as e:
            text = "Grup üyeleri alınamadı"
    else:
        richest_users_list = sorted(user_balances.items(), key=lambda x: x[1], reverse=True)[:10]
        text = "**🌎 Global en zengin kullanıcılar:**\n\n"
        for i, (user_id, balance) in enumerate(richest_users_list[:3], start=1):
            try:
                user = await client.get_users(user_id)
                if i == 1:
                    text += f"🥇 **1.** {user.first_name}  ➔  `{balance}` **TL**\n"
                elif i == 2:
                    text += f"🥈 **2.** {user.first_name}  ➔  `{balance}` **TL**\n"
                elif i == 3:
                    text += f"🥉 **3.** {user.first_name}  ➔  `{balance}` **TL**\n"
            except Exception as e:
                text += f"❌ Kullanıcı bulunamadı\n"
        
        for i, (user_id, balance) in enumerate(richest_users_list[3:], start=4):
            try:
                user = await client.get_users(user_id)
                text += f"▫️ **{i}.** {user.first_name}  ➔  `{balance}` **TL**\n"
            except Exception as e:
                text += f"❌ Kullanıcı bulunamadı\n"
    
    await message.reply_text(text)









@app.on_message(filters.command("wdaily") & filters.user(OWNER_ID))
async def daily_bonus_to_all(client: Client, message: Message):
    try:
        for user_id in user_balances:
            user_balances[user_id] += 30000
            save_balance(user_id, user_balances[user_id])
        await message.reply("__Tüm kullanıcılara bonus başarıyla eklendi. ✨__")
    except Exception as e:
        await message.reply(f"__Günlük bonus eklenirken bir hata oluştu: {e}__")







@app.on_message(filters.command("bcash") & filters.group)
async def play_basket(client: Client, message: Message):
    if is_user_blocked(message.from_user.id):
        await message.reply("Üzgünüm, bu komutu kullanma yetkiniz engellendi. 🚫")
        return

    user_id = message.from_user.id

    if user_id not in user_balances:
        await message.reply("__Basketbol oyununu oynamak için önce özelden start verin. 💫__")
        return

    current_time = datetime.now()
    last_cash_time = user_last_cash_time.get(user_id)

    if last_cash_time and current_time - last_cash_time < timedelta(seconds=3):
        await message.reply(f"**Lütfen 3 saniye bekleyin. ⏳**")
        return

    try:
        amount_str = message.command[1]
        if not amount_str.isdigit() or len(amount_str) > 17:
            await message.reply("**Lütfen sadece maksimum 17 rakam içeren bir miktar girin. 💵**")
            return
        
        amount = int(amount_str)

        multiplier = 1
        if len(message.command) > 2:
            multiplier_str = message.command[2]
            if multiplier_str[-1] == 'x' and multiplier_str[:-1].isdigit():
                multiplier = int(multiplier_str[:-1])
            else:
                raise ValueError()
            if multiplier < 1 or multiplier > 6:
                await message.reply("**Çarpan 1x ile 6x arasında olmalıdır. Örnek: /bcash 45 2x 🏀**")
                return

    except (IndexError, ValueError):
        await message.reply("**Lütfen geçerli bir miktar ve çarpan girin. Örnek: /bcash 45 veya /bcash 45 2x 🏀**")
        return

    if amount <= 0:
        await message.reply("__Lütfen pozitif bir miktar girin. 💵__")
        return

    user_balance = user_balances.get(user_id, 0)

    if amount > user_balance:
        await message.reply("**Yeterli bakiyeniz yok.** 😢")
        return

    
    dice_message = await client.send_dice(message.chat.id, emoji="🏀")

    
    await asyncio.sleep(3)

    
    dice_value = dice_message.dice.value

    
    if dice_value >= 4:  
        win_amount = amount * multiplier
        user_balances[user_id] = max(user_balance + win_amount, 0)
        result_message = f"__Tebrikler! 🎉 Basket topu potaya girdi ve `{win_amount}` TL kazandınız.__\n**Güncel bakiyeniz: `{user_balances[user_id]}` TL 💰**"
    else:
        win_amount = -amount * multiplier
        user_balances[user_id] = max(user_balance + win_amount, 0)
        result_message = f"__Üzgünüm 🥹 Basket topu potaya girmedi ve `{amount * multiplier}` TL kaybettiniz.__\n**Güncel bakiyeniz: `{user_balances[user_id]}` TL 💰**"

    save_balance(user_id, user_balances[user_id])

    if user_id not in richest_users and len(richest_users) < 10:
        richest_users.append(user_id)
    richest_users.sort(key=lambda x: user_balances[x], reverse=True)
    save_richest_users()

    user_last_cash_time[user_id] = current_time

    
    
    chat = message.chat
    user = message.from_user

    user_name = user.username if user.username else "None"
    group_name = chat.title
    group_link = f"@{chat.username}" if chat.username else "None"

    await client.send_message(LOG_GROUP_ID, f"""
**KOMUT KULLANILDI**

👤 **Kullanıcı:** {user.mention}
📛 **Kullanıcı Adı:** @{user_name}
🆔 **Kullanıcı İD:** `{user.id}`
🏘️ **Grup Adı:** {group_name}
🤖 **Grup İD:** `{chat.id}`
🔗 **Grup Linki:** {group_link}
🈷️ **Miktar:** {message.text} TL
🔰 **Sonuç:** {'kazandı' if win_amount > 0 else 'kaybetti'}
💵 **Güncel Bakiye:** `{user_balances[user_id]}` TL
""")

    
    
    await message.reply(result_message)






@app.on_message(filters.command("fcash") & filters.group)
async def play_basket(client: Client, message: Message):
    if is_user_blocked(message.from_user.id):
        await message.reply("Üzgünüm, bu komutu kullanma yetkiniz engellendi. 🚫")
        return

    user_id = message.from_user.id

    if user_id not in user_balances:
        await message.reply("__Futbol oyununu oynamak için önce özelden start verin. 💫__")
        return

    current_time = datetime.now()
    last_cash_time = user_last_cash_time.get(user_id)

    if last_cash_time and current_time - last_cash_time < timedelta(seconds=3):
        await message.reply(f"**Lütfen 3 saniye bekleyin. ⏳**")
        return

    try:
        amount_str = message.command[1]
        if not amount_str.isdigit() or len(amount_str) > 17:
            await message.reply("**Lütfen sadece maksimum 17 rakam içeren bir miktar girin. 💵**")
            return
        
        amount = int(amount_str)

        multiplier = 1
        if len(message.command) > 2:
            multiplier_str = message.command[2]
            if multiplier_str[-1] == 'x' and multiplier_str[:-1].isdigit():
                multiplier = int(multiplier_str[:-1])
            else:
                raise ValueError()
            if multiplier < 1 or multiplier > 6:
                await message.reply("**Çarpan 1x ile 6x arasında olmalıdır. Örnek: /fcash 45 2x ⚽️**")
                return

    except (IndexError, ValueError):
        await message.reply("**Lütfen geçerli bir miktar ve çarpan girin. Örnek: /fcash 45 veya /fcash 45 2x ⚽️**")
        return

    if amount <= 0:
        await message.reply("__Lütfen pozitif bir miktar girin. 💵__")
        return

    user_balance = user_balances.get(user_id, 0)

    if amount > user_balance:
        await message.reply("**Yeterli bakiyeniz yok.** 😢")
        return

    
    dice_message = await client.send_dice(message.chat.id, emoji="⚽️")

    
    await asyncio.sleep(3)

    
    dice_value = dice_message.dice.value

    
    if dice_value >= 3:  
        win_amount = amount * multiplier
        user_balances[user_id] = max(user_balance + win_amount, 0)
        result_message = f"__Tebrikler! 🎉 Gooool ! `{win_amount}` TL kazandınız.__\n**Güncel bakiyeniz: `{user_balances[user_id]}` TL 💰**"
    else:
        win_amount = -amount * multiplier
        user_balances[user_id] = max(user_balance + win_amount, 0)
        result_message = f"__Üzgünüm 🥹 Iskaladııın !  `{amount * multiplier}` TL kaybettiniz.__\n**Güncel bakiyeniz: `{user_balances[user_id]}` TL 💰**"

    save_balance(user_id, user_balances[user_id])

    if user_id not in richest_users and len(richest_users) < 10:
        richest_users.append(user_id)
    richest_users.sort(key=lambda x: user_balances[x], reverse=True)
    save_richest_users()

    user_last_cash_time[user_id] = current_time

    
    chat = message.chat
    user = message.from_user

    user_name = user.username if user.username else "None"
    group_name = chat.title
    group_link = f"@{chat.username}" if chat.username else "None"

    await client.send_message(LOG_GROUP_ID, f"""
**KOMUT KULLANILDI**

👤 **Kullanıcı:** {user.mention}
📛 **Kullanıcı Adı:** @{user_name}
🆔 **Kullanıcı İD:** `{user.id}`
🏘️ **Grup Adı:** {group_name}
🤖 **Grup İD:** `{chat.id}`
🔗 **Grup Linki:** {group_link}
🈷️ **Miktar:** {message.text} TL
🔰 **Sonuç:** {'kazandı' if win_amount > 0 else 'kaybetti'}
💵 **Güncel Bakiye:** `{user_balances[user_id]}` TL
""")

    # Sonucu kullanıcıya bildir
    await message.reply(result_message)









@app.on_message(filters.command("cash") & filters.group)
async def play_slot(client: Client, message: Message):
    if is_user_blocked(message.from_user.id):
        await message.reply("Üzgünüm, bu komutu kullanma yetkiniz engellendi. 🚫")
        return

    user_id = message.from_user.id

    
    if user_id not in user_balances:
        await message.reply("__Slot oyununu oynamak için önce özelden start verin. 💫__")
        return

    
    current_time = datetime.now()
    last_cash_time = user_last_cash_time.get(user_id)

    if last_cash_time and current_time - last_cash_time < timedelta(seconds=3):
        remaining_time = timedelta(seconds=3) - (current_time - last_cash_time)
        await message.reply(f"**Lütfen 3 saniye bekleyin. ⏳**")
        return

    try:
        amount_str = message.command[1]

        
        
        if not amount_str.isdigit() or len(amount_str) > 17:
            await message.reply("**Lütfen sadece maksimum 17 rakam içeren bir miktar girin. 💵**")
            return
        
        amount = int(amount_str)

        
        multiplier = 1

        
        if len(message.command) > 2:
            multiplier_str = message.command[2]
            if multiplier_str[-1] == 'x' and multiplier_str[:-1].isdigit():
                multiplier = int(multiplier_str[:-1])
            else:
                raise ValueError()

            # Çarpanın 1 ile 3 arasında olmasını kontrol et
            if multiplier < 1 or multiplier > 6:
                await message.reply("**Çarpan 1x ile 6x arasında olmalıdır. Örnek: /cash 45 2x 🎰**")
                return

    except (IndexError, ValueError):
        await message.reply("**Lütfen geçerli bir miktar ve çarpan girin. Örnek: /cash 45 veya /cash 45 2x 🎰**")
        return

    if amount <= 0:
        await message.reply("__Lütfen pozitif bir miktar girin. 💵__")
        return

    user_balance = user_balances.get(user_id, 0)

    if amount > user_balance:
        await message.reply("**Yeterli bakiyeniz yok.** 😢")
        return

    
    dice_message = await client.send_dice(message.chat.id, emoji="🎰")

    
    await asyncio.sleep(3)

    
    dice_value = dice_message.dice.value   
    
    win_chance = 0.45 # %45 kazanma şansı
    if user_id in WINNERS or random.random() < win_chance:
        win_amount = amount * multiplier
    else:
        win_amount = -amount * multiplier  # Çarpan kadar miktarı bakiyeden düş

    
    user_balances[user_id] = max(user_balance + win_amount, 0)
    save_balance(user_id, user_balances[user_id])

    
    if user_id not in richest_users and len(richest_users) < 10:
        richest_users.append(user_id)
    richest_users.sort(key=lambda x: user_balances[x], reverse=True)
    save_richest_users()

    
    user_last_cash_time[user_id] = current_time

    
    result = "kazandınız" if win_amount > 0 else "kaybettiniz"
    await message.reply(f"__Tebrikler! 🎉 `{win_amount}` TL {result}.__\n**Güncel bakiyeniz: `{user_balances[user_id]}` TL 💰**" if win_amount > 0 else f"__Üzgünüm 🥹 `{amount * multiplier}` TL {result}.__\n**Güncel bakiyeniz: `{user_balances[user_id]}` TL 💰**")

    
    chat = message.chat
    user = message.from_user

    user_name = user.username if user.username else "None"
    group_name = chat.title
    group_link = f"@{chat.username}" if chat.username else "None"

    await client.send_message(LOG_GROUP_ID, f"""
**KOMUT KULLANILDI**

👤 **Kullanıcı:** {user.mention}
📛 **Kullanıcı Adı:** @{user_name}
🆔 **Kullanıcı İD:** `{user.id}`
🏘️ **Grup Adı:** {group_name}
🤖 **Grup İD:** `{chat.id}`
🔗 **Grup Linki:** {group_link}
🈷️ **Miktar:** {message.text} TL
🔰 **Sonuç:** {result}
💵 **Güncel Bakiye:** `{user_balances[user_id]}` TL
""")


    # Sonucu kullanıcıya bildir
    await message.reply(result_message)




@app.on_message(filters.command("ebakiye") & filters.user(OWNER_ID))
async def add_balance(client: Client, message: Message):
    try:
        amount = int(message.command[1])
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            user_id = int(message.command[2])
    except (IndexError, ValueError):
        await message.reply("__Lütfen geçerli bir miktar ve kullanıcı kimliği girin. Örnek: /ebakiye [Miktar] * [Kullanıcı İD] veya yanıtla. 💵__")
        return
    if amount <= 0:
        await message.reply("__Lütfen pozitif bir miktar girin. 💵__")
        return
    user_balances[user_id] = user_balances.get(user_id, initial_balance) + amount
    save_balance(user_id, user_balances[user_id])
    # Zenginler listesini güncelle
    if user_id not in richest_users and len(richest_users) < 10:
        richest_users.append(user_id)
    richest_users.sort(key=lambda x: user_balances[x], reverse=True)
    save_richest_users()
    user = await client.get_users(user_id)
    await message.reply(f"__`{amount}` TL başarıyla `{user.first_name}` adlı kullanıcıya eklendi. ✅__\n**Güncel bakiyesi: `{user_balances[user_id]}` TL 💰**")
    




# Borç komutu
@app.on_message(filters.command(["borc", "borç"]) & filters.group)
async def lend_money(client: Client, message: Message):   
    if is_user_blocked(message.from_user.id):
        await message.reply("__Üzgünüm, bu komutu kullanma yetkiniz engellendi. 🚫__")
        return

    try:
        amount = int(message.command[1])
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            user_id = int(message.command[2])
    except (IndexError, ValueError):
        await message.reply("__Geçersiz komut kullanımı.🔮 Örnek: /borc [yanıtla] [miktar] 💸__")
        return

    from_user_id = message.from_user.id
    from_user_balance = user_balances.get(from_user_id, 0)
    to_user_balance = user_balances.get(user_id, 0)

    if amount <= 0 or amount > from_user_balance:
        await message.reply("__Yetersiz bakiye. 💸__")
        return

    user_balances[from_user_id] -= amount
    user_balances[user_id] += amount
    save_balance(from_user_id, user_balances[from_user_id])
    save_balance(user_id, user_balances[user_id])

    to_user = await client.get_users(user_id)
    await message.reply(f"__{message.from_user.first_name}, {to_user.first_name} adlı kullanıcıya `{amount}` TL borç verdi. ✅__\n\n**Güncel bakiyeniz: `{user_balances[from_user_id]}` TL 💵**")





@app.on_message(filters.command("bakiye"))
async def check_balance(client: Client, message: Message):
    if is_user_blocked(message.from_user.id):
        await message.reply("__Üzgünüm, bu komutu kullanma yetkiniz engellendi. 🚫__")
        return
    
    
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user = message.reply_to_message.from_user
        user_balance = user_balances.get(replied_user.id, initial_balance)
        await message.reply(f"__{replied_user.mention} kullanıcısının güncel bakiyesi: `{user_balance}` TL 💰__")
    else:
        
        user_id = message.from_user.id
        user_balance = user_balances.get(user_id, initial_balance)
        await message.reply(f"__Güncel bakiyeniz: `{user_balance}` TL 💰__")





# Bakiyeyi sıfırlama komutu
@app.on_message(filters.command("bakiyeres") & filters.user(OWNER_ID))
async def reset_balance(client: Client, message: Message):
    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            user_id = int(message.command[1])
    except (IndexError, ValueError):
        await message.reply("__Geçersiz komut kullanımı. Örnek: /bakiyeres [Kullanıcı İD] veya yanıtla.__")
        return

    if user_id not in user_balances:
        await message.reply("__Belirtilen kullanıcının bakiyesi bulunamadı.__")
        return

    
    user_balances[user_id] = 0
    save_balance(user_id, 0)

    
    if user_id in richest_users:
        richest_users.remove(user_id)
        save_richest_users()

    await message.reply("__Kullanıcının bakiyesi sıfırlandı ve zenginler listesinden kaldırıldı. 💰🔥__")





# Kullanıcıyı engelleme komutu
@app.on_message(filters.command("block") & filters.user(OWNER_ID))
async def block_user_cmd(client: Client, message: Message):
    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            user_id = int(message.command[1])
    except (IndexError, ValueError):
        await message.reply("__Geçersiz komut kullanımı. Örnek: /block [Kullanıcı İD] veya yanıtla.__")
        return

    block_user(user_id)
    await message.reply(f"**Kullanıcı `{user_id}` başarıyla engellendi. 🚫**")







# Kullanıcının engelini kaldırma komutu
@app.on_message(filters.command("unblock") & filters.user(OWNER_ID))
async def unblock_user_cmd(client: Client, message: Message):
    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            user_id = int(message.command[1])
    except (IndexError, ValueError):
        await message.reply("__Geçersiz komut kullanımı. Örnek: /unblock [Kullanıcı İD] veya yanıtla.__")
        return

    unblock_user(user_id)
    await message.reply(f"**Kullanıcı `{user_id}` başarıyla engeli kaldırıldı. ✅**")





# Günlük bonus
@app.on_message(filters.command(["gunluk", "günlük"]) & filters.group)
async def daily_bonus(client: Client, message: Message):
    if is_user_blocked(message.from_user.id):
        await message.reply("__Üzgünüm, bu komutu kullanma yetkiniz engellendi. 🚫__")
        return
        
    try:
        current_time = datetime.now()
        
        
        user_bonus_data = collection.find_one({'user_id': message.from_user.id})
        if user_bonus_data:
            last_bonus_time = user_bonus_data['last_bonus_time']
            last_bonus_time = datetime.fromisoformat(last_bonus_time)
        else:
            last_bonus_time = None
        
        if last_bonus_time:
            
            elapsed_time = current_time - last_bonus_time
            remaining_time = bonus_interval_hours * 3600 - elapsed_time.total_seconds()
            
            if remaining_time > 0:
                minutes_remaining = int(remaining_time // 60)
                hours_remaining = int(minutes_remaining // 60)
                await message.reply(f"__Bu komutu tekrar kullanabilmek için {hours_remaining} saat {minutes_remaining % 60} dakika beklemeniz gerekmektedir. 💫__")
                return

        
        user_id = message.from_user.id
        user_balances[user_id] += 50000
        save_balance(user_id, user_balances[user_id])

        
        if last_bonus_time:
            collection.update_one({'user_id': user_id}, {'$set': {'last_bonus_time': current_time.isoformat()}})
        else:
            collection.insert_one({'user_id': user_id, 'last_bonus_time': current_time.isoformat()})
            
        
        load_richest_users()
        save_richest_users()

        
        user_last_bonus_time[message.from_user.id] = current_time.timestamp()

        
        await message.reply(f"__Günlük bonus aldınız! 🚀 50.000 TL eklendi.😎__\n**Güncel bakiyeniz: `{user_balances[message.from_user.id]}` 💰**")
    except Exception as e:
        await message.reply(f"__⚡️ Günlük bonus verilirken bir hata oluştu.__\n__ℹ️ Bot'a start çektiğinizden emin olun.__")






@app.on_message(filters.new_chat_members)
async def welcome(client: Client, message: Message):
    for member in message.new_chat_members:
        if member.is_self:
            
            groups_collection.update_one(
                {"chat_id": message.chat.id},
                {
                    "$set": {
                        "chat_id": message.chat.id,
                        "chat_name": message.chat.title
                    }
                },
                upsert=True
            )

            
            await client.send_message(LOG_GROUP_ID, f"""
#YENİ GRUBA KATILDIM#

🤖 **Grup Adı:** {message.chat.title}
🆔 **Grup ID:** `{message.chat.id}`
""")






@app.on_message(filters.command("stat") & filters.user(OWNER_ID))
async def stat(client: Client, message: Message):
    user_count = users_collection.count_documents({})
    group_count = groups_collection.count_documents({})
    await message.reply(f"📊 **İstatistikler**\n\n👤 **Kullanıcı Sayısı:** `{user_count}`\n👥 **Grup Sayısı:** `{group_count}`")






@app.on_message(filters.command("duyuru") & filters.user(OWNER_ID))
async def duyuru(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply("Lütfen bir mesajı yanıtlayarak komutu kullanın.")
        return

    duyuru_mesaji = message.reply_to_message
    gruplar = groups_collection.find({})
    kullanicilar = users_collection.find({})
    
    basarili_grup = 0
    basarisiz_grup = 0
    basarili_kullanici = 0
    basarisiz_kullanici = 0

    
    for grup in gruplar:
        try:
            await client.forward_messages(grup["chat_id"], duyuru_mesaji.chat.id, duyuru_mesaji.id)
            basarili_grup += 1
        except Exception as e:
            basarisiz_grup += 1

    
    for kullanici in kullanicilar:
        try:
            await client.forward_messages(kullanici["user_id"], duyuru_mesaji.chat.id, duyuru_mesaji.id)
            basarili_kullanici += 1
        except Exception as e:
            basarisiz_kullanici += 1

    
    await message.reply(f"""**Duyuru başarıyla iletildi:** 📢
    
**Toplam Başarılı Grup:** `{basarili_grup}` - ✅
**Toplam Başarısız Grup:** `{basarisiz_grup}` - ❌
    
**Başarılı Kullanıcılar:** `{basarili_kullanici}` - ✅
**Başarısız Kullanıcılar:** `{basarisiz_kullanici}` - ❌
    """)






@app.on_message(filters.command("blockgrup") & filters.user(OWNER_ID))
async def block_group(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("__Kullanım: /blockgrup <grup_id>__")
        return

    try:
        chat_id = int(message.command[1])
    except ValueError:
        await message.reply_text("__Geçerli bir grup ID'si girin.__")
        return

    # Grubu banla
    groups_collection.update_one({"group_id": chat_id}, {"$set": {"blocked": True}}, upsert=True)
    await message.reply_text(f"__Grup `{chat_id}` banlandı.__")
    
    try:
        await client.leave_chat(chat_id)
    except Exception as e:
        await message.reply_text(f"__Grubu terk ederken hata: {str(e)}__")





@app.on_message(filters.command("unblockgrup") & filters.user(OWNER_ID))
async def unblock_group(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("__Kullanım: /unblockgrup <grup_id>__")
        return

    try:
        chat_id = int(message.command[1])
    except ValueError:
        await message.reply_text("__Geçerli bir grup ID'si girin.__")
        return

    # Grubun banını kaldır
    groups_collection.update_one({"group_id": chat_id}, {"$set": {"blocked": False}}, upsert=True)
    await message.reply_text(f"__Grup `{chat_id}` banı kaldırıldı.__")


@app.on_message(filters.new_chat_members)
async def welcome_new_group(client: Client, message: Message):
    chat_id = message.chat.id
    if groups_collection.find_one({"group_id": chat_id, "blocked": True}):
        await message.reply_text("Bu grup banlandı. Bot gruptan ayrılıyor.")
        await client.leave_chat(chat_id)
    else:
        await message.reply_text("__Merhaba! Slot botunu grubunuza eklediğiniz için teşekkürler. Komutlar için /komutlar yazabilirsiniz.__ 💫")


@app.on_message(filters.command("komutlar") & filters.group)
async def send_commands(client: Client, message: Message):
    await message.reply_text(komutlar)

@app.on_chat_member_updated()
async def monitor_group(client: Client, chat_member_updated: ChatMemberUpdated):
    if chat_member_updated.new_chat_member and chat_member_updated.new_chat_member.user.id == client.me.id:
        chat_id = chat_member_updated.chat.id
        if groups_collection.find_one({"group_id": chat_id, "blocked": True}):
            await client.send_message(chat_id, "__ℹ️ Bu grup banlandı. Eğer bunun bir hata olduğunu düşünüyorsanız t.me/goktuResmi 'ye bildirin.__")
            await client.leave_chat(chat_id)
            


# Gruba giriş mesajı `~~


@app.on_message(filters.new_chat_members, group=1)
async def hg(bot: Client, msg: Message):
    for new_user in msg.new_chat_members:
        if str(new_user.id) == str(BOT_ID):
            await msg.reply(
                f"""**📖 Hey , {msg.from_user.mention}\nMerhaba! Slot botunu grubunuza eklediğiniz için teşekkürler. Komutlar için /komutlar yazabilirsiniz**""",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "⚙️ Daha Fazla Bilgi",
                                url=f"https://t.me/{app.me.username}?start",
                            )
                        ]
                    ]
                ),
            )
        elif str(new_user.id) == str(OWNER_ID):
            await msg.reply(f"{new_user.mention} ⚡️🫡\n\n🇹🇷 ʙᴏᴛᴜɴ sᴀʜɪʙɪ ɢʀᴜʙᴜɴᴜᴢᴀ ᴋᴀᴛɪʟᴅɪ !")
        

# Günlük bonus
async def daily_bonus():
    while True:
        try:
            for user_id in user_balances:
                user_balances[user_id] += 10000
            await asyncio.sleep(24 * 3600)  # 24 saat bekle
        except Exception as e:
            print(f"Günlük bonus alınırken hata oluştu: {e}")



# Günlük bonusu başlat
asyncio.ensure_future(daily_bonus())

# Botu başlat
app.run()
print("Bot Çalışıyor :)!")
