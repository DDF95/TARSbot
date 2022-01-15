from pyrogram import Client, filters
import json
from youtubesearchpython import VideosSearch
import re
import requests
import urllib.parse
import random
import tweepy
import time
import datetime
from pytimeparse import parse
from googleapiclient.discovery import build
import praw
from pyrogram.types import InputMediaPhoto
import urllib.request
import ffmpy
import cv2
from configparser import ConfigParser
from pathlib import Path
from wand.image import Image
from wand.drawing import Drawing
from textwrap import wrap
from wand.font import Font
import sys
import os
from apscheduler.schedulers.background import BackgroundScheduler

app = Client("my_account")

# CONFIG
cfg = ConfigParser(interpolation=None)
config_file = Path(__file__).with_name('config.ini')
cfg.read(config_file)

admin1 = int(cfg.get("admins", "admin1"))

test_group = int(cfg.get("specialgroups", "test_group"))

old_size = int(cfg.get("autorestart", "old_size"))

google_apikey = cfg.get("google", "google_apikey")
google_cseid = cfg.get("google", "google_cseid")

tw_consumer_key = cfg.get("twitter", "tw_consumer_key")
tw_consumer_secret = cfg.get("twitter", "tw_consumer_secret")
tw_access_token = cfg.get("twitter", "tw_access_token")
tw_access_token_secret = cfg.get("twitter", "tw_access_token_secret")
tw_bearer_token = cfg.get("twitter", "tw_bearer_token")
tw_client = tweepy.Client(tw_bearer_token, tw_consumer_key, tw_consumer_secret, tw_access_token, tw_access_token_secret)

reddit_client_id = cfg.get("reddit", "reddit_client_id")
reddit_client_secret = cfg.get("reddit", "reddit_client_secret")
reddit_user_agent = cfg.get("reddit", "reddit_user_agent")
reddit_username = cfg.get("reddit", "reddit_username")
reddit_password = cfg.get("reddit", "reddit_password")

h2p_apiKey = cfg.get("html2pdf", "h2p_apiKey")

owm_appid = cfg.get("openweathermap", "owm_appid")

directory = Path(__file__).absolute().parent

# AUTO RESTART
def autorestart():
    new_size = Path(f"{directory}/pyro.py").stat().st_size
    if new_size != old_size:
        app.send_message(test_group, "Mi riavvio perché hai cambiato il codice")
        cfg.set("autorestart", "old_size", str(new_size))
        with open(config_file, 'w') as configfile:
            cfg.write(configfile)
        args = sys.argv[:]
        args.insert(0, sys.executable)
        os.chdir(os.getcwd())
        os.execv(sys.executable, args)
    else:
        pass
scheduler = BackgroundScheduler()
scheduler.add_job(autorestart, "interval", seconds=5)
scheduler.start()

# BACKUP
@app.on_message(filters.command("backup", "!"))
def backup(client, message):
    if message.from_user.id == admin1:
        sets_file = f"{directory}/sets.json"
        reaccs_file = f"{directory}/reactions.json"
        bot_file = f"{directory}/pyro.py"
        config_ini_file = f"{directory}/config.ini"
        client.send_message(test_group, datetime.datetime.utcfromtimestamp(message.date + 3600).strftime('Backup eseguito il %d-%m-%Y alle ore %H:%M:%S.'))
        client.send_document(chat_id=test_group, document=sets_file)
        client.send_document(chat_id=test_group, document=reaccs_file)
        client.send_document(chat_id=test_group, document=bot_file)
        client.send_document(chat_id=test_group, document=config_ini_file)
    else:
        message.reply_text("Scusami ma non posso farlo, non ti conosco")

# RESTART
@app.on_message(filters.command("restart", "!"))
def restart(client, message):
    if message.from_user.id == admin1:
        args = sys.argv[:]
        args.insert(0, sys.executable)
        os.chdir(os.getcwd())
        message.reply_text("Ok mi riavvio")
        os.execv(sys.executable, args)
    else:
        message.reply_text("Scusami ma non posso farlo, non ti conosco")

