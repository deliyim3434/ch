from pyrogram import Client, filters
from config import Config
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

bot = Client(
    "my_bot",
    api_id= 25504446
    api_hash= "47db27cde56c3e4690e244e6de10f919"
    bot_token= "7940182890:AAFpu-UoIxGYaCIUrzwO9D6hdE403LNaKuA"
)

def log_removed_user(user_id, username):
    with open('remove.txt', 'a') as f:
        f.write(f'Removed user ID: {user_id} @{username}\n')

async def remove_members(chat_id):
    try:
        async for member in bot.get_chat_members(chat_id):
            if not member.user.is_bot:
                try:
                    await bot.ban_chat_member(chat_id=chat_id, user_id=member.user.id)
                    logging.info(f"Banned {member.user.id} from chat {chat_id}")
                    username = member.user.username if member.user.username else "NoUsername"
                    log_removed_user(member.user.id, username)
                except Exception as e:
                    logging.error(f"Failed to ban member {member.user.id}: {e}")
    except Exception as e:
        logging.error(f"Failed to retrieve members from chat {chat_id}: {e}")

@bot.on_message(filters.group)
async def handle_message(client, message):
    try:
        logging.info(f"New message in chat {message.chat.id}")
        logging.info(f"Attempting to remove non-bot members from chat {message.chat.id}")
        
        # Call the function to remove members
        await remove_members(message.chat.id)
        
        logging.info("Process completed")
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    bot.run()
