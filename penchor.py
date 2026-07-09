from pyrogram import Client, filters, idle, raw
from pyrogram.types import Message, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, PeerIdInvalid
import requests
import html
import re
import asyncio
import json
import os
import tempfile
import time

API_ID = 25548765
API_HASH = "5b151e1c92a755111f516974a3b339ab"
BOT_TOKEN = "7167460054:AAHqBsR_vAVM3DG3yvnwT6Y7r5Tii59QKdA"

OWNER_ID = 6397638677
AUTHORIZED_USERS = [8236652660, 6397638677, 1493254974, 5360075159]

AUTOPOST_CHANNEL_ID = "@Goblin_In_Hindii"

# Search Sites
SITES = [
    {
        "name": "TGMovies",
        "emoji": "🎥",
        "url": "https://tgmovies.morimoflix.xyz",
        "api": "https://tgmovies.morimoflix.xyz/wp-json/wp/v2/movie",
    },
    {
        "name": "Morimoflix",
        "emoji": "🎬",
        "url": "https://morimoflix.xyz",
        "api": "https://morimoflix.xyz/wp-json/wp/v2/posts",
    },
    {
        "name": "HentaiDekho",
        "emoji": "🌸",
        "url": "https://hentaidekho.mom",
        "api": "https://hentaidekho.mom/wp-json/wp/v2/posts",
    },
    {
        "name": "AdultMorimoflix",
        "emoji": "🔞",
        "url": "https://adult.morimoflix.xyz",
        "api": "https://adult.morimoflix.xyz/wp-json/wp/v2/posts",
    },
]

CHANNELS_FILE = "channels_config.json"

channels_config = {"channels": {}}


