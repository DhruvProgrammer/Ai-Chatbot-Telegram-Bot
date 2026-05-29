# Yasir Bot

> A powerful, multi-model AI Telegram bot that acts as your group's intelligent assistant — capable of reading files, analyzing images, managing conversations, and publishing content to Telegraph.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-3.x-00ADD8?style=flat-square&logo=telegram&logoColor=white)
![NVIDIA](https://img.shields.io/badge/NVIDIA-API-76B900?style=flat-square&logo=nvidia&logoColor=white)
![Models](https://img.shields.io/badge/AI_Models-6-7C3AED?style=flat-square)

---

## Table of Contents

1. [Problem It Solves](#problem-it-solves)
2. [Features](#features)
3. [Architecture Overview](#architecture-overview)
4. [Supported AI Models](#supported-ai-models)
5. [Prerequisites](#prerequisites)
6. [Step-by-Step Setup](#step-by-step-setup)
7. [Configuration](#configuration)
8. [Bot Commands Reference](#bot-commands-reference)
9. [Usage Guide](#usage-guide)
10. [File Reading Capabilities](#file-reading-capabilities)
11. [Telegraph Publishing](#telegraph-publishing)
12. [Data Storage](#data-storage)
13. [Security Considerations](#security-considerations)
14. [Troubleshooting](#troubleshooting)
15. [Dependencies](#dependencies)
16. [Running as a Background Service](#running-as-a-background-service)
17. [License](#license)

---

## Problem It Solves

### The Challenge

Teams and communities using Telegram groups face several pain points when trying to leverage AI:

- **Fragmented tools** — Needing separate bots or apps for AI chat, file analysis, image recognition, and content publishing.
- **Single-model lock-in** — Most AI bots only support one model, limiting flexibility for different tasks (reasoning vs. coding vs. vision).
- **No group-level control** — Anyone can spam the bot in groups with no authorization mechanism.
- **Context loss** — Bots forget previous messages, requiring users to repeat context every time.
- **File analysis friction** — Having to copy-paste file contents manually instead of just sending the file.
- **Long responses break** — AI responses with code blocks or long text get mangled by Telegram's formatting limits.

### The Solution

Yasir Bot addresses all of these with a single, unified Telegram bot:

- **6 AI models** in one bot — switch per group based on the task at hand.
- **Group authorization** — only the bot owner can activate/deactivate the bot in groups.
- **Persistent conversation history** — per-user memory across messages with configurable depth.
- **Universal file reader** — send any supported file directly to the bot and get AI-powered analysis.
- **Vision support** — send images with questions and get intelligent descriptions using vision-capable models.
- **Telegraph integration** — publish AI responses, text, or images directly to Telegraph pages.
- **Smart MarkdownV2 formatting** — responses are properly formatted for Telegram with code blocks, bold, italic, and more.
- **Auto file generation** — the AI can create files (code, documents, PDFs) and send them back to the user.

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Model AI Chat** | Choose from 6 different AI models per group. Each model excels at different tasks — reasoning, coding, general chat, or multimodal analysis. |
| **Group Authorization** | Owner-controlled access. Only the bot owner can authorize which groups can use the bot. Unauthorized groups are completely ignored. |
| **File Reading & Analysis** | Send files directly to the bot. Supports 50+ file types including PDF, DOCX, XLSX, code files, and ZIP/TAR archives. |
| **Image Analysis** | Send photos with `/q` and get AI-powered descriptions using vision-capable models (Nemotron, Phi-4). |
| **Conversation Memory** | Per-user conversation history (up to 20 messages). The bot remembers context across messages for natural dialogue. |
| **Telegraph Publishing** | Publish text, code, or images to Telegraph with a single command. Supports image positioning (above/below text). |
| **File Generation** | The AI can create files in its response using a structured format. The bot extracts them and sends as downloadable attachments. |
| **Smart Formatting** | AI responses are automatically converted to Telegram MarkdownV2 with proper escaping, code blocks, bold, italic, and links. |

---

## Architecture Overview

```
 +------------------+       +------------------+       +------------------+
 |                  |       |                  |       |                  |
 |  Telegram User   |------>|  Telegram API    |------>|  Yasir Bot       |
 |  (Mobile/Web)    |       |  (Bot Server)    |       |  (Python/aiogram)|
 |                  |<------|                  |<------|                  |
 +------------------+       +------------------+       +--------+---------+
                                                                |
                                           +--------------------+--------------------+
                                           |                    |                    |
                                           v                    v                    v
                                  +-----------------+  +-----------------+  +-----------------+
                                  |                 |  |                 |  |                 |
                                  |  NVIDIA API     |  |  Telegraph API  |  |  data.json      |
                                  |  (6 AI Models)  |  |  (Publishing)   |  |  (Persistence)  |
                                  |                 |  |                 |  |                 |
                                  +-----------------+  +-----------------+  +-----------------+
```

### Component Breakdown

| Component | Technology | Purpose |
|-----------|------------|---------|
| Bot Framework | aiogram 3.x | Async Telegram bot framework handling commands, messages, callbacks |
| AI Backend | NVIDIA NIM API | Hosts and serves 6 different LLM models via unified API |
| HTTP Client | httpx | Async HTTP requests to AI API and Telegraph |
| Data Storage | JSON file | Persistent storage for groups, settings, conversations |
| Publishing | Telegraph API | Publish long-form content with images to Telegraph |
| PDF Processing | PyPDF2 / fpdf2 | Read PDF files and generate PDF output |
| Doc Processing | python-docx | Read Microsoft Word documents |
| Spreadsheet | openpyxl | Read Excel spreadsheets |

---

## Supported AI Models

All models are accessed through NVIDIA's unified API. Each group can independently select which model to use.

| Model | ID | Capabilities |
|-------|-----|-------------|
| **Nemotron 3 Nano** | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | Vision + Text |
| **DeepSeek V4 Flash** | `deepseek-ai/deepseek-v4-flash` | Text |
| **Mistral Large 675B** | `mistralai/mistral-large-3-675b-instruct-2512` | Text |
| **Llama 3.3 70B** | `meta/llama-3.3-70b-instruct` | Text |
| **Qwen3 Coder 480B** | `qwen/qwen3-coder-480b-a35b-instruct` | Text |
| **Phi-4 Multimodal** | `microsoft/phi-4-multimodal-instruct` | Vision + Text |

> **Note:** Vision models (Nemotron and Phi-4) support image analysis. When an image is sent, the bot automatically selects a vision-capable model regardless of the group's configured model.

---

## Prerequisites

- **Python 3.10 or higher** (tested on 3.14)
- **A Telegram Bot Token** — obtained from [@BotFather](https://t.me/BotFather)
- **NVIDIA API Key** — obtained from [NVIDIA NIM](https://build.nvidia.com/)
- **Your Telegram User ID** — get it from [@userinfobot](https://t.me/userinfobot)
- **A Telegram Channel** (optional) — for image hosting via `/post` command

---

## Step-by-Step Setup

### 1. Create Your Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Send `/newbot` and follow the prompts to name your bot.
3. Copy the **bot token** provided by BotFather (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`).
4. Optionally set commands via `/setcommands` in BotFather.

### 2. Get Your NVIDIA API Key

1. Go to [NVIDIA NIM](https://build.nvidia.com/) and create an account.
2. Navigate to the API keys section and generate a new key.
3. Copy the key (format: `nvapi-xxxxxxxxxxxxxxxxxxxx`).

### 3. Get Your Telegram User ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot).
2. Send any message to it.
3. It will reply with your numeric User ID (e.g., `5360075159`).

### 4. Install Python Dependencies

```bash
# Clone or download the bot files
mkdir yasir-bot && cd yasir-bot

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate       # Linux/Mac

# Install required packages
pip install aiogram httpx PyPDF2 fpdf2 python-docx openpyxl
```

### 5. Configure the Bot

Open `yasir.py` and update the following values at the top of the file:

```python
# Replace these with your actual values
BOT_TOKEN = "YOUR_BOT_TOKEN_FROM_BOTFATHER"
OWNER_ID = 123456789  # Your Telegram numeric user ID

# Replace the API key in each model entry
"api_key": "nvapi-YOUR_NVIDIA_API_KEY"
```

> ⚠️ **Security Warning** — Never commit your bot token or API keys to a public repository. Use environment variables or a `.env` file in production.

### 6. Set Up Image Channel (Optional)

For the `/post` command to publish images to Telegraph:

1. Create a new Telegram channel (can be private).
2. Add your bot as an **administrator** with post permissions.
3. Forward a message from the channel to [@userinfobot](https://t.me/userinfobot) to get the channel ID.
4. Send `/setchannel -100XXXXXXXXXX` to your bot in private chat.

### 7. Run the Bot

```bash
python yasir.py
```

You should see output like:

```
2026-05-29 10:00:00 [INFO] yasir-bot: Bot started: @YourBotName (id=123456789)
2026-05-29 10:00:00 [INFO] yasir-bot: Owner ID: 5360075159
2026-05-29 10:00:00 [INFO] yasir-bot: Authorized groups: 0
2026-05-29 10:00:00 [INFO] yasir-bot: Image channel: Not set
2026-05-29 10:00:00 [INFO] yasir-bot: Bot is running!
```

---

## Configuration

All configuration is done at the top of `yasir.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `BOT_TOKEN` | — | Your Telegram bot token from @BotFather |
| `OWNER_ID` | — | Your Telegram numeric user ID (admin of the bot) |
| `NVIDIA_API_URL` | `https://integrate.api.nvidia.com/v1/chat/completions` | NVIDIA NIM API endpoint |
| `PROXY_URL` | `""` | HTTP proxy URL for API calls (leave empty if not needed) |
| `DEFAULT_MODEL` | `"nemotron"` | Default AI model for new groups and private chats |
| `MAX_HISTORY` | `20` | Maximum conversation history messages per user |
| `DATA_FILE` | `data.json` | Path to the persistent data file (auto-created) |
| `IMAGE_CHANNEL_ID` | — | Telegram channel ID for image hosting (set via `/setchannel`) |

### Adding or Modifying Models

Edit the `MODELS` dictionary to add new models or change existing ones:

```python
MODELS = {
    "mymodel": {
        "name": "Display Name",        # Shown in /settings keyboard
        "model": "provider/model-id",  # NVIDIA model identifier
        "api_key": "nvapi-xxxxx",       # API key for this model
        "vision": False,               # True if model supports images
    },
}
```

---

## Bot Commands Reference

### User Commands (Everyone)

| Command | Where | Description |
|---------|-------|-------------|
| `/start` | Private / Group | Welcome message with basic instructions |
| `/q <question>` | Private / Group | Ask the AI a question. Supports replying to messages, files, and photos. |
| `/question <text>` | Private / Group | Alias for `/q` |
| `/post` | Private / Group | Publish text or images to Telegraph. Reply to a message or provide text as argument. |
| `/clearhistory` | Private / Group | Clear your personal conversation history |
| `/model` | Group | Show the current AI model for this group |
| `/help` | Private / Group | Show the full help message with all commands |

### Owner Commands (Bot Admin Only)

| Command | Where | Description |
|---------|-------|-------------|
| `/authorize` | Group | Activate the bot in the current group |
| `/deauthorize` | Group | Deactivate the bot in the current group |
| `/unauthorize` | Group | Alias for `/deauthorize` |
| `/settings` | Group | Open the AI model selection keyboard |
| `/setchannel <ID>` | Private | Set the Telegram channel for image hosting |
| `/clearallhistory` | Private / Group | Clear conversation history for ALL users |

---

## Usage Guide

### Private Chat (Owner)

The bot owner can chat directly with the bot in DM without any commands. Just send a message and the AI responds.

### Private Chat (Other Users)

Other users must use `/q` followed by their question:

```
/q What is the capital of France?
```

### Group Chat

The bot responds in groups only when:

- You **@mention** the bot: `@YourBotName what is Python?`
- You **reply** to one of the bot's messages

Regular messages are ignored to avoid spam.

### Asking About Files

```bash
# Send a file and reply to it with:
/q Summarize this document

# Or send a file with a caption starting with /q:
/q Explain this code line by line
```

### Asking About Images

```bash
# Reply to a photo with:
/q What do you see in this image?

# Send a photo with caption:
/q Describe the objects in this photo
```

### Replying to Messages

```bash
# Reply to any message with /q to ask about it:
/q Can you explain this in simpler terms?
```

---

## File Reading Capabilities

The bot can read and analyze a wide variety of file types. Send the file directly to the bot (or reply to it with `/q`).

### Text & Code Files

| Category | Extensions |
|----------|------------|
| Programming Languages | `.py` `.js` `.ts` `.jsx` `.tsx` `.java` `.kt` `.swift` `.c` `.cpp` `.h` `.cs` `.go` `.rs` `.rb` `.php` `.dart` `.scala` `.lua` `.r` `.ex` `.exs` `.hs` |
| Web Technologies | `.html` `.htm` `.css` `.scss` `.sass` `.less` `.vue` `.svelte` `.astro` |
| Data & Config | `.json` `.xml` `.yaml` `.yml` `.toml` `.ini` `.cfg` `.conf` `.env` `.properties` |
| Documentation | `.txt` `.md` `.markdown` `.rst` `.tex` `.log` `.csv` `.tsv` `.sql` |
| Shell & Scripts | `.sh` `.bash` `.zsh` `.bat` `.cmd` `.ps1` `.psm1` |
| Infrastructure | `.dockerfile` `.makefile` `.cmake` `.gradle` `.gitignore` `.dockerignore` `.htaccess` `.nginx` `.apache` |

### Binary Documents

| Format | Extensions | Notes |
|--------|------------|-------|
| PDF | `.pdf` | Text extracted using PyPDF2 |
| Word | `.docx` `.doc` | Requires `python-docx` |
| Excel | `.xlsx` `.xls` | Requires `openpyxl` |

### Archives

| Format | Extensions | Notes |
|--------|------------|-------|
| ZIP | `.zip` | Lists contents + reads embedded text files |
| TAR | `.tar` `.gz` `.tgz` `.bz2` `.xz` | Lists contents + reads embedded text files |

> **File Size Limit** — Maximum file size is **20 MB**. Archive reading is limited to 50 file listings and 20 text file contents. Content is truncated at 12,000 characters.

---

## Telegraph Publishing

The `/post` command publishes content to [Telegraph](https://telegra.ph) — a lightweight blogging platform by Telegram.

### Usage Examples

```bash
# Publish text directly
/post Hello World! This is my first Telegraph post.

# Publish AI response: reply to any bot message with /post

# Publish a photo with text (image appears above text by default)
# Reply to a photo with /post and optional caption
/post Check out this image!

# Publish with image below text
/post --below Here is my analysis of this chart.
```

### Image Positioning

| Flag | Behavior |
|------|----------|
| (default) | Image appears **above** the text |
| `--below` | Image appears **below** the text |

---

## Data Storage

The bot uses a single `data.json` file for all persistent data:

```json
{
  "owner_id": 5360075159,
  "authorized_groups": {
    "-1001234567890": {
      "title": "My Group",
      "authorized_at": "2026-05-29T10:00:00",
      "authorized_by": 5360075159
    }
  },
  "group_models": {
    "-1001234567890": "mistral"
  },
  "conversations": {
    "123456789": [
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi! How can I help?"}
    ]
  },
  "telegraph_token": "abc123...",
  "image_channel_id": -1003707695999
}
```

> ⚠️ **Backup Recommendation** — Regularly back up `data.json`. It contains conversation history, group settings, and API tokens.

---

## Security Considerations

> ⚠️ **Important** — Review these security points before deploying.

- **Hardcoded credentials** — The bot token and API keys are currently hardcoded in `yasir.py`. For production, use environment variables or a `.env` file with `python-dotenv`.
- **Owner-only access** — Only the user matching `OWNER_ID` can authorize groups, change models, and manage settings. Keep your User ID private.
- **Group authorization** — The bot ignores all messages in unauthorized groups. Always authorize only trusted groups.
- **File size limits** — Files are capped at 20MB to prevent abuse. Content is truncated at 12,000 characters.
- **No rate limiting** — The bot does not implement per-user rate limiting. Consider adding it for public deployments.
- **Temporary files** — Downloaded files are stored temporarily and deleted after processing. Ensure the temp directory has adequate space.

### Recommended: Use Environment Variables

```bash
# .env file
BOT_TOKEN=5278733059:AAG0RI7zsuCfDCq1g8xb23jdtgopoeCy_LE
OWNER_ID=5360075159
NVIDIA_API_KEY=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
```

```python
# In yasir.py, replace hardcoded values:
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot doesn't respond in group | Make sure you ran `/authorize` in the group as the owner. Check that the bot is a member of the group. |
| Bot doesn't respond to DMs | Only the owner can chat freely in DM. Other users must use `/q` command. |
| AI API error (401) | Your NVIDIA API key is invalid or expired. Generate a new one at [NVIDIA NIM](https://build.nvidia.com/). |
| AI API error (429) | Rate limit exceeded. Wait a few minutes and try again. |
| AI request timed out | The model is overloaded. Try switching to a different model via `/settings`. |
| Markdown formatting broken | The bot auto-escapes MarkdownV2. If responses still break, the AI may be generating incompatible formatting. The bot has a fallback to send unformatted text. |
| File not supported | Check the supported extensions list above. Files larger than 20MB are rejected. |
| `/post` fails | Make sure you set the image channel via `/setchannel` and the bot is admin in that channel. |
| `data.json` corrupted | Delete `data.json` and restart the bot. It will create a fresh file. You'll lose conversation history and authorized groups. |
| Missing Python packages | Run `pip install aiogram httpx PyPDF2 fpdf2 python-docx openpyxl` |

---

## Dependencies

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| `aiogram` | 3.x | Telegram bot framework | Yes |
| `httpx` | latest | Async HTTP client for API calls | Yes |
| `PyPDF2` | latest | Read PDF files | Yes |
| `fpdf2` | latest | Generate PDF files from AI responses | Yes |
| `python-docx` | latest | Read Word documents (.docx) | Optional |
| `openpyxl` | latest | Read Excel spreadsheets (.xlsx) | Optional |
| `python-dotenv` | latest | Load .env files (recommended for production) | Optional |

```bash
# Quick install all
pip install aiogram httpx PyPDF2 fpdf2 python-docx openpyxl python-dotenv

# Minimal install (no Excel/Word support)
pip install aiogram httpx PyPDF2 fpdf2
```

---

## Project Structure

```
yasir-bot/
├── yasir.py              # Main bot file (all logic)
├── data.json             # Auto-generated persistent data
├── .env                  # Optional: environment variables
├── requirements.txt      # Python dependencies
├── README.md             # This documentation
└── venv/                 # Python virtual environment (optional)
```

### Generating requirements.txt

```bash
pip freeze > requirements.txt
```

---

## Running as a Background Service

### Linux (systemd)

```ini
# /etc/systemd/system/yasir-bot.service
[Unit]
Description=Yasir Telegram AI Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/yasir-bot
ExecStart=/path/to/yasir-bot/venv/bin/python yasir.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable yasir-bot
sudo systemctl start yasir-bot
sudo systemctl status yasir-bot
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create a new task triggered at system startup
3. Action: Start a program → `python.exe` with argument `yasir.py`
4. Set "Start in" to the bot's directory
5. Enable "Run whether user is logged on or not"

### Screen / tmux (Quick & Dirty)

```bash
# Using screen
screen -S yasir-bot
python yasir.py
# Press Ctrl+A, then D to detach

# Reattach later
screen -r yasir-bot
```

---

## License

This project is provided as-is for personal use. Modify and distribute as needed. No warranty provided.

---

**Yasir Bot** — Built with Python, aiogram, and NVIDIA AI

Contact: [@itznik_x](https://t.me/itznik_x)