# QUOTE
@app.on_message(filters.command("quote", "!"))
def quote(client, message):
    random_int = random.randrange(99999)
    img_data = requests.get(f"https://picsum.photos/800/500?{str(random_int)}").content
    with open('starting_quote.jpg', 'wb') as handler:
        handler.write(img_data)
    img = Image(filename="starting_quote.jpg")
    img.brightness_contrast(brightness=-20)
    quote_font1 = Font(f"{directory}/open-sans/Vollkorn-Regular.ttf", color="black")
    quote_font2 = Font(f"{directory}/open-sans/Vollkorn-Regular.ttf", color="white")
    author_font1 = Font(f"{directory}/open-sans/Vollkorn-Italic.ttf", color="black")
    author_font2 = Font(f"{directory}/open-sans/Vollkorn-Italic.ttf", color="white")
    t_now = int(time.time())
    date = datetime.datetime.utcfromtimestamp(t_now + 3600).strftime("%d %B %Y")
    date = date.replace("January", "Gennaio")
    date = date.replace("February", "Febbraio")
    date = date.replace("March", "Marzo")
    date = date.replace("April", "Aprile")
    date = date.replace("May", "Maggio")
    date = date.replace("June", "Giugno")
    date = date.replace("July", "Luglio")
    date = date.replace("August", "Agosto")
    date = date.replace("September", "Settembre")
    date = date.replace("October", "Ottobre")
    date = date.replace("November", "Novembre")
    date = date.replace("December", "Dicembre")
    with Drawing():
        img.caption(f'{message.reply_to_message.text}', left=62, top=62, width=680, height=270, font=quote_font1, gravity='center')
        img.caption(f'- {message.reply_to_message.from_user.first_name}, {date}', left=62, top=352, width=680, height=70, font=author_font1, gravity='east')
        img.caption(f'{message.reply_to_message.text}', left=60, top=60, width=680, height=270, font=quote_font2, gravity='center')
        img.caption(f'- {message.reply_to_message.from_user.first_name}, {date}', left=60, top=350, width=680, height=70, font=author_font2, gravity='east')
    img.save(filename="result_quote.jpg")
    message.reply_photo("result_quote.jpg")

# READ DESCRIPTION
@app.on_message(filters.command("about", "!"))
def readgroupdescription(client, message):
    description = client.get_chat(message.chat.id).description
    message.reply_text(description)

# SET DESCRIPTION
@app.on_message(filters.command("setabout", "!"))
def setgroupdescription(client, message):
    new_description = message.text[9 + 1:]
    chat_info = client.get_chat(message.chat.id)
    old_description = chat_info.description
    message.reply_text("Nuova descrizione impostata, quella vecchia era:\n" + old_description)
    client.set_chat_description(message.chat.id, new_description)

# UNSET REACTION
@app.on_message(filters.command("unreacc", "!"))
def unsetreacc(client, message):
    trigger = message.command[1]
    groupid = message.chat.id
    filename = f"{directory}/reactions.json"
    with open(filename, 'r') as file:
        file_data = json.load(file)
    del file_data['{}'.format(groupid)]['{}'.format(trigger)]
    with open(filename, 'w') as file:
        message.reply_text("Cancellato amo")
        json.dump(file_data, file, indent=4)
    return True

# GET REACTION LIST
@app.on_message(filters.command("reaccs", "!"))
def getreacclist(client, message):
    groupid = message.chat.id
    filename = f"{directory}/reactions.json"
    try:
        with open(filename) as fileSets:
            dataSets = json.load(fileSets)
            messaggio = ""
            for key, value in dataSets['{}'.format(groupid)].items():
                messaggio += f"{key} → {value}\n"
            client.send_message(groupid, messaggio)
    except:
        pass

# SET REACTION
@app.on_message(filters.command("setreacc", "!"))
def setreacc(client, message):
    trigger = message.command[1]
    reaction = message.command[2]
    groupid = message.chat.id
    filename = f"{directory}/reactions.json"
    reactions = ["👍", "👎", "❤️", "🔥", "🎉", "🤩", "😱", "😁", "😢", "💩", "🤮"]  
    if any(x in reaction for x in reactions):
        with open(filename, 'r') as file:
            file_data = json.load(file)
        if not file_data.get('{}'.format(groupid)): 
            file_data['{}'.format(groupid)] = {}
        file_data['{}'.format(groupid)]['{}'.format(trigger)] = '{}'.format(reaction)
        with open(filename, 'w') as file:
            message.reply_text("Fatto amo")
            json.dump(file_data, file, indent=4)
        return True
    else:
        message.reply_text("Lol questa non è una reaction valida cretinə, usa queste:\n👍👎❤️🔥🎉🤩😱😁😢💩🤮")

