
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

TOKEN = '7773120207:AAFlvOOUknaXWDTh130is7SXL4fjBYAzr-Q'

# API URLLERİ BURAYA DAHA DÜZENLİ YANIT İÇİN GELİŞTİRİRSİNZ SADECE APİ YANITINI ATAR
API_URLS = {
"TC": "http://api.sowixvip.xyz/sowixapi/tc.php?tc=",
"Aile": "http://api.sowixvip.xyz/sowixapi/aile.php?tc=",
"Sulale": "http://api.sowixvip.xyz/sowixapi/sulale.php?tc=",
"Tc_GSM": "http://api.sowixvip.xyz/sowixapi/tcgsm.php?tc=",
"GSM_TC": "http://api.sowixvip.xyz/sowixapi/gsm.php?gsm=",
"TC_Pro": "http://api.sowixvip.xyz/sowixapi/tc.php?tc=",
"Ad_Soyad": "https://api.sowixvip.xyz/sowixapi/adsoyadilice.php?ad=roket&soyad=atar",
"Ad_Soyad_İl": "https://api.sowixvip.xyz/sowixapi/adsoyadilice.php?ad=roket&soyad=atar&il=bursa",
"Ad_Soyad_İl_İlçe": "https://api.sowixvip.xyz/sowixapi/adsoyadilice.php?ad=roket&soyad=atar&il=bursa",
"Adres": "http://api.sowixvip.xyz/sowixapi/adres.php?tc=",
}

# Hoş geldin mesajı burada düzenlersin
WELCOME_MESSAGE = (
"""Merhaba! 🌟
Benimle çeşitli sorgular yapabilirsiniz. Aşağıdaki seçeneklerden birini seçin ve gerekli bilgileri girin
Başlamak için lütfen bir seçenek belirleyin! 🇹🇷"""
)

async def start(update: Update, context: CallbackContext):
keyboard = [
[InlineKeyboardButton("📋 TC Sorgula", callback_data='TC')],
[InlineKeyboardButton("👪 Aile Bilgileri", callback_data='Aile')],
[InlineKeyboardButton("🌳 Sulale", callback_data='Sulale')],
[InlineKeyboardButton("📱 TC GSM", callback_data='Tc_GSM')],
[InlineKeyboardButton("📞 GSM TC", callback_data='GSM_TC')],
[InlineKeyboardButton("🔑 TC Pro", callback_data='TC_Pro')],
[InlineKeyboardButton("📝 Ad Soyad", callback_data='Ad_Soyad')],
[InlineKeyboardButton("📍 Ad Soyad İl", callback_data='Ad_Soyad_İl')],
[InlineKeyboardButton("📍 Ad Soyad İl İlçe", callback_data='Ad_Soyad_İl_İlçe')],
[InlineKeyboardButton("🏠 Adres", callback_data='Adres')],
]
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
if query_type == "Ad_Soyad":
parts = text.split(' ')
if len(parts) &lt; 2:
await update.message.reply_text("Ad ve soyadı doğru formatta girin: Ad Soyad")
return
params = {"ad": parts[0], "soyad": parts[1]}
elif query_type == "Ad_Soyad_İl":
parts = text.split(' ')
if len(parts) &lt; 3:
await update.message.reply_text("Ad, soyad ve il bilgisini doğru formatta girin: Ad Soyad İl")
return
params = {"ad": parts[0], "soyad": parts[1], "il": parts[2]}
elif query_type == "Ad_Soyad_İl_İlçe":
parts = text.split(' ')
if len(parts) &lt; 4:
await update.message.reply_text("Ad, soyad, il ve ilçe bilgisini doğru formatta girin: Ad Soyad İl İlçe")
return
params = {"ad": parts[0], "soyad": parts[1], "il": parts[2], "ilce": parts[3]}
else:
if query_type in ["GSM_TC", "Operatör"]:
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

if __name__ == '__main__':
main()(arts) < 2:
            await update.message.reply_text("Ad ve soyadı doğru formatta girin: Ad Soyad")
            return
        params = {"ad": parts[0], "soyad": parts[1]}
    elif query_type == "Ad_Soyad_İl":
        parts = text.split(' ')
        if len(parts) < 3:
            await update.message.reply_text("Ad, soyad ve il bilgisini doğru formatta girin: Ad Soyad İl")
            return
        params = {"ad": parts[0], "soyad": parts[1], "il": parts[2]}
    elif query_type == "Ad_Soyad_İl_İlçe":
        parts = text.split(' ')
        if len(parts) < 4:
            await update.message.reply_text("Ad, soyad, il ve ilçe bilgisini doğru formatta girin: Ad Soyad İl İlçe")
            return
        params = {"ad": parts[0], "soyad": parts[1], "il": parts[2], "ilce": parts[3]}
    else:
        if query_type in ["GSM_TC", "Operatör"]:
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
