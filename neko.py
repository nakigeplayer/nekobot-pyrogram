import os
import glob
from pyrogram import Client, filters
import zipfile
import shutil
import random
import string
import smtplib
import requests
import re
import datetime
import subprocess
import asyncio
import os
import hashlib
import py7zr
import shutil
import string
import random
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from moodleclient import upload_token
from email.message import EmailMessage
from pyrogram.types import Message
from PIL import Image
from htools import nh_combined_operation
from admintools import add_user, remove_user, add_chat, remove_chat, ban_user, deban_user
from imgtools import create_imgchest_post
from webtools import handle_scan, handle_multiscan
from mailtools import send_mail, set_mail
from videotools import update_video_settings, compress_video
from filetools import handle_compress, rename, set_size
from process_command import process_command

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('TOKEN')
admin_users = list(map(int, os.getenv('ADMINS').split(',')))
users = list(map(int, os.getenv('USERS').split(',')))
temp_users = []
temp_chats = []
ban_users = []
allowed_users = admin_users + users + temp_users + temp_chats
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
compression_size = 10  
file_counter = 0
bot_in_use = False
user_emails = {}
image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']

async def handle_start(client, message):
    await message.reply("Funcionando")
    
CODEWORD = os.getenv("CODEWORD")
@app.on_message(filters.command("access") & filters.private)
def access_command(client, message):
    user_id = message.from_user.id
    if len(message.command) > 1 and message.command[1] == CODEWORD:
        if user_id not in temp_users:
            temp_users.append(user_id)
            allowed_users.append(user_id)  
            message.reply("Acceso concedido.")
        else:
            message.reply("Ya estás en la lista de acceso temporal.")
    else:
        message.reply("Palabra secreta incorrecta.")
        
BOT_IS_PUBLIC = os.getenv("BOT_IS_PUBLIC")
def is_bot_public():
    return BOT_IS_PUBLIC and BOT_IS_PUBLIC.lower() == "true"
    
@app.on_message(filters.text)
async def handle_message(client, message):
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id
    
    if user_id in ban_users:
        return
    
    if not is_bot_public() and user_id not in allowed_users and chat_id not in allowed_users:
        return
    
    active_cmd = os.getenv("ACTIVE_CMD", "").lower()
    admin_cmd = os.getenv("ADMIN_CMD", "").lower()

    await process_command(client, message, active_cmd, admin_cmd, user_id, username, chat_id)
    
app.run()
app.start()
