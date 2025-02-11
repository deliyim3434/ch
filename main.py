import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

token = '7773120207:AAFlvOOUknaXWDTh130is7SXL4fjBYAzr-Q'

bot = telebot.TeleBot(token)

GROUP_CHAT_ID = -1002337387015

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    
    if not is_user_in_group(user_id):
        welcome_text = f"Merhaba {user_name},\n\nBeni Kullanabilmek İçin Destek kanalına Katılman Lazım. Katılıp Tekrar Deneyin!"
        join_button = InlineKeyboardButton("Kanala Katıl", url="https://t.me/DiyarbakirSohbetGrubu21")
        markup = InlineKeyboardMarkup().add(join_button)
        bot.send_message(user_id, welcome_text, reply_markup=markup)
    else:
        start_text = (
            f"Merhaba {user_name},\n\n"
            "Jesus Veri Analiz Sorgu Botuna Hoş Geldin!\n\n"
            "Benim Sayemde Ücretsiz Sorgu Atıp Veri Analiz İşlemi Gerçekleştirebilirsiniz.\n\n"
            "Herhangi Sorunuz/Sorununuz Olur İse [Destek Grubumuza](https://t.me/DiyarbakirSohbetGrubu21) Gelebilirsiniz."
        )
        commands_button = InlineKeyboardButton("🤡 Komutlar", callback_data="commands")
        markup = InlineKeyboardMarkup().add(commands_button)
        bot.send_message(user_id, start_text, reply_markup=markup, parse_mode="Markdown")

@bot.inline_handler(lambda query: True)
def handle_inline_query(query):
    user_id = query.from_user.id
    if query.query == "commands":
        commands_text = "Jesus Komutları:\n\n/tc - TC Sorgu İşlemi\n\n/tcgsm - TC Den GSM İşlemi\n\n/gsmtc - GSM Den TC İşlemi \n\n/aile - Aile Sorgu İşlemi \n\n/sorgu -isim * -soyisim * -il * | Ad Soyad Sorgu İşlemi\n\n/serino - Seri No Sorgu İşlemi\n\nDestek Ve Yardım İçin Grubumuza Gelebilirsiniz: @Majestesohbet"
        back_button = InlineKeyboardButton("Geri", switch_inline_query_current_chat="")
        markup = InlineKeyboardMarkup().add(back_button)
        result = [telebot.types.InlineQueryResultArticle('1', 'commands', telebot.types.InputTextMessageContent(commands_text, parse_mode="Markdown"), reply_markup=markup)]
        bot.answer_inline_query(query.id, result)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name 
    message_id = call.message.message_id
    if call.data == "commands":
        commands_text = "Jesus Komutları:\n\n/tc - TC Sorgu İşlemi\n\n/tcgsm - TC Den GSM İşlemi\n\n/gsmtc - GSM Den TC İşlemi \n\n/aile - Aile Sorgu İşlemi \n\n/sorgu -isim * -soyisim * -il * | Ad Soyad Sorgu İşlemi\n\n/serino - seri no sorgu işlemi\n\nDestek Ve Yardım İçin Grubumuza Gelebilirsiniz: @Majestesohbet"
        back_button = InlineKeyboardButton("Geri", callback_data="back")
        markup = InlineKeyboardMarkup().add(back_button)
        bot.edit_message_text(commands_text, user_id, message_id, reply_markup=markup)
    elif call.data == "back":
        start_text = (
            f"Merhaba {user_name},\n\n" 
            "Jesus Veri Analiz Sorgu Botuna Hoş Geldin!\n\n"
            "Benim Sayemde Ücretsiz Sorgu Atıp Veri Analiz İşlemi Gerçekleştirebilirsiniz.\n\n"
            "Herhangi Sorunuz/Sorununuz Olur İse Destek Grubumuza Gelebilirsiniz."
        )
        commands_button = InlineKeyboardButton("Komutlar", callback_data="commands")
        markup = InlineKeyboardMarkup().add(commands_button)
        bot.edit_message_text(start_text, user_id, message_id, reply_markup=markup, parse_mode="Markdown")

