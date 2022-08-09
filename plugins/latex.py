from pyrogram import Client, filters, enums


# TODO: maybe there is a more efficient way to do this?
@Client.on_message(filters.command("latex", "!"))
async def latex(client, message):
    if len(message.command) == 1:
        await message.reply("Usage: `!latex <latex code>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        import urllib.parse
        escaped_text = urllib.parse.quote("\dpi{1000}" + message.text[1+5+1:])
        
        import requests
        try:
            r = requests.get("https://latex.codecogs.com/png.image?" + escaped_text).content

            from PIL import Image, ImageOps
            from io import BytesIO
            with Image.open(BytesIO(r)) as im:
                bordered_image = ImageOps.expand(im, border=50, fill=(255, 255, 255))
                
                output = BytesIO()
                bordered_image.save(output, format='PNG')

                await message.reply_photo(photo=output)
        except Exception as e:
            print(e)
            await message.reply(f"Error: <code>{e}</code>")