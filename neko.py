import os
import asyncio
import nest_asyncio
from pyrogram import Client, filters
from process_command import process_command
from command.htools import manejar_opcion
from command.help import handle_help_callback, handle_help
import time  
from data.stickers import saludos
import random
from cmd_list import lista_cmd
from data.vars import api_id, api_hash, bot_token, admin_users, users, temp_users, temp_chats, vip_users, ban_users, MAIN_ADMIN, CODEWORD, BOT_IS_PUBLIC, PROTECT_CONTENT, allowed_ids, allowed_users
nest_asyncio.apply()

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Inicializar variables globales
bot_is_sleeping = False
sleep_duration = 0
start_sleep_time = 0  # Inicializada con 0 para evitar problemas

# Función para verificar si el bot es público
def is_bot_public():
    return BOT_IS_PUBLIC
    
# Función para convertir segundos a un formato legible con singular/plural
def format_time(seconds):
    years = seconds // (365 * 24 * 3600)
    days = (seconds % (365 * 24 * 3600)) // (24 * 3600)
    hours = (seconds % (24 * 3600)) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    formatted_time_parts = []
    if years > 0:
        formatted_time_parts.append(f"{years} año" if years == 1 else f"{years} años")
    if days > 0:
        formatted_time_parts.append(f"{days} día" if days == 1 else f"{days} días")
    if hours > 0:
        formatted_time_parts.append(f"{hours} hora" if hours == 1 else f"{hours} horas")
    if minutes > 0:
        formatted_time_parts.append(f"{minutes} minuto" if minutes == 1 else f"{minutes} minutos")
    if seconds > 0:
        formatted_time_parts.append(f"{seconds} segundo" if seconds == 1 else f"{seconds} segundos")

    return ", ".join(formatted_time_parts)

# Comando para procesar acceso temporal
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
    username = message.from_user.username if message.from_user  else ""
    chat_id = message.chat.id if message.chat else ""
    auto = True

    if user_id in ban_users:
        return

    if not is_bot_public() and user_id not in allowed_users and chat_id not in allowed_users:
        return

    if message.text and message.text.startswith("/reactive") and (str(user_id) == MAIN_ADMIN or username.lower() == MAIN_ADMIN.lower()):
        if bot_is_sleeping:
            bot_is_sleeping = False

            await client.send_sticker(
                chat_id=message.chat.id,
                sticker="CAACAgIAAxkBAAIKa2fr9k_RUYKn3a2ESnotX5OZix-DAAJlOgAC4KOCB0AuzmaDZs-sHgQ"
            )
            time.sleep(3)
            await message.reply("Ok, estoy de vuelta.")
        return

    if bot_is_sleeping and start_sleep_time:
        remaining_time = max(0, sleep_duration - int(time.time() - start_sleep_time))
        await client.send_sticker(
            chat_id=message.chat.id,
            sticker="CAACAgIAAxkBAAIKZWfr9RGuAW3W0j9az_LcQTeV8sXvAAIWSwAC4KOCB9L-syYc0ZfXHgQ"
        )
        time.sleep(3)
        await message.reply(
            f"Actualmente estoy descansando, no recibo comandos.\n\nRegresare en {format_time(remaining_time)}"
        )
        return

    if message.text and message.text.startswith("/sleep") and (str(user_id) == MAIN_ADMIN or username.lower() == MAIN_ADMIN.lower()):
        try:
            sleep_duration = int(message.text.split(" ")[1])
            bot_is_sleeping = True
            start_sleep_time = time.time()

            # Crear formato dinámico
            formatted_time = format_time(sleep_duration)

            # Enviar sticker y mensaje
            await client.send_sticker(
                chat_id=message.chat.id,
                sticker="CAACAgIAAxkBAAIKaGfr9YQxXzDbZD24aFoOoLvFUC9DAAIVSwAC4KOCB43TpRr21-13HgQ"
            )
            time.sleep(3)
            await message.reply(f"Ok, voy a descansar {formatted_time}.")

            # Temporizador para finalizar descanso
            await asyncio.sleep(sleep_duration)
            bot_is_sleeping = False

            # Notificar al MAIN_ADMIN que terminó el descanso
            await message.send_sticker(
                chat_id=message.chat.id,
                sticker="CAACAgIAAxkBAAIKa2fr9k_RUYKn3a2ESnotX5OZix-DAAJlOgAC4KOCB0AuzmaDZs-sHgQ"
            )
            time.sleep(3)
            await message.reply("Ok, estoy de vuelta.")

        except ValueError:
            await message.reply("Por favor, proporciona un número válido en segundos.")
        return

    # Comando /access
    if message.text and message.text.startswith("/access") and message.chat.type == "private":
        await process_access_command(message)
        return

    # Procesar comandos activos
    active_cmd = os.getenv('ACTIVE_CMD', '').lower()
    admin_cmd = os.getenv('ADMIN_CMD', '').lower()
    await process_command(client, message, active_cmd, admin_cmd, user_id, username, chat_id)


import asyncio
import logging
import random

# Configuración del módulo logging
logging.basicConfig(level=logging.ERROR)

async def notify_main_admin():
    if MAIN_ADMIN:
        try:
            chat_id = int(MAIN_ADMIN) if MAIN_ADMIN.isdigit() else MAIN_ADMIN

            # Enviar el sticker y el mensaje al MAIN_ADMIN
            sticker_message = await app.send_sticker(chat_id, sticker=random.choice(saludos))
            text_message = await app.send_message(
                chat_id=chat_id,
                text=f"Bot @{app.me.username} iniciado"
            )

            # Esperar 5 segundos antes de borrar los mensajes
            await asyncio.sleep(5)
            await app.delete_messages(chat_id=chat_id, message_ids=[sticker_message.id, text_message.id])

        except Exception as e:
            logging.error(f"Error al enviar o borrar el mensaje al MAIN_ADMIN: {e}")


@app.on_callback_query(filters.regex("^(cbz|pdf|fotos)"))
async def callback_handler(client, callback_query):
    user_id = callback_query.from_user.id
    protect_content = PROTECT_CONTENT and user_id not in allowed_ids
    await manejar_opcion(client, callback_query, protect_content, user_id)

@app.on_callback_query()
async def help_callback_handler(client, callback_query):
    await handle_help_callback(client, callback_query)
    
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
