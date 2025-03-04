import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

TOKEN = 'TOKEN BURAYA'

# API URLLERİ BURAYA DAHA DÜZENLİ YANIT İÇİN GELİŞTİRİRSİNZ SADECE APİ YANITINI ATAR
API_URLS = {
"TC": "http://api.sowixfree.xyz/sowixapi/tc.php?tc=",
"Aile": "http://api.sowixfree.xyz/sowixapi/aile.php?tc=",
"Sulale": "http://api.sowixfree.xyz/sowixapi/sulale.php?tc=",
"Tc GSM": "http://api.sowixfree.xyz/sowixapi/tcgsm.php?tc=",
"GSM TC": "http://api.sowixfree.xyz/sowixapi/gsm.php?gsm=",
"TC Pro": "http://api.sowixfree.xyz/sowixapi/tcpro.php?tc=",
"Telegram Sorgu API": "http://api.sowixfree.xyz/sowixapi/telegram_sorgu.php?username=",
"Okul No API": "http://api.sowixfree.xyz/sowixapi/okulno.php?tc=",
"Tapu API": "http://api.sowixfree.xyz/sowixapi/tapu.php?tc=",
"İş Yeri API": "http://api.sowixfree.xyz/sowixapi/isyeri.php?tc=",
"GSM Detay API": "http://api.sowixfree.xyz/sowixapi/gsmdetay.php?gsm=",
"Baba Sorgu API": "http://api.sowixfree.xyz/sowixapi/baba.php?tc=",
"Anne Sorgu API": "http://api.sowixfree.xyz/sowixapi/anne.php?tc=",
"Ad Soyad": "https://api.sowixfree.xyz/sowixapi/adsoyadilice.php?ad=roket&soyad=atar",
"Ad Soyad İl": "https://api.sowixfree.xyz/sowixapi/adsoyadilice.php?ad=roket&soyad=atar&il=bursa",
"Ad Soyad İl İlçe": "https://api.sowixfree.xyz/sowixapi/adsoyadilice.php?ad=roket&soyad=atar&il=bursa",
"Adres": "http://api.sowixfree.xyz/sowixapi/adres.php?tc=",
}

# Hoş geldin mesajı burada düzenlersin
WELCOME_MESSAGE = (
"Merhaba! @che 🌟\n\n"
"Benimle çeşitli sorgular yapabilirsiniz. Aşağıdaki seçeneklerden birini seçin ve gerekli bilgileri girin:\n\n"
"Başlamak için lütfen bir seçenek belirleyin! 🇹🇷"
)

async def start(update: Update, context: CallbackContext):
keyboard = [
[InlineKeyboardButton("📋 TC Sorgula", callback_data='TC')],
[InlineKeyboardButton("👪 Aile Bilgileri", callback_data='Aile')],
[InlineKeyboardButton("🌳 Sulale", callback_data='Sulale')],
[InlineKeyboardButton("📱 TC GSM", callback_data='Tc GSM')],
[InlineKeyboardButton("📞 GSM TC", callback_data='GSM TC')],
[InlineKeyboardButton("🔑 TC Pro", callback_data='TC Pro')],
[InlineKeyboardButton("🏦Telegram Sorgu API ", callback_data='Telegram Sorgu API')],
[InlineKeyboardButton("💼 Okul No API", callback_data='Okul No API')],
[InlineKeyboardButton("📞 Tapu API", callback_data='Tapu API')],
[InlineKeyboardButton("🔢 İş Yeri API", callback_data='İş Yeri API')],
[InlineKeyboardButton("📜 GSM Detay API", callback_data='GSM Detay API')],
[InlineKeyboardButton("📲 Baba Sorgu API", callback_data='Baba Sorgu API')],
[InlineKeyboardButton("👣 Anne Sorgu API", callback_data='Anne Sorgu API')],
[InlineKeyboardButton("📝 Ad Soyad", callback_data='Ad Soyad')],
[InlineKeyboardButton("📍 Ad Soyad İl", callback_data='Ad Soyad İl')],
[InlineKeyboardButton("📍 Ad Soyad İl İlçe", callback_data='Ad Soyad İl İlçe')],
InlineKeyboardButton("🏠 Adres", callback_data='Adres')],
]
return
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text(WELCOME_MESSAGE, reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext):
query = update.callback_query
await query.answer()
data = query.data

await query.edit_message_text(text=f"{data} sorgusu yapmak için gerekli bilgileri girin.")
context.user_data['current_query'] = data

async def handle_message(update: Update, context: CallbackContext):
text = update.message.text
query_type = context.user_data.get('current_query')

if not query_type:
await update.message.reply_text("Önce bir sorgu seçmelisiniz. /start komutunu kullanın.")
return

params = {}
if query_type == "Ad Soyad":
parts = text.split(' ')
if len(parts) &lt; 2:
await update.message.reply_text("Ad ve soyadı doğru formatta girin: Ad Soyad")
return
params = {"ad": parts[0], "soyad": parts[1]}
elif query_type == "Ad Soyad İl":
parts = text.split(' ')
if len(parts) &lt; 3:
await update.message.reply_text("Ad, soyad ve il bilgisini doğru formatta girin: Ad Soyad İl")
return
params = {"ad": parts[0], "soyad": parts[1], "il": parts[2]}
elif query_type == "Ad Soyad İl İlçe":
parts = text.split(' ')
if len(parts) &lt; 4:
await update.message.reply_text("Ad, soyad, il ve ilçe bilgisini doğru formatta girin: Ad Soyad İl İlçe")
return
params = {"ad": parts[0], "soyad": parts[1], "il": parts[2], "ilce": parts[3]}
else:
if query_type in ["GSM TC", "Operatör"]:
params = {"gsm": text}
else:
params = {"tc": text}

api_url = API_URLS.get(query_type).format(**params)
response = requests.get(api_url)
result = response.json()

await update.message.reply_text(f"API yanıtı:\n{result}")

def main():
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))
application.add_handler(MessageHandler(filters.TEXT &amp; ~filters.COMMAND, handle_message))

application.run_polling()

if __name__ == 'main()< 2:'
main() < 2:
            await update.message.reply_text("Ad ve soyadı doğru formatta girin: Ad Soyad")
            return
        params = {"ad": parts[0], "soyad": parts[1]}
    elif query_type == "Ad Soyad İl":
        parts = text.split(' ')
        if len(parts) < 3:
            await update.message.reply_text("Ad, soyad ve il bilgisini doğru formatta girin: Ad Soyad İl")
            return
        params = {"ad": parts[0], "soyad": parts[1], "il": parts[2]}
    elif query_type == "Ad Soyad İl İlçe":
        parts = text.split(' ')
        if len(parts) < 4:
            await update.message.reply_text("Ad, soyad, il ve ilçe bilgisini doğru formatta girin: Ad Soyad İl İlçe")
            return
        params = {"ad": parts[0], "soyad": parts[1], "il": parts[2], "ilce": parts[3]}
    else:
        if query_type in ["GSM TC", "Operatör"]:
            params = {"gsm": text}
        else:
            params = {"tc": text}

    api_url = API_URLS.get(query_type).format(**params)
    response = requests.get(api_url)
    result = response.json()
    
    await update.message.reply_text(f"API yanıtı:\n{result}")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
