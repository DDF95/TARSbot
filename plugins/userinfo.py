from pyrogram import Client, enums, filters


@Client.on_message(filters.command("id", "!"))
async def user_info(client, message):
    if len(message.command) == 1:
        if message.reply_to_message:
            if message.chat.type == enums.ChatType.GROUP or message.chat.type == enums.ChatType.SUPERGROUP:
                await message.reply(f"{message.reply_to_message.from_user.first_name}'s ID is: `{str(message.reply_to_message.from_user.id)}`\n\nGroup ID: `{str(message.chat.id)}`")
            else:
                await message.reply(f"{message.reply_to_message.from_user.first_name}'s ID is: `{str(message.reply_to_message.from_user.id)}`")
        else:
            user_id = f"Your ID is: `{str(message.from_user.id)}`"

            if message.chat.type == enums.ChatType.PRIVATE or message.chat.type == enums.ChatType.BOT:
                await message.reply(user_id)
            elif message.chat.type == enums.ChatType.GROUP or message.chat.type == enums.ChatType.SUPERGROUP:
                await message.reply(f"{user_id}\n\nGroup ID: `{str(message.chat.id)}`")
            elif message.chat.type == enums.ChatType.CHANNEL:
                await message.reply(f"{user_id}\n\nChannel ID: `{str(message.chat.id)}`")
    elif len(message.command) == 2:
        try:
            user_to_search = await client.get_users(user_ids=message.command[1])
            if user_to_search:
                await message.reply(f"{user_to_search.first_name}'s ID is: `{str(user_to_search.id)}`")
        except Exception as e:
            print(e)
            await message.reply("User not found!")
            # TODO: better error handling
