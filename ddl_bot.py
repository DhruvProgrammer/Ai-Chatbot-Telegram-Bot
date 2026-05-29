from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import re

API_ID = 25548765
API_HASH = "5b151e1c92a755111f516974a3b339ab"
BOT_TOKEN = "6552501089:AAEsQXoB769g_VINKVeq5uFiz-4ZGm3daRc"

app = Client("ddl_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def extract_links(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            return None

        html = response.text

        links = {}

        # File name
        name_match = re.search(r'Name\s*:\s*(.+?)</li>', html)
        if name_match:
            links["name"] = name_match.group(1).strip()

        # Size
        size_match = re.search(r'Size\s*:\s*(.+?)\s*\|', html)
        if size_match:
            links["size"] = size_match.group(1).strip()

        # PixelDrain
        pd_match = re.search(r'href="(https://pixeldrain\.dev/u/[a-zA-Z0-9]+)"', html)
        if pd_match:
            links["pixeldrain"] = pd_match.group(1)

        # Instant DL
        instant_match = re.search(r'href="(https://instant\.busycdn\.xyz/[^"]+)"', html)
        if instant_match:
            links["instant_dl"] = instant_match.group(1)

        # GoFile / Multiup
        gofile_match = re.search(r'href="(https://validate\.multiup[^"]+)"', html)
        if gofile_match:
            links["gofile"] = gofile_match.group(1)

        # Telegram Bot
        tg_match = re.search(r'href="(https://t\.me/[^"]+start=[^"]+)"', html)
        if tg_match:
            links["telegram"] = tg_match.group(1)

        return links if links else None

    except Exception as e:
        print(f"Error: {e}")
        return None


@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(
        "DDL Link Extractor Bot\n\n"
        "Send me a GDFlix link and I'll extract all download links.\n\n"
        "Example:\n"
        "https://gdflix.dev/file/xxxxx"
    )


@app.on_message(filters.text & filters.private)
async def handle_link(client, message: Message):
    url = message.text.strip()

    if "gdflix.dev/file/" not in url and "gdflix." not in url:
        await message.reply_text("Please send a valid GDFlix link.")
        return

    msg = await message.reply_text("Extracting links...")

    data = await __import__("asyncio").to_thread(extract_links, url)

    if not data:
        await msg.edit("Could not extract links. The link may be invalid or the site may be down.")
        return

    text = ""

    if "name" in data:
        text += f"File: {data['name']}\n"
    if "size" in data:
        text += f"Size: {data['size']}\n"

    text += "\nDownload Links:\n\n"

    if "instant_dl" in data:
        text += f"Instant DL:\n{data['instant_dl']}\n\n"
    if "pixeldrain" in data:
        text += f"PixelDrain:\n{data['pixeldrain']}\n\n"
    if "gofile" in data:
        text += f"GoFile (Mirrors):\n{data['gofile']}\n\n"
    if "telegram" in data:
        text += f"Telegram:\n{data['telegram']}\n\n"

    await msg.edit(text, disable_web_page_preview=True)


print("Bot Starting...")
app.run()
