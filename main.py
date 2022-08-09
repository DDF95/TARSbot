import asyncio
import os
import sys
from configparser import ConfigParser
from pathlib import Path

from pyrogram import Client, filters


os.chdir(os.path.dirname(os.path.realpath(__file__)))  

cfg = ConfigParser(interpolation=None)
cfg.read("config.ini")

API_ID = cfg.get("pyrogram", "api_id")
API_HASH = cfg.get("pyrogram", "api_hash")

ADMIN1_ID = int(cfg.get("admins", "admin1"))

plugins = dict(root="plugins")
app = Client(name="TARSbot", api_id=API_ID, api_hash=API_HASH, plugins=plugins)


@app.on_message(filters.command("plugins", "!"))
async def show_plugins(client, message):
    plugins_list = [plugin.stem for plugin in Path("plugins").glob("*.py")]
    all_plugins = ""
    for i in plugins_list:
        all_plugins += f"- {i}\n"
    await message.reply(f"**Plugins:**\n{all_plugins}")


@app.on_message(filters.command("restart", "!"))
async def restart(client, message):
    if message.from_user.id == ADMIN1_ID:
        args = sys.argv[:]
        args.insert(0, sys.executable)
        os.chdir(os.getcwd())
        await message.reply("Restarting...")
        os.execv(sys.executable, args)
    else:
        await message.reply("You are not an admin!")


asyncio(app.run())
