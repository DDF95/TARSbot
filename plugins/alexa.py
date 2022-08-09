from pyrogram import Client, filters
from youtubesearchpython import VideosSearch

@Client.on_message(filters.regex("(?i)alexa play (.+)"))
async def alexa(client, message):
    try:
        vs = VideosSearch(message.matches[0].group(1))
        
        await message.reply(
            vs.result()['result'][0]['title'] + 
            "\n\n" + 
            vs.result()['result'][0]['duration'] +
            " | " +
            vs.result()['result'][0]['viewCount']['text'] +
            "\n\n" +
            vs.result()['result'][0]['link']
        )
    except Exception as e:
        print(e)