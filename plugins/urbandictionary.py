from pyrogram import Client, filters, enums


@Client.on_message(filters.command("ud", "!"))
async def ud(client, message):
    if not len(message.command) == 1:
        import urllib.parse
        escaped_text = urllib.parse.quote(message.text[2+1:])

        try:
            import requests
            r = requests.get('http://api.urbandictionary.com/v0/define?term=' + escaped_text)
            
            if r.json()['list']:
                word = r.json()['list'][0]['word']
                definition = r.json()['list'][0]['definition']
                example = r.json()['list'][0]['example']

                await message.reply(
                    text=f"**{word}**\n{definition}\n\nExamples:\n__{example}__",
                    parse_mode = enums.ParseMode.MARKDOWN
                )
            else:
                await message.reply('No results found!')
        except Exception as e:
            await message.reply(f"Error:\n<code>{e}</code>")
    else:
        await message.reply(text="Usage: `!ud <word>`", parse_mode=enums.ParseMode.MARKDOWN)