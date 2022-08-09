from pyrogram import Client, filters

@Client.on_message(filters.command("cat", "!"))
async def cat(client, message):
    import requests

    try:
        r = requests.get("https://api.thecatapi.com/v1/images/search")
        
        await message.reply_photo(r.json()[0]['url'])
    except Exception as e:
        await message.reply(f"Error:\n<code>{e}</code>")