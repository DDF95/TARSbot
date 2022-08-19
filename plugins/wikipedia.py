import wikipedia
from pyrogram import Client, enums, filters


@Client.on_message(filters.command("wiki", "!"))
async def search_wikipedia(client, message):
    if len(message.command) == 1:
        await message.reply(text="Usage: `!wiki <query>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        wikipedia.set_lang("it")

        page = wikipedia.search(message.text[1+4+1:])[0]
        summary = f"<a href='http://it.wikipedia.org/wiki/{page}'><b>{page}</b></a>\n"
        summary += f"{wikipedia.summary(page, sentences=1)}"

        await message.reply(summary, disable_web_page_preview=True)
    
