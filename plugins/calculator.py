from pyrogram import Client, filters, enums

@Client.on_message(filters.command("calc", "!"))
async def calc(client, message):
    if not len(message.command) == 1:
        import urllib.parse
        escaped_text = urllib.parse.quote(message.text[4 + 1:])

        import requests
        try:
            r = requests.get('https://api.mathjs.org/v4/?expr=' + escaped_text)

            await message.reply(text=f"`{r.text}`")
        except Exception as e:
            print(e)
            await message.reply(f"Error:\n`{e}`")
    else:
        await message.reply(text="Usage: `!calc <expression>`", parse_mode=enums.ParseMode.MARKDOWN)