def load_channels():
    global channels_config
    try:
        if os.path.exists(CHANNELS_FILE):
            with open(CHANNELS_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and "channels" in data and isinstance(data["channels"], dict):
                    channels_config = data
    except Exception:
        pass

    if not channels_config.get("channels"):
        channels_config["channels"] = {
            AUTOPOST_CHANNEL_ID: {
                "sites": ["TGMovies", "Morimoflix", "AdultMorimoflix"],
                "last_ids": {}
            }
        }
        save_channels()


def save_channels():
    try:
        with open(CHANNELS_FILE, "w") as f:
            json.dump(channels_config, f)
    except Exception as e:
        print(f"Error saving channels: {e}")


def get_channel_data(channel_id):
    key = str(channel_id)
    if key not in channels_config["channels"]:
        channels_config["channels"][key] = {"sites": [], "last_ids": {}}
    return channels_config["channels"][key]


def get_enabled_sites(channel_id):
    ch = channels_config["channels"].get(str(channel_id), {})
    sites = ch.get("sites", [])
    by_name = {s["name"]: s for s in SITES}
    return [by_name[name] for name in sites if name in by_name]


AUTOPOST_FETCH_COUNT = 10
AUTOPOST_POST_DELAY = 4
AUTOPOST_CYCLE_DELAY = 60


# =====================================================
# APP
# =====================================================

app = Client(
    "movie_search_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# =====================================================
# HELPERS
# =====================================================

def normalize(text):
    return text.lower().strip()

def clean_html(raw_html):
    clean = re.sub('<.*?>', '', raw_html)
    return html.unescape(clean)


# =====================================================
# AUTOPOST HELPERS
# =====================================================

def scrape_movie_page_metadata(url):
    result = {"language": "", "posted_by": ""}
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return result
        html_text = resp.text

        lang_match = re.search(
            r'<p[^>]*class="[^"]*uppercase[^"]*"[^>]*>\s*Language\s*</p>\s*<p[^>]*class="[^"]*text-white[^"]*"[^>]*>([^<]+)</p>',
            html_text, re.IGNORECASE
        )
        if not lang_match:
            lang_match = re.search(
                r'Language\s*</p>\s*<p[^>]*>([^<]+)</p>',
                html_text, re.IGNORECASE
            )
        if lang_match:
            result["language"] = clean_html(lang_match.group(1)).strip()

        posted_match = re.search(
            r'<p[^>]*class="[^"]*uppercase[^"]*"[^>]*>\s*Posted\s*By\s*</p>\s*<p[^>]*class="[^"]*text-white[^"]*"[^>]*>([^<]+)</p>',
            html_text, re.IGNORECASE
        )
        if not posted_match:
            posted_match = re.search(
                r'Posted\s*By\s*</p>\s*<p[^>]*>([^<]+)</p>',
                html_text, re.IGNORECASE
            )
        if posted_match:
            result["posted_by"] = clean_html(posted_match.group(1)).strip()

    except Exception as e:
        print(f"AUTOPOST: scrape_movie_page_metadata error for {url}: {e}")
    return result


def parse_post(post):
    title = clean_html(post["title"]["rendered"])

    year = ""
    year_match = re.search(r'\((\d{4})\)', title)
    if year_match:
        year = year_match.group(1)
        title = re.sub(r'\s*\(\d{4}\)\s*', '', title).strip()
    else:
        year_match = re.search(r'\b(\d{4})\b', title)
        if year_match:
            year = year_match.group(1)

    language = ""
    lang_patterns = [
        r'\((Hindi|English|Tamil|Telugu|Malayalam|Kannada|Bengali|Marathi|Punjabi|Gujarati|Dual Audio|Multi Audio)\)',
        r'\[(Hindi|English|Tamil|Telugu|Malayalam|Kannada|Bengali|Marathi|Punjabi|Gujarati|Dual Audio|Multi Audio)\]',
        r'(Hindi|English|Tamil|Telugu|Malayalam|Kannada|Bengali|Marathi|Punjabi|Gujarati|Dual Audio|Multi Audio)',
    ]

    for pattern in lang_patterns:
        lang_match = re.search(pattern, title, re.IGNORECASE)
        if lang_match:
            language = lang_match.group(1)
            title = re.sub(pattern, '', title, flags=re.IGNORECASE).strip()
            break

    title = re.sub(r'\s+', ' ', title).strip()
    title = re.sub(r'^\(|\)$', '', title).strip()
    title = re.sub(r'^\[|\]$', '', title).strip()

    excerpt = clean_html(post["excerpt"]["rendered"])
    excerpt = re.sub(r'\[…\]|\.\.\.$', '', excerpt).strip()
    excerpt = re.sub(r'\s+', ' ', excerpt)

    poster_url = None
    embedded = post.get("_embedded", {})
    featured_media_list = embedded.get("wp:featuredmedia", [])
    if featured_media_list:
        fm = featured_media_list[0]
        poster_url = fm.get("source_url")
        if not poster_url:
            media_details = fm.get("media_details", {})
            sizes = media_details.get("sizes", {})
            for size_name in ["full", "morimoflix-poster", "medium"]:
                size_data = sizes.get(size_name, {})
                if size_data.get("source_url"):
                    poster_url = size_data["source_url"]
                    break

    return {
        "id": post["id"],
        "title": title,
        "link": post["link"],
        "excerpt": excerpt[:300] if excerpt else "No description available",
        "year": year,
        "language": language,
        "poster_url": poster_url,
        "posted_by": "",
    }


def get_latest_posts(site_api, count=10):
    try:
        response = requests.get(
            site_api,
            params={"per_page": count, "_embed": "wp:featuredmedia"},
            timeout=15
        )

        if response.status_code != 200:
            return []

        data = response.json()

        if not data:
            return []

        results = []
        for post in data:
            parsed = parse_post(post)
            results.append(parsed)

        return results

    except Exception as e:
        print(f"AUTOPOST ERROR ({site_api}): {e}")
        return []


# =====================================================
# AUTOPOST LOOP
# =====================================================

async def verify_channel_access(client, channel_id):
    try:
        chat = await client.get_chat(channel_id)
        print(f"AUTOPOST: Channel verified: {chat.title} ({channel_id})")
        return True
    except PeerIdInvalid:
        print(f"AUTOPOST WARNING: PeerIdInvalid for {channel_id}, will try sending anyway")
        return True
    except Exception as e:
        print(f"AUTOPOST WARNING: verify failed for {channel_id}: {e}, will try sending anyway")
        return True


async def download_poster(poster_url):
    if not poster_url:
        return None
    tmp_path = None
    try:
        resp = requests.get(poster_url, timeout=15)
        if resp.status_code == 200:
            ext = ".jpg"
            lower_url = poster_url.lower()
            if ".png" in lower_url:
                ext = ".png"
            elif ".webp" in lower_url:
                ext = ".webp"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            tmp.write(resp.content)
            tmp.close()
            tmp_path = tmp.name
            return tmp_path
    except Exception as e:
        print(f"AUTOPOST: Poster download failed: {e}")
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    return None


async def safe_send_photo(client, chat_id, photo_path, caption, max_retries=3):
    for attempt in range(max_retries):
        try:
            await client.send_photo(chat_id, photo=photo_path, caption=caption, parse_mode=ParseMode.HTML)
            return True
        except FloodWait as e:
            print(f"AUTOPOST: Flood wait {e.value}s, attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                await asyncio.sleep(e.value)
            else:
                return False
        except PeerIdInvalid:
            print(f"AUTOPOST: PeerIdInvalid on attempt {attempt + 1}, refreshing peer cache...")
            try:
                await client.get_dialogs()
            except Exception:
                pass
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        except Exception as e:
            print(f"AUTOPOST ERROR sending photo: {e}")
            return False
    return False


async def safe_send_message(client, chat_id, text, max_retries=3):
    for attempt in range(max_retries):
        try:
            await client.send_message(chat_id, text, disable_web_page_preview=False, parse_mode=ParseMode.HTML)
            return True
        except FloodWait as e:
            print(f"AUTOPOST: Flood wait {e.value}s, attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                await asyncio.sleep(e.value)
            else:
                return False
        except Exception as e:
            print(f"AUTOPOST ERROR: {e}")
            return False
    return False


def build_caption(post, site_name):
    title = html.escape(str(post.get('title', '')))
    language = html.escape(str(post.get('language', '')))
    raw_posted_by = str(post.get('posted_by', '')).strip()
    posted_by = html.escape(raw_posted_by) if raw_posted_by else html.escape(site_name)
    excerpt = html.escape(str(post.get('excerpt', '')))
    link = str(post.get('link', ''))

    caption = f"🆕 {html.escape(site_name)}\n"
    caption += "──────────────────────\n"
    caption += f"◈ Movie: {title}\n"

    if language:
        caption += f"◈ Languages: {language}\n"

    caption += f"◈ Posted by: {posted_by}\n"
    caption += f"◈ Description: {excerpt}\n"
    caption += "──────────────────────\n"
    caption += "❒ 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗯𝘆: @The_JonesNetwork\n\n"
    caption += f"🔗 <a href=\"{html.escape(link, quote=True)}\">Click me to view the movie</a>"

    return caption


async def process_site(site, app, channel_id, last_ids):
    latest_posts = get_latest_posts(site["api"], count=AUTOPOST_FETCH_COUNT)

    if not latest_posts:
        return

    site_last_key = last_ids.get(site['name'])
    site_last_id = None
    if site_last_key:
        try:
            site_last_id = int(site_last_key.split('_', 1)[1])
        except (ValueError, IndexError):
            site_last_id = None

    new_posts = []
    for post in latest_posts:
        if site_last_id is None or post['id'] > site_last_id:
            new_posts.append(post)

    if not new_posts:
        return

    newest_post = new_posts[0]
    last_ids[site['name']] = f"{site['name']}_{newest_post['id']}"
    save_channels()

    for post in reversed(new_posts):
        title = post['title']

        page_meta = await asyncio.to_thread(scrape_movie_page_metadata, post['link'])
        if page_meta.get('language'):
            post['language'] = page_meta['language']
        if page_meta.get('posted_by'):
            post['posted_by'] = page_meta['posted_by']

        caption = build_caption(post, site['name'])

        poster_path = None
        poster_url = post.get('poster_url')
        if poster_url:
            poster_path = await download_poster(poster_url)

        sent = False
        if poster_path:
            sent = await safe_send_photo(app, channel_id, poster_path, caption)
            try:
                if poster_path:
                    os.unlink(poster_path)
            except OSError:
                pass

        if not sent:
            sent = await safe_send_message(app, channel_id, caption)

        if sent:
            print(f"AUTOPOST: [{channel_id}] Posted: {title} ({site['name']})")
            await asyncio.sleep(AUTOPOST_POST_DELAY)


async def autopost_loop():
    cycle_count = 0
    verify_interval = 30
    channel_verified = {}

    while True:
        try:
            cycle_count += 1

            for channel_id in list(channels_config.get("channels", {}).keys()):
                ch_data = channels_config["channels"].get(channel_id)
                if not ch_data:
                    continue

                enabled_sites = ch_data.get("sites", [])
                if not enabled_sites:
                    continue

                last_ids = ch_data.get("last_ids", {})

                if not last_ids:
                    for site_name in list(enabled_sites):
                        site = next((s for s in SITES if s["name"] == site_name), None)
                        if not site:
                            continue
                        try:
                            latest_posts = get_latest_posts(site["api"], count=AUTOPOST_FETCH_COUNT)
                            if latest_posts:
                                newest = latest_posts[0]
                                last_ids[site_name] = f"{site_name}_{newest['id']}"
                        except Exception as e:
                            print(f"AUTOPOST: init error for {site_name} in {channel_id}: {e}")
                    ch_data["last_ids"] = last_ids
                    save_channels()
                    print(f"AUTOPOST: Initialized {channel_id} with IDs: {last_ids}")
                    continue

                if not channel_verified.get(channel_id) or cycle_count % verify_interval == 0:
                    channel_verified[channel_id] = await verify_channel_access(app, channel_id)

                for site_name in list(enabled_sites):
                    site = next((s for s in SITES if s["name"] == site_name), None)
                    if not site:
                        continue
                    try:
                        await process_site(site, app, channel_id, last_ids)
                    except Exception as e:
                        print(f"AUTOPOST: error processing {site_name} in {channel_id}: {e}")
                        continue

        except Exception as e:
            print("LOOP ERROR:", e)

        await asyncio.sleep(AUTOPOST_CYCLE_DELAY)


# =====================================================
# SETTINGS COMMAND (PER-CHANNEL)
# =====================================================

def build_channels_keyboard():
    buttons = []
    for ch_id, ch_data in channels_config.get("channels", {}).items():
        enabled_count = len(ch_data.get("sites", []))
        buttons.append([InlineKeyboardButton(
            f"{ch_id} ({enabled_count} sites)",
            callback_data=f"settingsch|{ch_id}"
        )])
    buttons.append([InlineKeyboardButton("➕ Add Channel", callback_data="add_channel")])
    buttons.append([InlineKeyboardButton("Close", callback_data="close_settings")])
    return InlineKeyboardMarkup(buttons)


def build_channel_settings_keyboard(channel_id):
    ch_data = channels_config["channels"].get(str(channel_id), {"sites": []})
    enabled_sites = ch_data.get("sites", [])
    buttons = []
    for site in SITES:
        status = "✅" if site["name"] in enabled_sites else "❌"
        buttons.append([InlineKeyboardButton(
            f"{status} {site['name']}",
            callback_data=f"toggle|{channel_id}|{site['name']}"
        )])
    buttons.append([InlineKeyboardButton("🗑 Remove Channel", callback_data=f"removech|{channel_id}")])
    buttons.append([InlineKeyboardButton("« Back to Channels", callback_data="back_to_channels")])
    buttons.append([InlineKeyboardButton("Close", callback_data="close_settings")])
    return InlineKeyboardMarkup(buttons)


@app.on_message(filters.command("settings") & filters.user(AUTHORIZED_USERS))
async def settings_command(client, message: Message):
    await message.reply_text(
        "**Autopost Channel Settings**\n\n"
        "Select a channel to configure its autopost sites:",
        reply_markup=build_channels_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


@app.on_message(filters.command("channels") & filters.user(AUTHORIZED_USERS))
async def channels_command(client, message: Message):
    if not channels_config.get("channels"):
        await message.reply_text("No channels configured. Use /addchannel to add one.")
        return

    text = "**Configured Autopost Channels:**\n\n"
    for ch_id, ch_data in channels_config["channels"].items():
        try:
            chat = await client.get_chat(ch_id)
            title = chat.title
        except Exception:
            title = ch_id
        sites = ch_data.get("sites", [])
        text += f"• **{title}** (`{ch_id}`)\n"
        text += f"  Sites: {', '.join(sites) if sites else '_none_'}\n\n"

    text += "Use /settings to configure."
    await message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


@app.on_callback_query(filters.user(AUTHORIZED_USERS))
async def settings_callback(client, callback: CallbackQuery):
    data = callback.data

    if data == "close_settings":
        try:
            await callback.message.delete()
        except Exception:
            pass
        return

    if data == "back_to_channels":
        try:
            await callback.message.edit_text(
                "**Autopost Channel Settings**\n\nSelect a channel to configure:",
                reply_markup=build_channels_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            pass
        await callback.answer()
        return

    if data == "add_channel":
        pending_addchannel[callback.from_user.id] = {
            "expires_at": time.time() + ADDCHANNEL_TIMEOUT
        }
        try:
            await callback.message.edit_text(
                "Send the channel ID or @username to add for autopost.\n\n"
                "Example: `@mychannel` or `-1001234567890`\n\n"
                "Make sure the bot is added as an admin in the channel first."
            )
        except Exception:
            pass
        await callback.answer()
        return

    if data.startswith("settingsch|"):
        channel_id = data.split("|", 1)[1]
        try:
            chat = await client.get_chat(channel_id)
            channel_display = f"{chat.title} ({channel_id})"
        except Exception:
            channel_display = str(channel_id)
        try:
            await callback.message.edit_text(
                f"**Settings for: {channel_display}**\n\nClick to toggle sites on/off:",
                reply_markup=build_channel_settings_keyboard(channel_id),
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            pass
        await callback.answer()
        return

    if data.startswith("toggle|"):
        parts = data.split("|", 2)
        if len(parts) == 3:
            _, channel_id, site_name = parts
            ch_data = get_channel_data(channel_id)
            if site_name in ch_data["sites"]:
                ch_data["sites"].remove(site_name)
            else:
                ch_data["sites"].append(site_name)
            save_channels()
            try:
                await callback.message.edit_reply_markup(build_channel_settings_keyboard(channel_id))
            except Exception:
                pass
            await callback.answer(f"{site_name} toggled")
        return

    if data.startswith("removech|"):
        channel_id = data.split("|", 1)[1]
        if str(channel_id) in channels_config["channels"]:
            del channels_config["channels"][str(channel_id)]
            save_channels()
            try:
                await callback.message.edit_text(
                    "**Autopost Channel Settings**\n\nSelect a channel to configure:",
                    reply_markup=build_channels_keyboard(),
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception:
                pass
            await callback.answer("Channel removed")
        return

    if data.startswith("change_"):
        action = data.replace("change_", "", 1)
        await callback.answer()
        await handle_change_action(client, callback, action)
        return


# =====================================================
# ADD CHANNEL COMMAND
# =====================================================

ADDCHANNEL_TIMEOUT = 90
pending_addchannel = {}


@app.on_message(filters.command("addchannel") & filters.private & filters.user(AUTHORIZED_USERS))
async def addchannel_command(client, message: Message):
    pending_addchannel[message.from_user.id] = {
        "expires_at": time.time() + ADDCHANNEL_TIMEOUT
    }
    await message.reply_text(
        "Send the channel ID or @username to add for autopost.\n\n"
        "Example: `@mychannel` or `-1001234567890`\n\n"
        "Make sure the bot is added as an admin in the channel first."
    )


async def handle_addchannel_response(client, message: Message):
    user_id = message.from_user.id
    pending = pending_addchannel.get(user_id)

    if not pending:
        return

    pending_addchannel.pop(user_id, None)

    if time.time() > pending["expires_at"]:
        await message.reply_text("Add channel request timed out. Try /addchannel again.")
        return

    if not message.text:
        await message.reply_text("Please send the channel ID or @username as text.")
        return

    channel_input = message.text.strip()
    channel_input = channel_input.replace("https://t.me/", "").replace("http://t.me/", "").replace("t.me/", "")

    try:
        chat = await client.get_chat(channel_input)
        channel_id = f"@{chat.username}" if chat.username else str(chat.id)
        channel_title = chat.title
    except Exception as e:
        await message.reply_text(
            f"Could not access channel: {e}\n\n"
            f"Make sure the bot is added as an admin in the channel."
        )
        return

    if channel_id in channels_config["channels"]:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙ Configure Sites", callback_data=f"settingsch|{channel_id}")],
            [InlineKeyboardButton("Close", callback_data="close_settings")]
        ])
        await message.reply_text(
            f"Channel **{channel_title}** (`{channel_id}`) is already configured.\n"
            f"Use /settings or click below to configure its sites.",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        return

    channels_config["channels"][channel_id] = {
        "sites": ["TGMovies", "Morimoflix", "AdultMorimoflix"],
        "last_ids": {}
    }
    save_channels()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙ Configure Sites", callback_data=f"settingsch|{channel_id}")],
        [InlineKeyboardButton("Close", callback_data="close_settings")]
    ])

    await message.reply_text(
        f"✅ Channel added: **{channel_title}** (`{channel_id}`)\n\n"
        f"Default sites enabled: TGMovies, Morimoflix, AdultMorimoflix\n"
        f"Click below to change which sites autopost here:",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )


# =====================================================
# CHANGE COMMAND (operates on default channel)
# =====================================================

CHANGE_PROMPTS = {
    "name": "Send me your new channel name:",
    "username": "Send me your new channel username:",
    "description": "Send me your new channel description/bio:",
    "photo": "Send me your new channel profile photo:",
    "add_admin": "Send me the user ID, username, or forward a message from the user:",
    "unpin": "Send me the message link to unpin, or reply/forward the pinned message:",
}

CHANGE_TIMEOUT_SECONDS = 90
pending_changes = {}


def clean_username_input(text):
    text = text.strip()
    text = text.replace("https://t.me/", "").replace("http://t.me/", "").replace("t.me/", "")
    if text.startswith("@"):
        text = text[1:]
    return text


def clean_user_input(text):
    text = text.strip()
    text = text.replace("https://t.me/", "").replace("http://t.me/", "").replace("t.me/", "")
    if text and not text.startswith("@") and not text.lstrip("-").isdigit():
        text = f"@{text}"
    return text


def extract_message_id_from_link(text):
    patterns = [
        r't\.me/[^/]+/(\d+)',
        r't\.me/c/(\d+)/(\d+)',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            if len(m.groups()) == 1:
                return int(m.group(1))
            return int(m.group(2))
    return None


async def resolve_user_id(client, user_input):
    peer = await client.resolve_peer(user_input)
    if isinstance(peer, raw.types.InputPeerUser):
        return peer.user_id
    if isinstance(peer, raw.types.InputUser):
        return peer.user_id
    raise Exception("Could not resolve user. Send @username, user ID, or forward a message from the user.")


def promote_admin_via_bot_api(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/promoteChatMember"
    data = {
        "chat_id": AUTOPOST_CHANNEL_ID,
        "user_id": user_id,
        "is_anonymous": False,
        "can_manage_chat": True,
        "can_delete_messages": True,
        "can_restrict_members": True,
        "can_promote_members": True,
        "can_change_info": True,
        "can_post_messages": True,
        "can_edit_messages": True,
        "can_invite_users": True,
        "can_pin_messages": True,
    }
    response = requests.post(url, data=data, timeout=30)
    result = response.json()
    if result.get("ok"):
        return True

    description = result.get("description", "")
    if any(error in description for error in ["CHAT_ADMIN_REQUIRED", "USER_ADMIN_INVALID", "BOT_METHOD_INVALID"]):
        raise PermissionError("no rights")

    raise Exception(result.get("description") or result)


async def handle_change_action(client, callback: CallbackQuery, action):
    prompt = CHANGE_PROMPTS.get(action)
    if not prompt:
        await callback.message.edit_text("Invalid option.")
        return

    pending_changes[callback.from_user.id] = {
        "action": action,
        "expires_at": time.time() + CHANGE_TIMEOUT_SECONDS,
    }
    await callback.message.edit_text(prompt)


async def handle_change_response(client, message: Message):
    user_id = message.from_user.id
    pending = pending_changes.get(user_id)

    if not pending:
        return

    pending_changes.pop(user_id, None)

    if time.time() > pending["expires_at"]:
        await message.reply_text("Change request timed out. Please use /change again.")
        return

    action = pending["action"]

    if action == "name":
        if not message.text:
            await message.reply_text("Please send text only.")
            return
        new_value = message.text.strip()
        if not new_value:
            await message.reply_text("Channel name cannot be empty.")
            return
        try:
            await client.set_chat_title(AUTOPOST_CHANNEL_ID, new_value)
            await message.reply_text("Channel name updated.")
        except Exception as e:
            await message.reply_text(f"Failed to update channel name: {e}")

    elif action == "username":
        if not message.text:
            await message.reply_text("Please send text only.")
            return
        new_value = clean_username_input(message.text)
        if not new_value:
            await message.reply_text("Channel username cannot be empty.")
            return
        try:
            await client.set_chat_username(AUTOPOST_CHANNEL_ID, new_value)
            await message.reply_text(f"Channel username updated to @{new_value}.")
        except Exception as e:
            await message.reply_text(f"Failed to update channel username: {e}")

    elif action == "description":
        if not message.text:
            await message.reply_text("Please send text only.")
            return
        new_value = message.text.strip()
        if not new_value:
            await message.reply_text("Channel description/bio cannot be empty.")
            return
        try:
            await client.set_chat_description(AUTOPOST_CHANNEL_ID, new_value)
            await message.reply_text("Channel description/bio updated.")
        except Exception as e:
            await message.reply_text(f"Failed to update channel description: {e}")

    elif action == "add_admin":
        if message.forward_from:
            user_id = message.forward_from.id
            user_label = str(user_id)
        elif message.text:
            user_input = clean_user_input(message.text)
            if not user_input:
                await message.reply_text("User cannot be empty.")
                return
            try:
                user_id = await resolve_user_id(client, user_input)
                user_label = user_input
            except Exception:
                await message.reply_text("Could not resolve user. Send @username, user ID, or forward a message from the user.")
                return
        else:
            await message.reply_text("Please send a user ID, username, or forward a message from the user.")
            return

        try:
            promote_admin_via_bot_api(user_id)
            await message.reply_text(f"Admin added: {user_label}")
        except PermissionError:
            await message.reply_text("cant add admin due to no rights")
        except Exception as e:
            await message.reply_text(f"Failed to add admin: {e}")

    elif action == "unpin":
        if message.reply_to_message:
            target_message = message.reply_to_message
            if getattr(target_message, "forward_from_chat", None):
                target_chat = target_message.forward_from_chat.id
                target_msg_id = target_message.forward_from_message_id
            else:
                target_chat = AUTOPOST_CHANNEL_ID
                target_msg_id = extract_message_id_from_link(target_message.text or "")
        elif message.text:
            target_chat = AUTOPOST_CHANNEL_ID
            target_msg_id = extract_message_id_from_link(message.text)
        else:
            await message.reply_text("Please send the message link, or reply/forward the pinned message.")
            return

        if not target_msg_id:
            await message.reply_text("Could not extract a message ID. Send the post link or forward/reply to the pinned message.")
            return

        try:
            await client.unpin_chat_message(target_chat, target_msg_id)
            await message.reply_text(f"Message {target_msg_id} unpinned.")
        except Exception as e:
            await message.reply_text(f"Failed to unpin message: {e}")

    elif action == "photo":
        is_photo = bool(message.photo) or bool(
            message.document and message.document.mime_type and message.document.mime_type.startswith("image/")
        )
        if not is_photo:
            await message.reply_text("Please send a photo only.")
            return

        photo_path = None
        try:
            fd, photo_path = tempfile.mkstemp(suffix=".jpg")
            os.close(fd)
            await message.download(file_name=photo_path)
            await client.set_chat_photo(AUTOPOST_CHANNEL_ID, photo=photo_path)
            await message.reply_text("Channel profile photo updated.")
        except Exception as e:
            await message.reply_text(f"Failed to update channel profile photo: {e}")
        finally:
            if photo_path:
                try:
                    os.unlink(photo_path)
                except OSError:
                    pass


@app.on_message(filters.command("change") & filters.user(AUTHORIZED_USERS))
async def change_command(client, message: Message):
    pending_changes.pop(message.from_user.id, None)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Channel name", callback_data="change_name")],
        [InlineKeyboardButton("Channel username", callback_data="change_username")],
        [InlineKeyboardButton("Channel description/bio", callback_data="change_description")],
        [InlineKeyboardButton("Channel profile photo", callback_data="change_photo")],
        [InlineKeyboardButton("Add admin", callback_data="change_add_admin")],
        [InlineKeyboardButton("Unpin message", callback_data="change_unpin")],
    ])

    await message.reply_text(
        "Choose what you want to change:",
        reply_markup=keyboard
    )


# =====================================================
# OWNER DM COMMANDS
# =====================================================

@app.on_message(filters.command("post") & filters.user(AUTHORIZED_USERS))
async def post_to_channel(client, message: Message):
    if len(message.command) > 1:
        text_to_send = message.text.split(None, 1)[1]
        try:
            await client.send_message(AUTOPOST_CHANNEL_ID, text_to_send)
            await message.reply_text("Message channel mein bhej diya gaya hai!")
        except Exception as e:
            await message.reply_text(f"Error: {e}")
    else:
        await message.reply_text("Command ke baad apna message likho.\nExample: /post Hello Channel!")


@app.on_message(filters.command("delete") & filters.user(AUTHORIZED_USERS))
async def dm_delete_command(client, message: Message):
    target_message = None

    if message.reply_to_message:
        target_message = message.reply_to_message
    else:
        parts = message.text.split(None, 1)
        if len(parts) < 2 or not parts[1].strip():
            await message.reply_text(
                "Reply to a forwarded post from the channel, or use:\n"
                "/delete <link to the post>"
            )
            return

        link = parts[1].strip()

        msg_id = None
        patterns = [
            r't\.me/[^/]+/(\d+)',
            r't\.me/c/(\d+)/(\d+)',
        ]
        for pat in patterns:
            m = re.search(pat, link)
            if m:
                if len(m.groups()) == 1:
                    msg_id = int(m.group(1))
                else:
                    msg_id = int(m.group(2))
                break

        if not msg_id:
            await message.reply_text("Could not extract a message ID from that link.")
            return

        try:
            await client.delete_messages(AUTOPOST_CHANNEL_ID, msg_id)
            await message.reply_text(f"Deleted message {msg_id} from the channel.")
            return
        except Exception as e:
            await message.reply_text(f"Failed to delete: {e}")
            return

    try:
        fwd = target_message
        src_chat = None
        src_msg_id = None

        if getattr(fwd, "forward_from_chat", None):
            src_chat = fwd.forward_from_chat.id
            src_msg_id = fwd.forward_from_message_id
        elif getattr(fwd, "forward_from_message_id", None) and getattr(fwd, "forward_signature", None):
            src_chat = AUTOPOST_CHANNEL_ID
            src_msg_id = fwd.forward_from_message_id

        if not src_chat or not src_msg_id:
            await message.reply_text(
                "Could not determine the source of that forwarded message.\n"
                "Try using the link instead: /delete <link>"
            )
            return

        await client.delete_messages(src_chat, src_msg_id)
        await message.reply_text(
            f"Deleted message {src_msg_id} from chat {src_chat}."
        )
    except Exception as e:
        await message.reply_text(f"Failed to delete: {e}")


@app.on_message(filters.command("pin") & filters.user(AUTHORIZED_USERS))
async def dm_pin_command(client, message: Message):
    target_msg_id = None
    is_silent = True

    if message.reply_to_message:
        fwd = message.reply_to_message
        if getattr(fwd, "forward_from_chat", None):
            target_chat = fwd.forward_from_chat.id
            target_msg_id = fwd.forward_from_message_id
        else:
            await message.reply_text(
                "Please reply to a message forwarded FROM the channel."
            )
            return
    else:
        parts = message.text.split(None, 1)
        if len(parts) < 2 or not parts[1].strip():
            await message.reply_text(
                "Usage:\n"
                "/pin <message text>  - sends and pins a new message\n"
                "/pin <link to a post>  - pins an existing post\n"
                "Or reply to a forwarded channel post with /pin"
            )
            return

        arg = parts[1].strip()

        msg_id = None
        m = re.search(r't\.me/[^/]+/(\d+)', arg)
        if not m:
            m = re.search(r't\.me/c/(\d+)/(\d+)', arg)
            if m:
                msg_id = int(m.group(2))
        else:
            msg_id = int(m.group(1))

        if msg_id:
            target_chat = AUTOPOST_CHANNEL_ID
            target_msg_id = msg_id
        else:
            try:
                sent = await client.send_message(
                    AUTOPOST_CHANNEL_ID, arg, parse_mode=ParseMode.HTML
                )
                target_chat = AUTOPOST_CHANNEL_ID
                target_msg_id = sent.id
            except Exception as e:
                await message.reply_text(f"Failed to send message: {e}")
                return

    if len(message.command) >= 2 and message.command[-1].lower() in ("notify", "loud"):
        is_silent = False

    try:
        await client.pin_chat_message(
            target_chat, target_msg_id, disable_notification=is_silent
        )
        mode = "silently" if is_silent else "with notification"
        await message.reply_text(f"Message {target_msg_id} pinned {mode}.")
    except Exception as e:
        await message.reply_text(f"Failed to pin: {e}")


@app.on_message(filters.private & filters.user(AUTHORIZED_USERS) & ~filters.regex(r"^/"))
async def change_response_handler(client, message: Message):
    user_id = message.from_user.id

    if user_id in pending_addchannel:
        await handle_addchannel_response(client, message)
        return

    if user_id in pending_changes:
        await handle_change_response(client, message)
        return


# =====================================================
# START
# =====================================================

async def main():
    load_channels()
    await app.start()

    await app.set_bot_commands([
        BotCommand("settings", "Autopost site settings (per-channel)"),
        BotCommand("channels", "List configured autopost channels"),
        BotCommand("addchannel", "Add a channel for autopost"),
        BotCommand("change", "Change channel info (name, username, description, photo)"),
        BotCommand("post", "Post a message to the channel"),
        BotCommand("delete", "Delete a post by link or forwarded reply"),
        BotCommand("pin", "Pin a message in the channel"),
    ])

    print("BOT STARTED")
    print(f"Configured channels: {list(channels_config['channels'].keys())}")

    asyncio.create_task(autopost_loop())
    await idle()


if __name__ == "__main__":
    app.run(main())