from configparser import ConfigParser, NoSectionError, NoOptionError, ParsingError
from pyrogram import Client, enums, filters
import requests
import urllib.parse

cfg = ConfigParser(interpolation=None)
try:
    cfg.read("config.ini")
    OWM_APPID = cfg.get("openweathermap", "owm_appid")
except (FileNotFoundError, ParsingError) as e:
    raise SystemExit(f"Failed to read configuration file: {e}")
except (NoSectionError, NoOptionError) as e:
    raise SystemExit(f"Configuration error: {e}")

@Client.on_message(filters.command("loc", "!"))
async def loc(client, message):
    if len(message.command) == 1:
        await message.reply(text="Usage: `!loc <city>`", parse_mode=enums.ParseMode.MARKDOWN)
        return
    
    escaped_text = urllib.parse.quote(message.text[5:].strip())
    
    try:
        response = requests.get(
            'http://api.openweathermap.org/geo/1.0/direct',
            params={'q': escaped_text, 'limit': 1, 'appid': OWM_APPID}
        )
        response.raise_for_status()
        data = response.json()
        
        if not data:
            await message.reply(text="No location found for the specified city.")
            return
        
        latitude = data[0]['lat']
        longitude = data[0]['lon']
        await client.send_location(message.chat.id, latitude, longitude)
    except requests.exceptions.RequestException as req_err:
        await message.reply(f"Request error:\n<code>{req_err}</code>")
    except (KeyError, IndexError) as parse_err:
        await message.reply(f"Error parsing response:\n<code>{parse_err}</code>")
    except Exception as e:
        await message.reply(f"An unexpected error occurred:\n<code>{e}</code>")
