import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '8170723295:AAE05oQ0Aeep7eQ34hrTwNxLL0aw8Zl_u_Y'

API_URLS = {
    "TC": "http://api.sowixvip.xyz/sowixapi/tc.php?tc={tc}",
    "Aile": "http://api.sowixvip.xyz/sowixapi/aile.php?tc={tc}",
    "Sulale": "http://api.sowixvip.xyz/sowixapi/sulale.php?tc={tc}",
    "Tc_GSM": "http://api.sowixvip.xyz/sowixapi/tcgsm.php?tc={tc}",
    "GSM_TC": "http://api.sowixvip.xyz/sowixapi/gsm.php?gsm={gsm}",
    "TC_Pro": "http://api.sowixvip.xyz/sowixapi/tc.php?tc={tc}",
    "Ad_Soyad": "https://api.sowixvip.xyz/sowixapi/adsoyadilice.php?ad={ad}&soyad={soyad}",
    "Ad_Soyad_İl": "https://api.sowixvip.xyz/sowixapi/adsoyadilice.php?ad={ad}&soyad={soyad}&il={il}",
    "Ad_Soyad_İl_İlçe": "https://api.sowixvip.xyz/sowixapi/adsoyadilice.php?ad={ad}&soyad={soyad}&il={il}&ilce={ilce}",
    "Adres": "https://sowixfree.xyz/sowixapi/adres.php.?tc={tc}",
}

WELCOME_MESSAGE = """
Merhaba! 🌟
Benimle çeşitli sorgular yapabilirsiniz. Aşağıdaki seçeneklerden birini seçin ve gerekli bilgileri girin.
Başlamak için lütfen bir seçenek belirleyin! 🇹🇷
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    
    context.user_data['current_query'] = data
    await query.edit_message_text(text=f"{data} sorgusu yapmak için gerekli bilgileri girin.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        text = update.message.text
        query_type = context.user_data.get('current_query')

        if not query_type:
            await update.message.reply_text("Önce bir sorgu seçmelisiniz. /start komutunu kullanın.")
            return

        params = {}
        if query_type == "Ad_Soyad":
            parts = text.split()
            if len(parts) < 2:
                await update.message.reply_text("Ad ve soyadı doğru formatta girin: Ad Soyad")
                return
            params = {"ad": parts[0], "soyad": parts[1]}
        
        elif query_type == "Ad_Soyad_İl":
            parts = text.split()
            if len(parts) < 3:
                await update.message.reply_text("Ad, soyad ve il bilgisini doğru formatta girin: Ad Soyad İl")
                return
            params = {"ad": parts[0], "soyad": parts[1], "il": parts[2]}
        
        elif query_type == "Ad_Soyad_İl_İlçe":
            parts = text.split()
            if len(parts) < 4:
                await update.message.reply_text("Ad, soyad, il ve ilçe bilgisini doğru formatta girin: Ad Soyad İl İlçe")
                return
            params = {"ad": parts[0], "soyad": parts[1], "il": parts[2], "ilce": parts[3]}
        
        elif query_type in ["GSM_TC", "Operatör"]:
            params = {"gsm": text}
        
        else:
            params = {"tc": text}

        api_url = API_URLS[query_type].format(**params)
        response = requests.get(api_url)
        response.raise_for_status()
        result = response.json()

        formatted_result = f"🔍 Sorgu Sonucu:\n\n{result}"
        await update.message.reply_text(formatted_result)

    except requests.RequestException as e:
        logger.error(f"API hatası: {e}")
        await update.message.reply_text("API'ye erişirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.")
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
        await update.message.reply_text("İşlem sırasında bir hata oluştu. Lütfen tekrar deneyin.")

def main() -> None:
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot başlatılıyor...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
