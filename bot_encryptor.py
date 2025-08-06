import os
import dotenv
import discord
import asyncio
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import random
from commands import handle_command

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
API_URL = os.getenv("API_URL")  # e.g. http://127.0.0.1:8000/api/key/
API_TOKEN = os.getenv("API_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

cached_key = None
cached_salt = None

def fetch_key_and_salt():
    global cached_key, cached_salt
    try:
        headers = {"Authorization": f"Token {API_TOKEN}"}
        response = requests.get(API_URL, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        cached_key = bytes.fromhex(data["key"])
        cached_salt = data["salt"].encode()
    except Exception as e:
        print("[WARN] API unreachable. Using cached key/salt.")


def encrypt_message(message: str) -> str:
    if not cached_key or not cached_salt:
        fetch_key_and_salt()

    iv = cached_salt[:16]
    cipher = AES.new(cached_key, AES.MODE_CBC, iv)
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    return cached_salt.decode() + base64.b64encode(ct_bytes).decode()


async def keep_alive():
    while True:
        wait_minutes = random.randint(1, 12)
        await asyncio.sleep(wait_minutes * 60)
        try:
            headers = {"Authorization": f"Token {API_TOKEN}"}
            response = requests.get(API_URL, headers=headers, timeout=5)
            print(f"[Keep-Alive] Pinged API ({response.status_code}) after {wait_minutes} min.")
        except Exception as e:
            print("[Keep-Alive] API ping failed.")


@client.event
async def on_ready():
    print(f'Bot connected as {client.user}')
    fetch_key_and_salt()
    client.loop.create_task(keep_alive())


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("?"):
        command_result = await handle_command(message, encrypt_message)

        if command_result:
            await message.delete()
            await message.channel.send(command_result)


client.run(BOT_TOKEN)
