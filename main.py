import asyncio
import os
import sys
from configparser import ConfigParser
from pathlib import Path

from pyrogram import Client, enums, filters


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


@app.on_message(filters.command("restart", ["!", "/"]))
async def restart(client, message):
    if message.from_user.id == ADMIN1_ID:
        args = sys.argv[:]
        args.insert(0, sys.executable)
        os.chdir(os.getcwd())
        await message.reply("Restarting...")
        os.execv(sys.executable, args)
    else:
        await message.reply("You are not an admin!")


@app.on_message(filters.command("version", "!"))
async def version(client, message):
    await message.reply(f"TARS 3.0.1\nhttps://github.com/DDF95/TARSbot")



# HELP
@app.on_message(filters.command("help", ["!", "/", "."]))
async def help(client, message):
    await message.reply("""**OpenAI commands**
    • `!askdavinci <text>`
    • `!askcurie <text>`
    • `!askbabbage <text>`
    • `!askada <text>`
    • `!continue <engine>`: Continues the message you're replying to with the specified engine. Available engines: `davinci`, `curie`, `babbage`, `ada`.

**Chat commands**
    • `!about`: Read the chat description.
    • `!del`: Deletes the message you're replying to.
    • `!find <text>`: Searchs for text messages inside the chat and returns a random result.
    • `!id`: Returns the chat ID and the user ID. You can reply to a message to get the ID of the user who sent it.
    • `!join <invite link>`: Joins a chat. 
    • `!pin`: Pins the message you're replying to.
    • `!setabout <description>`: Set chat description.
    • `!setpicture`: Sets the photo you're replying to as the chat's picture. 
    • `!title <text>`: Changes the chat's title.

**Twitter commands**
    • `!follow <Twitter username>`: Follows the specified Twitter user.
    • `!tweet <text>`: Sends a tweet using the @rTARSbot Twitter account.
    • `!tweets <Twitter username>`: Retrieves the last 5 tweets sent by the user.
    • `!twsearch <query>`: Searches for tweets containing the specified query.
    • `!unfollow <Twitter username>`: Unfollows the specified Twitter user.

**Reactions commands**
    • `!reacts`: Shows the list of saved reactions.
    • `!setreact <trigger> <reaction emoji>`: Saves a reaction that will automatically be sent when the trigger word appears in a message.
    • `!unsetreatc <trigger>`: Deletes the reaction. 

**Set commands**
    • `!sets`: Returns the list of saved sets.
    • `!set <trigger> <reply>`: Saves a reply that will automatically be sent when the trigger word appears in a message.
    • `!unset <trigger>`: Deletes the reply associated with the trigger word.
    • `!media`: Returns the list of media saved.
    • `!setmedia <trigger>`: Reply this to a message to save a media object (photo, video, sticker, etc...) that will automatically be sent when the trigger word appears.
    • `!unsetmedia <trigger>`: Deletes the media object associated with the trigger word.

**Other commands**
    • `Alexa play <text>`: Sends the first YouTube search result.
    • `!calc <expression>`: Resolves the expression and sends the result.
    • `!cat`: Sends a random cat picture.
    • `!dog`: Sends a random dog picture.
    • `!echo <text>`: Echoes the message. 
    • `!fox`: Sends a random fox picture.
    • `!glasses <phrase1> - <phrase2>`: Creates a "deal with it" ASCII art with your two phrases.
    • `!help`: Show all commands. 
    • `!html2pdf <link>`: Sends a .pdf file of the specified web page.
    • `!img <query>`: Searches a random image on Google (max 100 requests per day).
    • `!latex <text>`: Convert LaTeX text to image.
    • `!loc <location>`: Returns a map of the specified location.
    • `!lyrics <artist> - <track>`: Returns the song's lyrics.
    • `!magic8ball <text>`: Seek advice from TARS.
    • `!paywall <link>`: Tries to bypass paywalled articles using 12ft.io
    • `!qr <text>`: Generates a QR code of your text.
    • `!quote`: Generates an inspirational quote based on the message you're replying to.
    • `!reddit <subreddit>`: Retrieves a random hot post from the subreddit.
    • `!reddit <subreddit> <1-27>`: Retrieves a specific post from the subreddit.
    • `!remind <4w5d2h3m> <text>`: Insert a time delay and set a reminder (w = weeks, d = days, h = hours, m = minutes).
    • `!google <query>`: Searches Google and sends results (max 100 requests per day).
    • `!ud <term>`: Returns the definition of the term from Urban Dictionary.
    • `!version`: Shows the current version of TARS and it's source code.
    • `!watch <query>`: Searches movies/TV shows on JustWatch and returns a list of links (credits: Trifase).""",
    parse_mode=enums.ParseMode.MARKDOWN
    )


asyncio(app.run())
