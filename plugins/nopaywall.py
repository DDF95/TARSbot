from pyrogram import Client, filters, enums

@Client.on_message(filters.command("paywall", "!"))
async def nopaywall(client, message):
    if not len(message.command) == 1:
        import urllib.parse

        escaped_link = urllib.parse.quote(message.command[1])
        
        await message.reply("https://12ft.io/proxy?q=" + escaped_link)
    else:
        await message.reply("Usage: `!paywall <link>`", parse_mode=enums.ParseMode.MARKDOWN)