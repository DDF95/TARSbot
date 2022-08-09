from pyrogram import Client, filters, enums


@Client.on_message(filters.command("glasses", "!"))
async def glasses(client, message):
    if not len(message.command) == 1:
        if "-" in message.text:
            if " - " not in message.text:
                message.text = message.text.replace("-", " - ")
                
            split_message = message.text[7 + 1:].split(" - ")
            phrase1 = split_message[0]
            phrase2 = split_message[1]
            
            await message.reply(phrase1 + "\n\n<code>(•_•)\n( •_•)>⌐■-■\n(⌐■_■)</code> " + phrase2)
        else:
            await message.reply("You forgot to put the hyphen '-' between the two phrases!")
    else:
        await message.reply(text="Usage: `!glasses <phrase1> - <phrase2>`", parse_mode=enums.ParseMode.MARKDOWN)
