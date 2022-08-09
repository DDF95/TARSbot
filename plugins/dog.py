from pyrogram import Client, filters

@Client.on_message(filters.command("dog", "!"))
async def dog(client, message):
    import requests
    
    try:
        r = requests.get("https://dog.ceo/api/breeds/image/random")

        await message.reply_photo(r.json()['message'])
    except Exception as e:
        await message.reply(f"Errore:\n<code>{e}</code>")