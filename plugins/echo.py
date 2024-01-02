from pyrogram import Client, filters, enums


@Client.on_message(filters.command("echo", "!"))
async def echo(client, message):
    if len(message.command) == 1:
        if message.reply_to_message:
            if message.reply_to_message.text:
                await client.send_message(chat_id=message.chat.id, text=message.reply_to_message.text)
            elif message.reply_to_message.caption:
                await client.send_message(chat_id=message.chat.id, caption=message.reply_to_message.caption)
            else:
                await message.reply("Error: I can't echo this!")
        else:
            await message.reply(text="Usage: `!echo <text>` or `!echo` in reply to a message", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        await client.send_message(chat_id=message.chat.id, text=message.text[4+1:])


@Client.on_message(filters.command("echo-nw", "!"))
async def echo_no_web(client, message):
    if len(message.command) == 1:
        if message.reply_to_message:
            if message.reply_to_message.text:
                await client.send_message(chat_id=message.chat.id, text=message.reply_to_message.text, disable_web_page_preview=True)
            elif message.reply_to_message.caption:
                await client.send_message(chat_id=message.chat.id, caption=message.reply_to_message.caption, disable_web_page_preview=True)
            else:
                await message.reply("Error: I can't echo this!")
        else:
            await message.reply(text="Usage: `!echo <text>` or `!echo` in reply to a message", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        await client.send_message(chat_id=message.chat.id, text=message.text[4+3+1:], disable_web_page_preview=True)