# VOMIT REACT
@app.on_message(filters.command("vomita", list("!/")))
def vomita(client, message):
    message_id = message.reply_to_message.message_id
    client.send_reaction(message.chat.id, message_id, "🤮")

# VERSION
@app.on_message(filters.command("version", "!"))
def version(client, message):
    message.reply_text("Version 0.69\nhttps://github.com/DDF95/TARSbot")

# SET CHAT PICTURE
@app.on_message(filters.command("setpicture", "!"))
def grouppropic(client, message):
    image = message.reply_to_message.photo.file_id
    client.set_chat_photo(chat_id=message.chat.id, photo=image)

# TWITTER TIMELINE
@app.on_message(filters.command("tweets", "!"))
def timelineTW(client, message):
    userStr = ' '.join(message.command[1:])
    userStrFixed = userStr.replace("@", "")
    userResponse = tw_client.get_user(username=userStrFixed)
    twUserID = userResponse.data['id']
    tweets = tw_client.get_users_tweets(id=twUserID, tweet_fields=['context_annotations','created_at','geo'], max_results=5, exclude="replies,retweets")
    for tweet in tweets.data:
        client.send_message(message.chat.id, tweet)

# REDDIT API
@app.on_message(filters.command("reddit", "!"))
def reddit(client, message):
    reddit = praw.Reddit(
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        user_agent=reddit_user_agent
        #username=reddit_username,
        #password=reddit_password,
    )
    redditStr = message.command[1]
    submissions = list(reddit.subreddit(redditStr).hot(limit=27))
    try:
        postNumber = int(message.command[2])
    except:
        postNumber = None
    if postNumber is None:
        submission = random.choice(submissions)
    else:
        submission = submissions[postNumber]
    title = submission.title
    upvotes = submission.score
    url = submission.url
    permalink = f"https://reddit.com{submission.permalink}"
    sub = f"r/{submission.subreddit}"
    gallery = []
    images = []
    media_caption = f"<b>{title}</b>\n{upvotes} upvotes | <a href='{permalink}'>{sub}</a>"
    if submission.is_self == True:
        selftext = submission.selftext
        textSelf = f"<b>{title}</b>\n{upvotes} upvotes | <a href='{permalink}'>{sub}</a>\n\n{selftext}"
        if len(textSelf) > 4096:
            for x in range(0, len(textSelf), 4096):
                message.reply_text(textSelf[x:x + 4096], disable_web_page_preview=True)
        else:
            message.reply_text(textSelf, disable_web_page_preview=True)
    else:
        if "redd" in url:
            if "gallery" in url:
                ids = [i['media_id'] for i in submission.gallery_data['items']]
                for id in ids:
                    url = submission.media_metadata[id]['p'][0]['u']
                    url = url.split("?")[0].replace("preview", "i")
                    gallery.append(url)
                for index, url in enumerate(gallery):
                    link = urllib.request.urlopen(url)
                    try:
                        name = f"{directory}/albumcache/image{index+1}.jpg"
                        images.append(name)
                        with open(name, "wb") as output:
                            output.write(link.read())
                    except IOError:
                        print("Unable to create file")
                client.send_media_group(reply_to_message_id=message.message_id, chat_id=message.chat.id, media=[InputMediaPhoto(name) for name in images[:10]])
                client.send_message(message.chat.id, media_caption, disable_web_page_preview=True)
            elif submission.url.endswith(".gif"):
                videourl = submission.preview['images'][0]['variants']['mp4']['source']['url']
                message.reply_video(video=videourl, caption=media_caption)
            elif "v.redd.it" in url:
                message.reply_text("Scarico il video, potrebbe volerci qualche secondo...")
                url = submission.media['reddit_video']['fallback_url']
                url = url.replace("?source=fallback", "")
                url_audio = url.replace("1080", "audio")
                url_audio = url_audio.replace("720", "audio")
                url_audio = url_audio.replace("360", "audio")
                video_file = f"{directory}/videocache/video.mp4"
                audio_file = f"{directory}/videocache/audio.mp4"
                link_video = urllib.request.urlopen(url)
                link_audio = urllib.request.urlopen(url_audio)
                with open(video_file, "wb") as output:
                    output.write(link_video.read())
                with open(audio_file, "wb") as output:
                    output.write(link_audio.read())
                video_file_finale = f"{directory}/videocache/video_con_audio.mp4"
                ff = ffmpy.FFmpeg(
                    inputs={url: None, url_audio: None},
                    outputs={video_file_finale: '-y -c:v copy -c:a aac -loglevel quiet'})
                ff.run()
                cv2video = cv2.VideoCapture(video_file_finale)
                height = cv2video.get(cv2.CAP_PROP_FRAME_HEIGHT)
                width  = cv2video.get(cv2.CAP_PROP_FRAME_WIDTH) 
                message.reply_video(video=video_file_finale, caption=media_caption, height=int(height), width=int(width))
            else:
                message.reply_photo(photo=url, caption=media_caption)
        elif "imgur" in url:
            if submission.url.endswith(".gif") or submission.url.endswith(".gifv"):
                videourl = url.replace("gifv", "mp4")
                videourl = url.replace("gif", "mp4")
                message.reply_video(video=videourl, caption=media_caption)
            else:
                url += ".jpeg"
                message.reply_photo(photo=url, caption=media_caption)
        elif "gfycat" in url:
            url = submission.media['oembed']['thumbnail_url'][:-20]
            videourl = f"{url}-mobile.mp4"
            message.reply_video(video=videourl, caption=media_caption)
        elif "redgifs.com" in url:
            videourl = submission.preview['reddit_video_preview']['fallback_url']
            message.reply_video(video=videourl, caption=media_caption)
        else:
            message.reply_text(f"<b>{title}</b>\n{url}\n\n{upvotes} upvotes | <a href='{permalink}'>{sub}</a>")

