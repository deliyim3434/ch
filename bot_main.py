import telebot
import requests

TOKEN = "7519134899:AAHf8pLSgqwxuhV49moMwpBMyqhD53Y9PPI"
bot = telebot.TeleBot(TOKEN)

user_reports = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "🔹 Merhaba! Şikayet etmek istediğiniz kullanıcının kullanıcı adını gönderin (örn: @kullanici_adi)")
    bot.register_next_step_handler(message, get_username)

def get_username(message):
    username = message.text.strip()
    if not username.startswith('@'):
        bot.send_message(message.chat.id, "⚠️ Lütfen geçerli bir Telegram kullanıcı adı girin (örn: @username)")
        return
    
    user_reports[message.chat.id] = {'username': username}
    bot.send_message(message.chat.id, "📌 Şikayet sebebinizi yazın (örn: Dolandırıcılık, Spam, Sahte hesap vb.)")
    bot.register_next_step_handler(message, get_reason)

def get_reason(message):
    reason = message.text.strip()
    user_reports[message.chat.id]['reason'] = reason
    username = user_reports[message.chat.id]['username']
    
    report_data = {
        'message': f'Bu kullanıcı ({username}) spam veya dolandırıcılık yapıyor: {reason}',
        'email': 'ali3421@gmail.com',  # istediğin maili gir annesiz
        'phone': '+1234567890'  # fake no gir orospu evladi 
    }
    
    response = requests.post('https://telegram.org/support?setln=tr', data=report_data)
    
    if response.status_code == 200:
        bot.send_message(message.chat.id, f"✅ Şikayetiniz başarıyla gönderildi!\n🔹 Şikayet Edilen Kullanıcı: {username}\n📌 Sebep: {reason}\n🔗 Telegram Destek Ekibi en kısa sürede inceleyecektir.")
    else:
        bot.send_message(message.chat.id, "❌ Şikayet gönderme işlemi başarısız oldu, lütfen manuel olarak iletin.")

bot.polling(none_stop=True)
