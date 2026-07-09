# Project Memory — yasir.py Telegram Bot

## Project Overview
- **File**: `yasir.py` — AI-powered Telegram bot built with `aiogram`
- **Purpose**: Multi-model AI chatbot with group management, web search, file reading, and leech-bot-style authorization
- **Stack**: Python, aiogram (async Telegram framework), httpx, NVIDIA API, Tavily, PyPDF2
- **Working Dir**: `C:\Users\MR.PC\Desktop\baloch`
- **Python**: Python 3.14 at `C:\Users\MR.PC\AppData\Local\Programs\Python\Python314\python.exe`
- **OS**: Windows (PowerShell 5.1)

## Authorization Architecture (Leech Bot Style)
Reference repo: https://github.com/SilentDemonSD/WZML-X

### 3-Tier Permission System
1. **Owner** (`OWNER_ID = 5360075159`) → Can use bot anywhere without authorization
2. **Globally Authorized Users** → Stored in `db["authorized_users"]`, can use bot in any chat (DM + groups)
3. **Group-Authorized** → Members of an authorized group (`db["authorized_groups"]`) can only use bot in that group

### Key Authorization Functions (yasir.py:241-288)
- `_is_owner(user_id)` — owner check (defined before `is_owner()` to avoid forward-ref issues)
- `is_owner(user_id)` — original owner check (yasir.py:936)
- `authorize_user(user_id, authorized_by)` — adds to global authorized users
- `deauthorize_user(user_id)` — removes from global authorized users
- `is_user_authorized(user_id)` — checks global authorized users
- `can_use_bot(user_id, chat_id)` — main permission check (owner OR global user OR authorized group)
- `is_authorized_group(chat_id)` — checks if group is authorized
- `is_authorized(chat_id, user_id=None)` — backwards-compat wrapper; passes user_id → `can_use_bot`

### Authorization Commands
- `/authorize` in group → authorizes the group
- `/authorize <group_id>` in DM → authorizes group by ID
- Reply to a user with `/authorize` → globally authorizes that user
- `/deauthorize` in group → deauthorizes the group
- `/deauthorize <group_id>` in DM → deauthorizes group by ID
- Reply to a user with `/deauthorize` → globally deauthorizes that user
- No sudo users (only owner + authorized users)

### Data Structure (data.json)
```python
{
    "owner_id": OWNER_ID,
    "authorized_groups": {chat_id: {title, authorized_at, authorized_by}},
    "authorized_users": {user_id: {authorized_by, authorized_at}},  # NEW
    "group_models": {chat_id: model_key},
    "conversations": {user_id: [{role, content}]},
    "telegraph_token": None,
    "image_channel_id": None,
    "bot_alias": None,
    "setname_enabled": True,
    "user_instructions": {user_id: instruction},
}
```

## Bot Features

### AI Models (11 total)
nemotron (default, vision), deepseek, mistral, llama, qwen, phi (vision),
kimi, mistral-medium, minimax, gpt-oss (vision)

### Commands
- `/q <question>` — ask AI (supports replied files/images)
- `/search <query>` — Tavily web search + AI answer
- `/translate <lang> <text>` — NVIDIA riva-translate
- `/safety <text>` — content safety check
- `/post` — publish to Telegraph (supports images, --below flag)
- `/setname` — set bot alias name (inline keyboard menu)
- `/settings` — owner-only model selection
- `/model` — show current group model
- `/instruction` — per-user custom prompt
- `/setchannel` — set image channel ID (owner, DM only)
- `/clearhistory`, `/clearallhistory` (owner)
- `/authorize`, `/deauthorize`, `/unauthorize` (owner)

### Cancel Button Feature
- `active_requests = {}` — {message_id: {user_id, cancelled, chat_id}}
- `CANCEL_AI = "cancel:ai"` callback data constant
- `send_ai_response()` sends inline keyboard with "Cancel" button
- `cb_cancel_ai()` callback handler — only initiator can cancel
- On cancel: thinking message deleted, no AI response sent

### Alias-Based File Reading
- `handle_message()` checks for documents/photos when alias/mention is triggered
- Documents: downloaded, read (txt/pdf/docx/xlsx/zip), content appended to user_text
- Photos: downloaded as base64, sent to vision model
- Works same as `/q` with replied files

## Environment Setup
- PowerShell commands use `;` (not `&&`)
- Set UTF-8 encoding: `$env:PYTHONIOENCODING='utf-8'; python script.py`
- Syntax check: `python -c "compile(open('yasir.py', encoding='utf-8').read(), 'yasir.py', 'exec'); print('Syntax OK')"`
- Run bot: `python yasir.py`
- Temp files: `C:\Users\MR.PC\AppData\Local\Temp\opencode\`

## Known Issues / Notes
- API keys and bot token are hardcoded in the file (security concern)
- `db` loaded globally at startup; not thread/process safe for multi-worker
- `MemoryStorage` used for FSM — lost on restart
- Duplicate import of `ChatType, ParseMode` (lines 14 and 29) — cosmetic only
- `is_authorized(chat_id)` without user_id still works (checks group only, used in handle_photo_with_caption for model downgrade logic)
- `_is_owner()` defined early to avoid forward-reference issues since `is_owner()` is defined later (line 936)

## Change History
- Added leech-bot authorization architecture (owner/global users/groups)
- Added cancel button during AI thinking (inline keyboard, initiator-only)
- Fixed alias-based PDF/document reading
- Updated `/authorize` and `/deauthorize` for DM group auth + user auth via reply
- Updated all permission checks to use new auth system
- Updated help text and command descriptions