# DELETE MESSAGE
@app.on_message(filters.command("del", "!"))
def delmsg(client, message):
    message.reply_to_message.delete()

# GOOGLE SEARCH
@app.on_message(filters.command("search", "!"))
def gsearch(client, message):
    searchStr = message.command[1:]
    page = 1
    start = (page - 1) * 10 + 1
    url = f"https://www.googleapis.com/customsearch/v1?key={google_apikey}&cx={google_cseid}&q={searchStr}&start={start}"
    data = requests.get(url).json()
    search_items = data.get("items")
    resultsStr = ""
    for i, search_item in enumerate(search_items, start=1):
        title = search_item.get("title")
        html_snippet = search_item.get("htmlSnippet")
        link = search_item.get("link")
        resultsStr += f"<b>{title}</b>\n<i>{html_snippet}</i>\n{link}\n\n"
    message.reply_text(resultsStr, disable_web_page_preview=True)

# GOOGLE IMAGE SEARCH
@app.on_message(filters.command("img", "!"))
def gimgsearch(client, message):
    searchStr = ' '.join(message.command[1:])
    resource = build("customsearch", 'v1', developerKey=google_apikey).cse()
    result = resource.list(q=searchStr, cx=google_cseid, searchType='image').execute()
    randomInt = random.randrange(10)
    message.reply_photo(result['items'][randomInt]['link'])

# LATEX
@app.on_message(filters.command("latex", "!"))
def latex(client, message):
    latexStr = ' '.join(message.command[1:])
    latexEscaped = urllib.parse.quote("\dpi{200}" + latexStr)
    latexRequest = "https://latex.codecogs.com/png.image?" + latexEscaped
    message.reply_photo(latexRequest)

# FOX
@app.on_message(filters.command("fox", "!"))
def fox(client, message):
    foxRequest = requests.get("https://randomfox.ca/floof/")
    message.reply_photo(foxRequest.json()['image'])

# UNFOLLOW
@app.on_message(filters.command("unfollow", "!"))
def unfollowTW(client, message):
    userStr = ' '.join(message.command[1:])
    userStrFixed = userStr.replace("@", "")
    userResponse = tw_client.get_user(username=userStrFixed)
    twUserID = userResponse.data['id']
    tw_client.unfollow_user(twUserID)
    message.reply_text("Ho unfollowato @" + userStrFixed + " su Twitter")

# FOLLOW
@app.on_message(filters.command("follow", "!"))
def followTW(client, message):
    userStr = ' '.join(message.command[1:])
    userStrFixed = userStr.replace("@", "")
    userResponse = tw_client.get_user(username=userStrFixed)
    twUserID = userResponse.data['id']
    tw_client.follow_user(twUserID)
    message.reply_text("Ho followato @" + userStrFixed + " su Twitter")

