import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta

API_TOKEN = '8133504850:AAFki7MS45X9A7RSvFUR1V0JYi_iEWyb9_U'
bot = telebot.TeleBot(API_TOKEN)

conn = sqlite3.connect('message_counts.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                    user_id INTEGER, 
                    group_id INTEGER, 
                    count INTEGER, 
                    date TIMESTAMP
                 )''')

def increment_message_count(user_id, group_id):
    now = datetime.utcnow()
    date_str = now.date().isoformat()
    
    cursor.execute('''INSERT INTO messages (user_id, group_id, count, date) 
                      VALUES (?, ?, 1, ?) 
                      ON CONFLICT(user_id, group_id, date) 
                      DO UPDATE SET count = count + 1 
                      WHERE user_id = ? AND group_id = ? AND date = ?''',
                   (user_id, group_id, date_str, user_id, group_id, date_str))
    conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Merhaba! Mesajları saymaya başladım.')

@bot.message_handler(commands=['mesaj'])
def send_message_stats(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Günlük Konuşanlar', callback_data='daily'))
    markup.add(types.InlineKeyboardButton('Haftalık Konuşanlar', callback_data='weekly'))
    markup.add(types.InlineKeyboardButton('Aylık Konuşanlar', callback_data='monthly'))
    bot.send_message(message.chat.id, 'Hangi dönemin konuşanlarını görmek istiyorsunuz?', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'daily':
        period = 1
        period_text = 'günlük'
    elif call.data == 'weekly':
        period = 7
        period_text = 'haftalık'
    elif call.data == 'monthly':
        period = 30
        period_text = 'aylık'
    else:
        bot.answer_callback_query(call.id, 'Geçersiz seçim.')
        return

    group_id = call.message.chat.id
    now = datetime.utcnow()
    start_date = (now - timedelta(days=period)).date().isoformat()
    
    cursor.execute('''SELECT user_id, SUM(count) as total 
                      FROM messages 
                      WHERE group_id = ? AND date >= ? 
                      GROUP BY user_id 
                      ORDER BY total DESC 
                      LIMIT 10''', (group_id, start_date))
    
    results = cursor.fetchall()
    if results:
        response = f'{period_text} en çok mesaj atan kullanıcılar:\n\n'
        for user_id, total in results:
            response += f'Kullanıcı {user_id}: {total} mesaj\n'
    else:
        response = f'Bu dönemde mesaj atan kullanıcı yok.'

    bot.send_message(call.message.chat.id, response)
    bot.answer_callback_query(call.id, 'Seçiminiz işlendi.')

@bot.message_handler(func=lambda message: True)
def count_messages(message):
    user_id = message.from_user.id
    group_id = message.chat.id
    increment_message_count(user_id, group_id)

try:
    bot.polling()
except Exception as e:
    print(f"Hata oluştu: {e}")
