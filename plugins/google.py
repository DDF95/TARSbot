from configparser import ConfigParser

from pyrogram import Client, enums, filters


cfg = ConfigParser(interpolation=None)
cfg.read("config.ini")

G_APIKEY = cfg.get("google", "google_apikey")
G_CSEID = cfg.get("google", "google_cseid")


@Client.on_message(filters.command(["search", "google"], "!"))
async def g_search(client, message):
    if len(message.command) == 1:
        await message.reply(text="Usage: `!google <text>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        import urllib.parse
        query = urllib.parse.quote(message.text[1+6+1:])

        try:
            import requests
            r = requests.get('https://www.googleapis.com/customsearch/v1?key=' + G_APIKEY + '&cx=' + G_CSEID + '&q=' + query)

            results = ""
            for i in range(5):
                results += f"{str(i+1)}. <b>{r.json()['items'][i]['title']}</b>\n{r.json()['items'][i]['link']}\n{r.json()['items'][i]['htmlSnippet']}\n\n"
            
            await message.reply(text=results, disable_web_page_preview=True)
        except Exception as e:
            await message.reply(f"Error:\nProbably the limit of 100 requests per day has been reached.\n<code>{e}</code>")


@Client.on_message(filters.command(["img", "pic"], "!"))
async def g_images(client, message):
    if len(message.command) == 1:
        await message.reply(text="Usage: `!pic <text>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        import urllib.parse
        query = urllib.parse.quote(message.text[1+3+1:])

        try:
            import requests
            r = requests.get('https://www.googleapis.com/customsearch/v1?key=' + G_APIKEY + '&cx=' + G_CSEID + '&q=' + query + '&searchType=image')

            import random
            await message.reply_photo(photo=r.json()['items'][random.randint(0, len(r.json()['items'])-1)]['link'])
        except Exception as e:
            await message.reply(f"Error:\nProbably the limit of 100 requests per day has been reached.\n<code>{e}</code>")
# TODO: instead of sending a single image, send an album of 10 images