# REMIND
@app.on_message(filters.command("remind", "!"))
def remind(client, message):
    timeToMessageStr = message.command[1]
    reminderText = message.text[7 + 1 + len(timeToMessageStr) + 1:]
    t_now = int(time.time())
    secondsToMessage = parse(timeToMessageStr)
    t = t_now + secondsToMessage
    client.send_message(message.chat.id, reminderText, schedule_date=t)
    message.reply_text(datetime.datetime.utcfromtimestamp(t + 3600).strftime('Te lo ricorderò il %d-%m-%Y alle %H:%M giuro'))

# NO PAYWALL
@app.on_message(filters.command("paywall", "!"))
def nopaywall(client, message):
    linkStr = ' '.join(message.command[1:])
    linkEscaped = urllib.parse.quote(linkStr)
    message.reply_text("https://12ft.io/proxy?q=" + linkEscaped)

# TWEET
@app.on_message(filters.command("tw", "!"))
def tweet(client, message):
    tweetStr = ' '.join(message.command[1:])
    response = tw_client.create_tweet(text=tweetStr)
    message.reply_text("Ho inviato il tweet amo: https://twitter.com/rTARSbot/status/" + response.data['id'])

# HTML2PDF
@app.on_message(filters.command("html2pdf", "!"))
def html2pdf(client, message):
    html2pdfStr = ' '.join(message.command[1:])
    linkRequests = "https://api.html2pdf.app/v1/generate?url={0}&apiKey={1}".format(html2pdfStr, h2p_apiKey)
    result = requests.get(linkRequests).content
    document = f"{directory}/othercache/document.pdf"
    with open(document, "wb") as handler:
        handler.write(result)
        app.send_document(message.chat.id, document)

# QR CODE 
@app.on_message(filters.command("qr", "!"))
def qrcode(client, message):
    qrStr = ' '.join(message.command[1:])
    qrStrEsc = urllib.parse.quote(qrStr)
    message.reply_photo("https://api.qrserver.com/v1/create-qr-code/?size=500x500&data=" + qrStrEsc)

# CAT
@app.on_message(filters.command("cat", "!"))
def cat(client, message):
    catRequest = requests.get("https://api.thecatapi.com/v1/images/search")
    message.reply_photo(catRequest.json()[0]['url'])

# DOG
@app.on_message(filters.command("dog", "!"))
def dog(client, message):
    dogRequest = requests.get("https://dog.ceo/api/breeds/image/random")
    message.reply_photo(dogRequest.json()['message'])

# GLASSES 
@app.on_message(filters.command("glasses", "!"))
def glasses(client, message):
    glassesStr = ' '.join(message.command[1:])
    phrase1and2 = glassesStr.split(" - ")
    phrase1 = phrase1and2[0]
    phrase2 = phrase1and2[1]
    message.reply_text(phrase1 + "\n\n<code>(•_•)\n( •_•)>⌐■-■\n(⌐■_■)</code> " + phrase2)

