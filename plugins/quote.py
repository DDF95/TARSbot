import random
from pyrogram import Client, filters
from datetime import datetime

async def get_author_name(message):
    if message.reply_to_message.forward_sender_name:
        return message.reply_to_message.forward_sender_name
    elif message.reply_to_message.forward_from:
        return message.reply_to_message.forward_from.first_name
    elif message.reply_to_message.from_user.first_name:
        return message.reply_to_message.from_user.first_name
    else:
        return "Unknown"

async def get_quote(message):
    if message.reply_to_message.text:
        return await spongebob_style(message.reply_to_message.text)
    elif message.reply_to_message.caption:
        return await spongebob_style(message.reply_to_message.caption)
    else:
        return f"Lmao {message.from_user.first_name}, I just shitted my pants."

async def spongebob_style(text):
    output_text = ""
    if random.randint(1, 5) == 1:  # 1 in 5 chance for SpongeBob text
        for char in text:
            if char.isalpha():
                if random.random() > 0.5:
                    output_text += char.upper()
                else:
                    output_text += char.lower()
            else:
                output_text += char
    else:
        output_text = text

    return output_text

@Client.on_message(filters.command("quote", "!"))
async def quotes(client, message):
    if message.reply_to_message:
        author = await get_author_name(message)
        quote = await get_quote(message)

        # Get the current date in the format 'dd/mm/yyyy'
        current_date = datetime.now().strftime("%d/%m/%Y")

        # Include the date after the author name in the reply
        reply_text = f"<i>\"{quote}\"</i>\n\n<b>- {author}</b>, {current_date}"

        await message.reply(reply_text)
    else:
        await message.reply("Usage: `!quote` in reply to a message")
