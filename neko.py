import os
import asyncio
import nest_asyncio
import logging
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from process_command import process_command
from command.help import handle_help_callback
from command.mailtools import mail_query
from cmd_list import lista_cmd
from data.stickers import saludos, STICKER_SALUDO, STICKER_DESCANSO, STICKER_REACTIVADO
from data.vars import (
    api_id, api_hash, bot_token, admin_users, users, temp_users,
    temp_chats, vip_users, ban_users, MAIN_ADMIN, CODEWORD,
    BOT_IS_PUBLIC, PROTECT_CONTENT, allowed_ids, allowed_users
)

nest_asyncio.apply()
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

bot_is_sleeping = False
sleep_duration = 0
start_sleep_time = 0

def is_bot_public():
    return BOT_IS_PUBLIC

def format_time(seconds):
    years = seconds // (365 * 24 * 3600)
    days = (seconds % (365 * 24 * 3600)) // (24 * 3600)
    hours = (seconds % (24 * 3600)) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    result = []
    if years: result.append(f"{years} año" if years == 1 else f"{years} años")
    if days: result.append(f"{days} día" if days == 1 else f"{days} días")
    if hours: result.append(f"{hours} hora" if hours == 1 else f"{hours} horas")
    if minutes: result.append(f"{minutes} minuto" if minutes == 1 else f"{minutes} minutos")
    if seconds: result.append(f"{seconds} segundo" if seconds == 1 else f"{seconds} segundos")
    return ", ".join(result)

async def process_access_command(message):
    user_id = message.from_user.id
    if len(message.command) > 1 and message.command[1] == CODEWORD:
        if user_id not in temp_users:
            temp_users.append(user_id)
            allowed_users.append(user_id)
            await message.reply("Acceso concedido.")
        else:
            await message.reply("Ya estás en la lista de acceso temporal.")
    else:
        await message.reply("Palabra secreta incorrecta.")

@app.on_message()
async def handle_message(client, message):
    await lista_cmd(app)
    global bot_is_sleeping, start_sleep_time, sleep_duration
    user_id = message.from_user.id if message.from_user else ""
    username = message.from_user.username if message.from_user else ""
    chat_id = message.chat.id if message.chat else ""

    if user_id in ban_users:
        return

    if not is_bot_public() and user_id not in allowed_users and chat_id not in allowed_users:
        return

    if message.text and message.text.startswith("/reactive") and (str(user_id) == MAIN_ADMIN or username.lower() == MAIN_ADMIN.lower()):
        if bot_is_sleeping:
            bot_is_sleeping = False
            await app.send_sticker(chat_id, sticker=random.choice(STICKER_REACTIVADO))
            await message.reply("Ok, estoy de vuelta.")
        return

    if bot_is_sleeping and start_sleep_time:
        remaining = max(0, sleep_duration - int(time.time() - start_sleep_time))
        await app.send_sticker(chat_id, sticker=random.choice(STICKER_DESCANSO))
        await message.reply(f"Actualmente estoy descansando, no recibo comandos.\n\nRegresaré en {format_time(remaining)}")
        return

    if message.text and message.text.startswith("/sleep") and (str(user_id) == MAIN_ADMIN or username.lower() == MAIN_ADMIN.lower()):
        try:
            sleep_duration = int(message.text.split(" ")[1])
            bot_is_sleeping = True
            start_sleep_time = time.time()
            await message.reply(f"Ok, voy a descansar {format_time(sleep_duration)}.")
            await asyncio.sleep(sleep_duration)
            bot_is_sleeping = False
            await app.send_sticker(chat_id, sticker=random.choice(STICKER_REACTIVADO))
            await message.reply("Ok, estoy de vuelta.")
        except ValueError:
            await message.reply("Por favor, proporciona un número válido en segundos.")
        return

    if message.text and message.text.startswith("/access") and message.chat.type == "private":
        await process_access_command(message)
        return

    active_cmd = os.getenv('ACTIVE_CMD', '').lower()
    admin_cmd = os.getenv('ADMIN_CMD', '').lower()
    await process_command(client, message, active_cmd, admin_cmd, user_id, username, chat_id)

logging.basicConfig(level=logging.ERROR)

async def notify_main_admin():
    if MAIN_ADMIN:
        try:
            chat_id = int(MAIN_ADMIN) if MAIN_ADMIN.isdigit() else MAIN_ADMIN
            sticker_msg = await app.send_sticker(chat_id, sticker=random.choice(STICKER_SALUDO))
            text_msg = await app.send_message(chat_id=chat_id, text=f"Bot @{app.me.username} iniciado")
            await asyncio.sleep(5)
            await app.delete_messages(chat_id, message_ids=[sticker_msg.id, text_msg.id])
        except Exception as e:
            logging.error(f"Error al enviar o borrar el mensaje al MAIN_ADMIN: {e}")

@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    mail_related = ["send_next_part", "cancel_send", "no_action"] + [f"auto_delay_{x}" for x in [10, 30, 60, 90, 180]]
    help_related = [f"help_{x}" for x in [1, 2, 3, 4, 5]] + ["help_back"]
    if data in mail_related:
        await mail_query(client, callback_query)
    elif data in help_related:
        await handle_help_callback(client, callback_query)
    else:
        await callback_query.answer("No se ha encontrado una respuesta Query correcta.", show_alert=True)

async def main():
    await app.start()
    if MAIN_ADMIN:
        await notify_main_admin()
    print("Bot iniciado y operativo.")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Detención forzada realizada")