# HELP
@app.on_message(filters.command("help", list("/.!")))
def help(client, message):
    message.reply_text("""<b>Chat commands</b>
• <code>!about</code>: Read group description.
• <code>!del</code>: Deletes the message you're replying to.
• <code>!id</code>: Returns the chat id.
• <code>!join [invite link]</code>: Joins a group. 
• <code>!pin</code>: Pins the message you're replying to.
• <code!setabout [description]</code>: Set group description.
• <code>!setpicture</code>: Sets the photo you're replying to as the chat's picture. 
• <code>!settitle [text]</code>: Changes the group's title.

<b>Twitter commands</b>
• <code>!follow [Twitter username]</code>: Follows the specified Twitter user.
• <code>!tw [text]</code>: Sends a tweet using the @rTARSbot Twitter account.
• <code>!tweets [Twitter username]</code>: Retrieves the last 5 tweets sent by the user.
• <code>!unfollow [Twitter username]</code>: Unfollows the specified Twitter user.

<b>Reactions commands</b>
• <code>!reaccs</code>: Shows the list of set reactions.
• <code>!setreacc [word] [reaction emoji]</code>: Saves a reaction.
• <code>!unreacc [word]</code>: Deletes the reaction. 
• <code>!vomita</code>: Reply this to vomit on a message.

<b>Set commands</b>
• <code>!get</code>: Returns the list of sets.
• <code>!set [value_name] [data]</code>: Saves the data with the value_name name.
• <code>!unset [value_name]</code>: Deletes the data with the value_name name.

<b>Other commands</b>
• <code>Alexa play [song title]</code>: Sends the first YouTube search result.
• <code>!calc [expression]</code>: Evaluates the expression and sends the result.
• <code>!cat</code>: Sends a random cat picture.
• <code>!dog</code>: Sends a random dog picture.
• <code>!echo [whatever]</code>: Echoes the message. 
• <code>!fox</code>: Sends a random fox picture.
• <code>!glasses [input1 - input2]</code>: Creates a "deal with it" ASCII art with your two inputs.
• <code>!help</code>: Show all commands. 
• <code>!html2pdf [link]</code>: Sends a .pdf file of the specified web page.
• <code>!img [query]</code>: Random searches an image with Google API (max 100 requests per day).
• <code>!latex [equation]</code>: Convert LaTeX equation to image.
• <code>!loc [location]</code>: Returns a map of the specified location.
• <code>!lyrics [artist - track]</code>: Search and get lyrics of the song (the order and the dash are important).
• <code>!magic8ball [text]</code>: Seek advice from TARS.
• <code>!paywall [link]</code>: Tries to bypass paywalled articles using 12ft.io
• <code>!qr [text]</code>: Generates a QR code.
• <code>!quote</code>: Generates an inspirational quote based on the message you're replying to.
• <code>!reddit [subreddit]</code>: Retrieves a random hot post from the subreddit.
• <code>!reddit [subreddit] [1-27]</code>: Retrieves a specific post from the subreddit.
• <code>!remind [2h] [text]</code>
• <code>!remind [4w5d2h3m] [text]</code>: Insert a time delay and set a reminder (w = weeks, d = days, h = hours, m = minutes).
• <code>!search [query]</code>: Searches Google and sends results (max 100 requests per day).
• <code>!ud [term]</code>: Returns the definition of term from Urban Dictionary.""")

# ECHO
@app.on_message(filters.command("echo", "!"))
def echo(client, message):
    echoStr = ' '.join(message.command[1:])
    client.send_message(message.chat.id, echoStr)
    
# URBAN DICTIONARY
@app.on_message(filters.command("ud", "!"))
def ud(client, message):
    searchStr = ' '.join(message.command[1:])
    searchEscaped = urllib.parse.quote(searchStr)
    wordRequest = requests.get('http://api.urbandictionary.com/v0/define?term=' + searchEscaped)
    message.reply_text(
        '**' + wordRequest.json()['list'][0]['word'] + '**' + '\n' +
        wordRequest.json()['list'][0]['definition'] + '\n\nExamples: \n' +
        '__' + wordRequest.json()['list'][0]['example'] + '__', parse_mode = 'markdown'
        )

# LYRICS 
@app.on_message(filters.command("lyrics", "!"))
def lyrics(client, message):
    searchStr = ' '.join(message.command[1:])
    authorandsong = searchStr.split(" - ")
    author = authorandsong[0]
    song = authorandsong[1]
    authorEsc = urllib.parse.quote(author)
    songEsc = urllib.parse.quote(song)
    lyricsRequest = requests.get("https://api.lyrics.ovh/v1/" + authorEsc + "/" + songEsc)
    message.reply_text(lyricsRequest.json()['lyrics'])

# MAGIC8BALL
@app.on_message(filters.command("magic8ball", "!"))
def magic8ball(client, message):
    responses = ['It is certain','It is decidedly so','Without a doubt','Yes definitely','You may rely on it','As I see it, yes','Most likely','Outlook good','Yes','Signs point to yes','Reply hazy try again','Ask again later','Better not tell you now','Cannot predict now','Concentrate and ask again','Don\'t count on it','My reply is no','My sources say no','Outlook not so good','Very doubtful']
    message.reply_text(random.choice(responses))

# LOC
@app.on_message(filters.command("loc", "!"))
def loc(client, message):
    locStr = ' '.join(message.command[1:])
    locEscaped = urllib.parse.quote(locStr)
    locRequest = requests.get('http://api.openweathermap.org/geo/1.0/direct?q=' + locEscaped + '&limit=1&appid=' + owm_appid)
    client.send_location(message.chat.id, locRequest.json()[0]['lat'], locRequest.json()[0]['lon'])

