import os

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('TOKEN')
admin_users = list(map(int, os.getenv('ADMINS').split(','))) if os.getenv('ADMINS') else []
users = list(map(int, os.getenv('USERS').split(','))) if os.getenv('USERS') else []
vip_users = list(map(int, os.getenv('VIP_USERS', '').split(','))) if os.getenv('VIP_USERS') else []
temp_users, temp_chats, ban_users = [], [], []
video_limit = os.getenv('VIDEO_LIMIT')
video_limit = int(video_limit) if video_limit else None

MAIN_ADMIN = os.getenv("MAIN_ADMIN")
CODEWORD = os.getenv('CODEWORD', '')
BOT_IS_PUBLIC = os.getenv('BOT_IS_PUBLIC', 'false').strip().lower() == "true"
PROTECT_CONTENT = os.getenv('PROTECT_CONTENT', '').strip().lower() == "true"

allowed_users = admin_users + users + temp_users + temp_chats
allowed_ids = set(admin_users).union(set(vip_users))

# Inicializamos video_settings con un ID base como 'default'
video_settings = {
    'default': {
        'resolution': '640x400',
        'crf': '28',
        'audio_bitrate': '80k',
        'fps': '18',
        'preset': 'veryfast',
        'codec': 'libx265'
    }
}
