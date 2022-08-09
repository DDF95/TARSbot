from pyrogram import Client, filters


@Client.on_message(filters.command("fox", "!"))
async def fox(client, message):
    try:
        import requests
        r = requests.get("https://randomfox.ca/floof/")
        await message.reply_photo(r.json()['image'])
    except Exception as e:
        await message.reply(f"Error:\n<code>{e}</code>")