def is_user_in_group(user_id):
    try:
        chat_member = bot.get_chat_member(GROUP_CHAT_ID, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except telebot.apihelper.ApiException as e:
        return False

TCGSM_API = "http://api.sowixvip.xyz/sowixapi/tcgsm.php?tc="

@bot.message_handler(commands=['tcgsm'])
def handle_tcgsm(message):
    try:
        
        tc_number = message.text.split()[1]

        
        api_response = requests.get(TCGSM_API + tc_number).json()

        
        if api_response.get("success") == "true" and api_response.get("number") > 0:
            data = api_response.get("data")[0]
            gsm = data.get("GSM")
            tc = data.get("TC")

            
            result_text = f"╭━━━━━━━━━━━━━╮\n┃➥ GSM: {gsm}\n┃➥ TC: {tc}\n╰━━━━━━━━━━━━━╯"
            bot.send_message(message.chat.id, result_text)
        else:
            bot.send_message(message.chat.id, "Data bulunamadı.")
    except IndexError:
        bot.send_message(message.chat.id, "Lütfen geçerli bir TC numarası girin.")

GSRTC_API = "http://api.sowixvip.xyz/sowixapi/gsm.php?gsm="


@bot.message_handler(commands=['gsmtc'])
def handle_gsmtc(message):
    try:
        # Extract GSM number from the command
        gsm_number = message.text.split()[1]

        
        api_response = requests.get(GSRTC_API + gsm_number).json()

        
        if api_response.get("success") == "true" and api_response.get("number") > 0:
            data = api_response.get("data")
            
            
            result_text = "╭━━━━━━━━━━━━━╮\n"
            for entry in data:
                tc = entry.get("TC")
                gsm = entry.get("GSM")
                result_text += f"┃➥ GSM: {gsm}\n┃➥ TC: {tc}\n╰━━━━━━━━━━━━━╯\n"

            
            bot.send_message(message.chat.id, result_text)
        else:
            bot.send_message(message.chat.id, "Data bulunamadı.")
    except IndexError:
        bot.send_message(message.chat.id, "Lütfen geçerli bir GSM numarası girin Başında 0 Olmadan.")

TC_API = "http://api.sowixvip.xyz/sowixapi/tc.php?tc="

@bot.message_handler(commands=['tc'])
def handle_tc_command(message):
    try:
        
        tc = message.text.split()[1]
        
        
        api_response = requests.get(TC_API + tc).json()

        
        adi = api_response.get("ADI", "")
        soyadi = api_response.get("SOYADI", "")
        dogum_tarihi = api_response.get("DOĞUMTARIHI", "")
        il = api_response.get("NUFUSIL", "")
        ilce = api_response.get("NUFUSILCE", "")
        anne_adi = api_response.get("ANNEADI", "")
        anne_tc = api_response.get("ANNETC", "")
        baba_adi = api_response.get("BABAADI", "")
        baba_tc = api_response.get("BABATC", "")
        yas = api_response.get("YAŞ", "")

        
        response_text = (
            f"╭━━━━━━━━━━━━━╮\n"
            f"┃➥ @che\n"
            f"╰━━━━━━━━━━━━━╯\n"
            f"\n"
            f"╭━━━━━━━━━━━━━━\n"
            f"┃➥TC: {tc}\n"
            f"┃➥ ADI: {adi}\n"
            f"┃➥ SOY ADI: {soyadi}\n"
            f"┃➥ DOĞUM TARİHİ: {dogum_tarihi}\n"
            f"┃➥ İL: {il}\n"
            f"┃➥ İLÇE: {ilce}\n"
            f"┃➥ ANNE ADI: {anne_adi}\n"
            f"┃➥ ANNE TC: {anne_tc}\n"
            f"┃➥ BABA ADI: {baba_adi}\n"
            f"┃➥ BABA TC: {baba_tc}\n"
            f"┃➥ YAŞ: {yas}\n"
            f"╰━━━━━━━━━━━━━━"
        )

        
        bot.reply_to(message, response_text)

    except IndexError:
        bot.reply_to(message, "Geçerli Bir TC Kimlik Numarası Girin.")
    except Exception as e:
        bot.reply_to(message, f"HATA: {str(e)}")


AILE_API = "http://api.sowixvip.xyz/sowixapi/aile.php?tc="

@bot.message_handler(commands=['aile'])
def handle_aile_command(message):
    try:
        
        tc = message.text.split()[1]
        
        
        api_response = requests.get(AILE_API + tc).json()

        
        user_info = api_response.get("data", [])

        
        response_text = (
            f"╭━━━━━━━━━━━━━╮\n"
            f"┃➥ @che\n"
            f"╰━━━━━━━━━━━━━╯"
        )

        for info in user_info:
            response_text += (
                f"\n"
                f"╭━━━━━━━━━━━━━━\n"
                f"┃➥ TC: {info['TC']}\n"
                f"┃➥ ADI: {info['ADI']}\n"
                f"┃➥ SOY ADI: {info['SOYADI']}\n"
                f"┃➥ DOĞUM TARİHİ: {info['DOGUMTARIHI']}\n"
                f"┃➥ İL: {info['NUFUSIL']}\n"
                f"┃➥ İLÇE: {info['NUFUSILCE']}\n"
                f"┃➥ ANNE ADI: {info['ANNEADI']}\n"
                f"┃➥ ANNE TC: {info['ANNETC']}\n"
                f"┃➥ BABA ADI: {info['BABAADI']}\n"
                f"┃➥ BABA TC: {info['BABATC']}\n"
                f"┃➥ UYRUK: {info['UYRUK']}\n"
                f"┃➥ YAKINLIK: {info['Yakinlik']}\n"
                f"╰━━━━━━━━━━━━━━"
            )

        
        bot.reply_to(message, response_text)

    except IndexError:
        bot.reply_to(message, "Lütfen geçerli bir TC kimlik numarası girin.")
    except Exception as e:
        bot.reply_to(message, f"HATA: {str(e)}")


api_base_url = 'https://api.sowixvip.xyz/sowixapi/adsoyadilice.php?ad=roket&soyad=atar'


@bot.message_handler(commands=['sorgu'])
def handle_sorgu(message):
    try:
        
        command_args = message.text.split()
        isim_index = command_args.index('-isim') + 1
        soyisim_index = command_args.index('-soyisim') + 1

        isim = command_args[isim_index]
        soyisim = command_args[soyisim_index]

        
        if '-il' in command_args:
            il_index = command_args.index('-il') + 1
            il = command_args[il_index]
            api_url = f'{api_base_url}ad={isim}&soyad={soyisim}&il={il}'
        else:
            api_url = f'{api_base_url}ad={isim}&soyad={soyisim}'

        
        api_response = requests.get(api_url).json()

        
        if api_response.get("success", "").lower() == "true" and api_response.get("number", 0) > 0:
            
            if os.path.exists('sonuclar.txt'):
                os.remove('sonuclar.txt')

            
            with open('sonuclar.txt', 'a') as file:
                for api_data in api_response.get("data", []):
                    response_text = create_response_text(api_data)
                    file.write(response_text + '\n\n')

            
            bot.send_document(message.chat.id, open('sonuclar.txt', 'rb'))

        else:
            bot.reply_to(message, 'Data Bulunmadı.')

    except Exception as e:
        print(e)
        bot.reply_to(message, 'Sorgu Başarısız Oldu')


def create_response_text(api_data):
    response_text = (
        f"╭━━━━━━━━━━━━━╮\n"
        f"┃➥ @che\n"
        f"╰━━━━━━━━━━━━━╯\n"
        f"\n"
        f"╭━━━━━━━━━━━━━━\n"
        f"┃➥TC: {api_data.get('TC', '')}\n"
        f"┃➥ ADI: {api_data.get('ADI', '')}\n"
        f"┃➥ SOY ADI: {api_data.get('SOYADI', '')}\n"
        f"┃➥ DOĞUM TARİHİ: {api_data.get('DOGUMTARIHI', '')}\n"
        f"┃➥ İL: {api_data.get('NUFUSIL', '')}\n"
        f"┃➥ İLÇE: {api_data.get('NUFUSILCE', '')}\n"
        f"┃➥ ANNE ADI: {api_data.get('ANNEADI', '')}\n"
        f"┃➥ ANNE TC: {api_data.get('ANNETC', '')}\n"
        f"┃➥ BABA ADI: {api_data.get('BABAADI', '')}\n"
        f"┃➥ BABA TC: {api_data.get('BABATC', '')}\n"
        f"┃➥ UYRUK: {api_data.get('UYRUK', '')}\n"
        f"╰━━━━━━━━━━━━━━"
    )

    return response_text


serino_api_base_url = 'http://20.208.139.30/serino.php?'


@bot.message_handler(commands=['serino'])
def handle_serino(message):
    try:
        
        command_args = message.text.split()
        tc = command_args[1]

        
        api_url = f'{serino_api_base_url}tc={tc}'
        api_response = requests.get(api_url).json()

        
        if api_response.get("success", False):
            
            response_text = create_serino_response_text(api_response)

            
            bot.send_message(message.chat.id, response_text)

        else:
            bot.reply_to(message, 'Sonuç Bulunmadı')

    except Exception as e:
        print(e)
        bot.reply_to(message, 'Sorgu işlemi başarısız.')


def create_serino_response_text(api_response):
    response_text = (
        f"╭━━━━━━━━━━━━━╮\n"
        f"┃➥ S.NO: {api_response.get('SeriNo', '')}\n"
        f"┃➥ TC: {api_response.get('TcKimlikNo', '')}\n"
        f"╰━━━━━━━━━━━━━╯"
    )

    return response_text

    try:
    bot.polling(none_stop=True)
except Exception as e:
    print(f"Hata: {e}")
