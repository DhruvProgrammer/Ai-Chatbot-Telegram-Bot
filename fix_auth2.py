with open('yasir.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the entire cmd_authorize function with a clean version
old_start = content.find('async def cmd_authorize(message: Message):')
end = content.find('async def cmd_deauthorize')

# Build the clean function
new_func = '''async def cmd_authorize(message: Message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        await message.answer(f"Only the bot owner can authorize{_DOT_HTML}", parse_mode=ParseMode.HTML)
        return
    
    command_parts = message.text.split() if message.text else []
    target_arg = command_parts[1] if len(command_parts) > 1 else None
    
    # If replying to a user's message, authorize that user globally
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        if target.id == bot.id:
            await message.answer(f"Cannot authorize the bot itself{_DOT_HTML}", parse_mode=ParseMode.HTML)
            return
        authorize_user(target.id, user_id)
        name = target.first_name or target.username or str(target.id)
        await message.answer(
            f"User <b>{escape_html(name)}</b> (ID: <code>{target.id}</code>) has been globally authorized{_EXC_HTML}\\n"
            f"They can now use the bot in DM and any group where I'm present{_EXC_HTML}",
            parse_mode=ParseMode.HTML,
        )
        return
    
    # Parse argument for user or group
    if target_arg:
        # Try to parse as username (with or without @)
        if target_arg.startswith("@") or (target_arg.replace("_", "").isalnum() and not target_arg.isdigit()):
            username = target_arg.lstrip("@")
            try:
                chat = await bot.get_chat(username)
                if chat.type == ChatType.PRIVATE:
                    if chat.id == bot.id:
                        await message.answer(f"Cannot authorize the bot itself{_DOT_HTML}", parse_mode=ParseMode.HTML)
                        return
                    authorize_user(chat.id, user_id)
                    name = chat.first_name or chat.username or str(chat.id)
                    await message.answer(
                        f"User <b>{escape_html(name)}</b> (ID: <code>{chat.id}</code>) has been globally authorized{_EXC_HTML}\\n"
                        f"They can now use the bot in DM and any group where I'm present{_EXC_HTML}",
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    await message.answer(f"Usernames only work for users, not groups/channels{_DOT_HTML}", parse_mode=ParseMode.HTML)
                return
            except Exception as e:
                await message.answer(f"Could not resolve username <code>{escape_html(username)}</code>{_DOT_HTML} {escape_html(str(e))}", parse_mode=ParseMode.HTML)
                return
        
        # Try numeric argument
        if target_arg.lstrip("-").isdigit():
            target_id = int(target_arg)
            
            # If positive ID, try to resolve as user first (could be group)
            if target_id > 0:
                try:
                    chat = await bot.get_chat(target_id)
                    if chat.type == ChatType.PRIVATE:
                        if chat.id == bot.id:
                            await message.answer(f"Cannot authorize the bot itself{_DOT_HTML}", parse_mode=ParseMode.HTML)
                            return
                        authorize_user(chat.id, user_id)
                        name = chat.first_name or chat.username or str(chat.id)
                        await message.answer(
                            f"User <b>{escape_html(name)}</b> (ID: <code>{chat.id}</code>) has been globally authorized{_EXC_HTML}\\n"
                            f"They can now use the bot in DM and any group where I'm present{_EXC_HTML}",
                            parse_mode=ParseMode.HTML,
                        )
                    else:
                        # It's a group/channel
                        if message.chat.type == ChatType.PRIVATE:
                            chat_id_str = str(target_id)
                            if chat_id_str in db["authorized_groups"]:
                                await message.answer(f"Group is already authorized{_DOT_HTML}", parse_mode=ParseMode.HTML)
                                return
                            
                            db["authorized_groups"][chat_id_str] = {
                                "title": f"Group {target_id}",
                                "authorized_at": datetime.now().isoformat(),
                                "authorized_by": user_id,
                            }
                            db["group_models"][chat_id_str] = DEFAULT_MODEL
                            save_data(db)
                            
                            await message.answer(
                                f"Group <code>{target_id}</code> has been authorized{_EXC_HTML}\\n"
                                f"Current AI model: <b>{escape_html(MODELS[DEFAULT_MODEL]['name'])}</b>",
                                parse_mode=ParseMode.HTML,
                            )
                        else:
                            await message.answer(f"Use <code>/authorize</code> in DM to authorize groups by ID{_DOT_HTML}", parse_mode=ParseMode.HTML)
                        return
                except Exception:
                    # If get_chat fails, assume it's a user ID
                    authorize_user(target_id, user_id)
                    await message.answer(
                        f"User <code>{target_id}</code> has been globally authorized{_EXC_HTML}\\n"
                        f"They can now use the bot in DM and any group where I'm present{_EXC_HTML}",
                        parse_mode=ParseMode.HTML,
                    )
                return
            
            # Negative ID = group
            else:
                if message.chat.type == ChatType.PRIVATE:
                    group_id = abs(target_id)
                    chat_id_str = str(group_id)
                    if chat_id_str in db["authorized_groups"]:
                        await message.answer(f"Group is already authorized{_DOT_HTML}", parse_mode=ParseMode.HTML)
                        return
                    
                    db["authorized_groups"][chat_id_str] = {
                        "title": f"Group {group_id}",
                        "authorized_at": datetime.now().isoformat(),
                        "authorized_by": user_id,
                    }
                    db["group_models"][chat_id_str] = DEFAULT_MODEL
                    save_data(db)
                    
                    await message.answer(
                        f"Group <code>{group_id}</code> has been authorized{_EXC_HTML}\\n"
                        f"Current AI model: <b>{escape_html(MODELS[DEFAULT_MODEL]['name'])}</b>",
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    await message.answer(f"Use <code>/authorize</code> in DM to authorize groups by ID{_DOT_HTML}", parse_mode=ParseMode.HTML)
                return
        
        await message.answer(f"Invalid argument{_DOT_HTML} Use <code>/authorize @username</code> or <code>/authorize <user_id></code> or reply to user{_DOT_HTML}", parse_mode=ParseMode.HTML)
        return
    
    # In a group - authorize the group itself
    if message.chat.type != ChatType.PRIVATE:
        chat_id = str(message.chat.id)
        chat_title = escape_html(message.chat.title or chat_id)
        
        if chat_id in db["authorized_groups"]:
            await message.answer(f"Group <b>{chat_title}</b> is already authorized{_DOT_HTML}", parse_mode=ParseMode.HTML)
            return
        
        db["authorized_groups"][chat_id] = {
            "title": message.chat.title or chat_id,
            "authorized_at": datetime.now().isoformat(),
            "authorized_by": user_id,
        }
        db["group_models"][chat_id] = DEFAULT_MODEL
        save_data(db)
        
        model_name = escape_html(MODELS[DEFAULT_MODEL]["name"])
        await message.answer(
            f"Group <b>{chat_title}</b> has been authorized{_EXC_HTML}\\n"
            f"Current AI model: <b>{model_name}</b>\\n"
            f"Use /settings to change the model{_DOT_HTML}",
            parse_mode=ParseMode.HTML,
        )
        return
    
    await message.answer(
        f"Usage:\\n"
        f"- <code>/authorize</code> in a group - Authorize the group\\n"
        f"- <code>/authorize @username</code> or <code>/authorize <user_id></code> in DM - Globally authorize a user\\n"
        f"- Reply to a user with <code>/authorize</code> - Globally authorize that user",
        parse_mode=ParseMode.HTML,
    )

'''

# Replace the function
start = content.find('async def cmd_authorize(message: Message):')
end = content.find('async def cmd_deauthorize')
content = content[:content.find('async def cmd_authorize')] + new_func + content[content.find('async def cmd_deauthorize'):]

with open('yasir.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed authorize function")