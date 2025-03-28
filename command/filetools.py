import os
import shutil
import random
import string
import py7zr
from pyrogram import Client, filters

user_comp = {} 
compression_size = 10  

def compressfile(file_path, part_size):
    parts = []
    part_size *= 1024 * 1024  
    archive_path = f"{file_path}.7z"
    with py7zr.SevenZipFile(archive_path, 'w') as archive:
        archive.write(file_path, os.path.basename(file_path))
    with open(archive_path, 'rb') as archive:
        part_num = 1
        while True:
            part_data = archive.read(part_size)
            if not part_data:
                break
            part_file = f"{archive_path}.{part_num:03d}"
            with open(part_file, 'wb') as part:
                part.write(part_data)
            parts.append(part_file)
            part_num += 1
    return parts

async def handle_compress(client, message, username):
    reply_message = message.reply_to_message

    # Verificar si el caption empieza con "Look Here" y el remitente es el bot
    if reply_message and reply_message.caption and reply_message.caption.startswith("Look Here") and reply_message.from_user.is_self:
        await message.reply("No puedes comprimir este contenido debido a restricciones.", protect_content=True)
        return

    try:
        os.system("rm -rf ./server/*")
        await message.reply("Descargando el archivo para comprimirlo...")
        
        def get_file_name(message):
            if message.reply_to_message.document:
                return os.path.basename(message.reply_to_message.document.file_name)[:50]
            elif message.reply_to_message.photo:
                return ''.join(random.choices(string.ascii_letters + string.digits, k=20)) + ".jpg"
            elif message.reply_to_message.audio:
                return ''.join(random.choices(string.ascii_letters + string.digits, k=20)) + ".mp3"
            elif message.reply_to_message.video:
                return ''.join(random.choices(string.ascii_letters + string.digits, k=20)) + ".mp4"
            elif message.reply_to_message.sticker:
                return ''.join(random.choices(string.ascii_letters + string.digits, k=20)) + ".webp"
            else:
                return ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        
        file_name = get_file_name(message)
        file_path = await client.download_media(
            message.reply_to_message,
            file_name=file_name
        )
        await message.reply("Comprimiendo el archivo...")
        
        sizd = user_comp.get(username, 10)
        parts = compressfile(file_path, sizd)
        
        await message.reply("Se ha comprimido el archivo, ahora se enviarán las partes")
        for part in parts:
            try:
                await client.send_document(message.chat.id, part)
            except Exception as e:
                print(f"Error al enviar la parte {part}: {e}")
                await message.reply(f"Error al enviar la parte {part}: {e}")
        
        await message.reply("Esas son todas las partes")
        shutil.rmtree('server')
        os.mkdir('server')
    
    except Exception as e:
        await message.reply(f'Error: {str(e)}')

async def rename(client, message):
    reply_message = message.reply_to_message

    # Verificar si el caption empieza con "Look Here" y el remitente es el bot
    if reply_message and reply_message.caption and reply_message.caption.startswith("Look Here") and reply_message.from_user.is_self:
        await message.reply("No puedes renombrar este contenido debido a restricciones.", protect_content=True)
        return

    if reply_message and reply_message.media:
        try:
            await message.reply("Descargando el archivo para renombrarlo...")
            new_name = message.text.split(' ', 1)[1]
            file_path = await client.download_media(reply_message)
            new_file_path = os.path.join(os.path.dirname(file_path), new_name)
            os.rename(file_path, new_file_path)
            await message.reply("Subiendo el archivo con nuevo nombre...")
            await client.send_document(message.chat.id, new_file_path)
            os.remove(new_file_path)
        except Exception as e:
            await message.reply(f'Error: {str(e)}')
    else:
        await message.reply('Ejecute el comando respondiendo a un archivo')

async def set_size(client, message):
    valor = int(message.text.split(" ")[1])
    username = message.from_user.username
    user_comp[username] = valor
    await message.reply(f"Tamaño de archivos {valor}MB registrado para el usuario @{username}")
