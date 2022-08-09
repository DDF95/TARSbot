from pyrogram import Client, filters, enums

@Client.on_message(filters.command("qr", "!"))
async def qrcode(client, message):
    if not len(message.command) == 1:
        import urllib.parse

        escaped_text = urllib.parse.quote(message.text[2+1:])

        try:
            await message.reply_photo("https://api.qrserver.com/v1/create-qr-code/?size=500x500&data=" + escaped_text)
        except Exception as e:
            print(e)
            await message.reply(f"Error:\n<code>{e}</code>")
    else:
        await message.reply(text="Usage: `!qr <text>`", parse_mode=enums.ParseMode.MARKDOWN)