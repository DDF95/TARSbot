from configparser import ConfigParser

from pyrogram import Client, enums, filters


cfg = ConfigParser(interpolation=None)
cfg.read("config.ini")

H2P_API_KEY = cfg.get("html2pdf", "h2p_apikey")


@Client.on_message(filters.command("html2pdf", "!"))
async def html2pdf(client, message):
    if len(message.command) == 1:
        await message.reply(text="Usage: `!html2pdf <url>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        try:
            import requests
            r = requests.get(f"https://api.html2pdf.app/v1/generate?url={message.command[1]}&apiKey={H2P_API_KEY}")

            from io import BytesIO
            with BytesIO(r.content) as pdf:
                pdf.name = "document.pdf"
                await message.reply_document(document=pdf)

        except Exception as e:
            await message.reply(f"Error:\n<code>{e}</code>")