# JOIN CHAT
@app.on_message(filters.command("join", "!"))
def join(client, message):
    linkStr = ' '.join(message.command[1:])
    linkFixed = linkStr.replace("+", "joinchat/")
    client.join_chat(linkFixed)
    message.reply_text("Forse ho joinato amo")

# PIN
@app.on_message(filters.command("pin", "!"))
def pin(client, message):
    message.reply_to_message.pin()

# SET CHAT TITLE
@app.on_message(filters.command("settitle", "!"))
def title(client, message):
    titolo = ' '.join(message.command[1:])
    client.set_chat_title(chat_id=message.chat.id, title=titolo)

# GROUP ID
@app.on_message(filters.command("id", "!"))
def groupid(client, message):
    message.reply_text("ID del gruppo: " + str(message.chat.id) + "\n\nIl tuo ID: " + str(message.from_user.id))

# SET
@app.on_message(filters.command("set", "!"))
def set(client, message):
    trigger = message.command[1]
    risposta = message.text[4 + 1 + len(trigger) + 1:]
    groupid = message.chat.id
    filename = f"{directory}/sets.json"
    with open(filename, 'r') as file:
        file_data = json.load(file)
    if not file_data.get('{}'.format(groupid)): 
        file_data['{}'.format(groupid)] = {}
    file_data['{}'.format(groupid)]['{}'.format(trigger)] = '{}'.format(risposta)
    with open(filename, 'w') as file:
        message.reply_text("Fatto amo")
        json.dump(file_data, file, indent=4)
    return True

# UNSET
@app.on_message(filters.command("unset", "!"))
def unset(client, message):
    trigger = message.command[1]
    groupid = message.chat.id
    filename = f"{directory}/sets.json"
    with open(filename, 'r') as file:
        file_data = json.load(file)
    del file_data['{}'.format(groupid)]['{}'.format(trigger)]
    with open(filename, 'w') as file:
        message.reply_text("Cancellato amo")
        json.dump(file_data, file, indent=4)
    return True

# ALEXA
@app.on_message(filters.regex("[Aa]lexa [Pp]lay (.+)"))
def alexa(client, message):
    searchTerm = re.search(r'[Aa]lexa [Pp]lay (.+)', message.text).group(1)
    videosSearch = VideosSearch(searchTerm, limit = 1)
    message.reply_text(
        videosSearch.result()['result'][0]['title'] + 
        "\n\n" + 
        videosSearch.result()['result'][0]['duration'] +
        " | " +
        videosSearch.result()['result'][0]['viewCount']['text'] +
        "\n\n" +
        videosSearch.result()['result'][0]['link']
        )

# CALC
@app.on_message(filters.command("calc", "!"))
def calc(client, message):
    mathExpr = re.search(r'!calc (.+)', message.text).group(1)
    mathExprEscaped = urllib.parse.quote(mathExpr)
    mathjsRequest = requests.get('https://api.mathjs.org/v4/?expr=' + mathExprEscaped)
    risultato = mathjsRequest.text
    message.reply_text(risultato)

# GET LIST
@app.on_message(filters.command("get", "!"))
def getlist(client, message):
    groupid = message.chat.id
    filename = f"{directory}/sets.json"
    try:
        with open(filename) as fileSets:
            dataSets = json.load(fileSets)
            messaggio = ""
            for key in dataSets['{}'.format(groupid)].keys():
                messaggio += "{}\n".format(key)
            client.send_message(groupid, messaggio)
    except:
        pass

# GET
@app.on_message(filters.text)
def get(client, message):
    groupid = message.chat.id
    wordList = message.text.split() 
    getFirstWord = wordList[0]
    setsfilename = f"{directory}/sets.json"
    try:
        with open(setsfilename) as fileSets:
            dataSets = json.load(fileSets)
        client.send_message(groupid, dataSets['{}'.format(groupid)]['{}'.format(getFirstWord)])
    except:
        pass

    # REACTIONS
    message_id = message.message_id
    reaccsfilename = f"{directory}/reactions.json"
    try:
        with open(reaccsfilename) as fileReaccs:
            dataReaccs = json.load(fileReaccs)
        keys = dataReaccs[str(groupid)].keys()
        triggerWords = list(filter(lambda x:x in keys, wordList))
        if any(x in keys for x in wordList):
            try: 
                client.send_reaction(groupid, message_id, dataReaccs[str(groupid)][triggerWords[0]])
            except:
                pass
    except:
        pass

app.run()
