from configparser import ConfigParser

from pyrogram import Client, enums, filters


cfg = ConfigParser(interpolation=None)
cfg.read("config.ini")

OWM_APPID = cfg.get("openweathermap", "owm_appid")


@Client.on_message(filters.command("loc", "!"))
async def loc(client, message):
    if len(message.command) == 1:
        await message.reply(text="Usage: `!loc <city>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        import urllib.parse
        escaped_text = urllib.parse.quote(message.text[3+1:])
        
        try:
            import requests
            r = requests.get('http://api.openweathermap.org/geo/1.0/direct?q=' + escaped_text + '&limit=1&appid=' + OWM_APPID)

            await client.send_location(message.chat.id, r.json()[0]['lat'], r.json()[0]['lon'])
        except Exception as e:
            await message.reply(f"Error:\n<code>{e}</code>")
