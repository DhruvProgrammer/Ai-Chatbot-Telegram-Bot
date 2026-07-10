with open('yasir.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the entire cmd_deauthorize function
import re

# Find the deauthorize function
start = content.find('async def cmd_deauthorize')
end = content.find('async def cmd_settings')

old_func = content[start:end]

# New clean deauthorize function
new_deauth = '''async def cmd_deauthorize(message: Message):
    if not is_owner(message.from_user.id):
        await message.answer(f"Only the bot owner can deauthorize{_DOT_HTML}", parse_mode=ParseMode.HTML)
        return

    command_parts = message.text.split() if message.text else []
    target_arg = command_parts[1] if len(command_parts) > 1 else None
    
    # Reply to a user to deauthorize them globally
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        if target.id == bot.id:
            await message.answer(f"Cannot deauthorize the bot{_DOT_HTML}", parse_mode=ParseMode.HTML)
            return
        deauthorize_user(target.id)
        name = target.first_name or target.username or str(target.id)
        await message.answer(
            f"User <b>{escape_html(name)}</b> has been globally deauthorized{_EXC_HTML}",
            parse_mode=ParseMode.HTML,
        )
        return
    
    # If target argument provided
    if target_arg:
        # Try username (with or without @)
        if target_arg.startswith("@") or (target_arg.replace(".", "").isalnum() and not target_arg.isdigit()):
            # This is likely a username, try to resolve it
            # We need to check if user is in authorized_users
            username = target_arg.lstrip("@").lower()
            found = False
            for uid, data in db.get("authorized_users", {}).items():
                # We don't store username, so we can't easily lookup by username
                # This would require a user lookup, which we can't do without API
                pass
            # Fall through to user ID check
        
        # Try user ID
        try:
            user_id = int(target_arg)
            if deauthorize_user(user_id):
                await message.answer(
                    f"User <code>{user_id}</code> has been globally deauthorized{_EXC_HTML}",
                    parse_mode=ParseMode.HTML,
                )
            else:
                await message.answer(f"User <code>{user_id}</code> was not authorized{_EXC_HTML}", parse_mode=ParseMode.HTML)
            return
        except ValueError:
            pass
    
    # In DM with a group ID
    if message.chat.type == ChatType.PRIVATE and target_arg:
        try:
            group_id = int(target_arg)
            chat_id_str = str(group_id)
            
            if chat_id_str not in db["authorized_groups"]:
                await message.answer(f"Group <code>{group_id}</code> is not authorized{_DOT_HTML}", parse_mode=ParseMode.HTML)
                return
            
            del db["authorized_groups"][chat_id_str]
            db["group_models"].pop(chat_id_str, None)
            db["conversations"].pop(chat_id_str, None)
            save_data(db)
            
            await message.answer(f"Group <code>{group_id}</code> has been deauthorized{_EXC_HTML}", parse_mode=ParseMode.HTML)
            return
        except ValueError:
            pass
    
    # In a group - deauthorize the group itself
    if message.chat.type != ChatType.PRIVATE:
        chat_id = str(message.chat.id)
        chat_title = escape_html(message.chat.title or chat_id)
        
        if chat_id not in db["authorized_groups"]:
            await message.answer(f"Group <b>{chat_title}</b> is not authorized{_DOT_HTML}", parse_mode=ParseMode.HTML)
            return
        
        del db["authorized_groups"][chat_id]
        db["group_models"].pop(chat_id, None)
        db["conversations"].pop(chat_id, None)
        save_data(db)
        
        await message.answer(f"Group <b>{chat_title}</b> has been deauthorized{_EXC_HTML}", parse_mode=ParseMode.HTML)
        return
    
    await message.answer(
        f"Usage:\\n"
        f"- <code>/deauthorize</code> in a group - Deauthorize the group\\n"
        f"- <code>/deauthorize <group_id></code> in DM - Deauthorize a group by ID\\n"
        f"- Reply to a user with <code>/deauthorize</code> - Globally deauthorize that user",
        parse_mode=ParseMode.HTML,
    )

'''

# Replace the old function
start = content.find('async def cmd_deauthorize')
end = content.find('async def cmd_settings')
content = content[:content.find('async def cmd_deauthorize')] + new_deauth + content[content.find('async def cmd_settings'):]

with open('yasir.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed deauthorize function")