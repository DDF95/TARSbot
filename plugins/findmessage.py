from configparser import ConfigParser
from pickle import BINPUT

from pyrogram import Client, enums, filters


cfg = ConfigParser(interpolation=None)
cfg.read("config.ini")

BOT_ID = int(cfg.get("admins", "bot_id"))


@Client.on_message(filters.command("find", "!"))
async def find_message(client, message):
        if len(message.command) == 1:
            await message.reply("Usage:\n`!find <text>`\n`!find @<username> <text>`", parse_mode=enums.ParseMode.MARKDOWN)
        else:
            try:
                results = ""
                n = 0

                if "@" in message.command[1]:
                    async for result in client.search_messages(chat_id=message.chat.id, query=message.text[1+4+1 + len(message.command[1]):], from_user=message.command[1], offset=1):
                        if not result.text.startswith(("!", "/")) and result.from_user.id != BOT_ID:
                            if result.caption:
                                n += 1
                                results += f"{n}. <a href=\"{result.link}\">link to message</a>\n{result.caption}\n\n"
                            elif result.text:
                                n += 1
                                results += f"{n}. <a href=\"{result.link}\">link to message</a>\n{result.text}\n\n"
                            else:
                                n += 1
                                results += f"{n}. <a href=\"{result.link}\">link to message</a>\n\n"
                else:
                    async for result in client.search_messages(chat_id=message.chat.id, query=message.text[1+4+1:], offset=1):
                        if not result.text.startswith(("!", "/")) and result.from_user.id != BOT_ID:
                            if result.caption:
                                n += 1
                                results += f"{n}. <a href=\"{result.link}\">link to message</a>\n{result.caption}\n\n"
                            elif result.text:
                                n += 1
                                results += f"{n}. <a href=\"{result.link}\">link to message</a>\n{result.text}\n\n"
                            else:
                                n += 1
                                results += f"{n}. <a href=\"{result.link}\">link to message</a>\n\n"
                    
                if results:
                    await message.reply(text=results)
                else:
                    await message.reply(text="No results found.")
            except Exception as e:
                await message.reply(text=f"Error:\n<code>{e}</code>")
