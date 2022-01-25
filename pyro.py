import datetime
import glob
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from configparser import ConfigParser
from pathlib import Path
from textwrap import wrap

import cv2
import ffmpy
import openai
import praw
import requests
import tweepy
from apscheduler.schedulers.background import BackgroundScheduler
from googleapiclient.discovery import build
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto
from pytimeparse import parse
from wand.drawing import Drawing
from wand.font import Font
from wand.image import Image
from youtubesearchpython import VideosSearch

app = Client("my_account")

# CONFIG
cfg = ConfigParser(interpolation=None)
config_file = Path(__file__).with_name('config.ini')
cfg.read(config_file)

bot_id = int(cfg.get("admins", "bot_id"))
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
tw_client = tweepy.Client(
    tw_bearer_token,
    tw_consumer_key,
    tw_consumer_secret,
    tw_access_token,
    tw_access_token_secret
    )

reddit_client_id = cfg.get("reddit", "reddit_client_id")
reddit_client_secret = cfg.get("reddit", "reddit_client_secret")
reddit_user_agent = cfg.get("reddit", "reddit_user_agent")
reddit_username = cfg.get("reddit", "reddit_username")
reddit_password = cfg.get("reddit", "reddit_password")

h2p_apiKey = cfg.get("html2pdf", "h2p_apiKey")

owm_appid = cfg.get("openweathermap", "owm_appid")

openai_apikey = cfg.get("openai", "openai_apikey")

directory = Path(__file__).absolute().parent
cache = Path(f"{directory}/cache")
cache.mkdir(parents=True, exist_ok=True)

# GENERATE TEXT
@app.on_message(filters.command("textgen", "!"))
def textgen(client, message):
    if message.from_user.id == admin1:
        try:
            prompt = message.text[8 + 1:]

            openai.api_key = openai_apikey
            response = openai.Completion.create(
                engine="text-babbage-001",
                prompt=f"{prompt}",
                temperature=0.7,
                max_tokens=100,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            message.reply_text(f"{response['choices'][0]['text']}")

        except Exception as e:
            message.reply_text(f"{e}")
    else:
        message.reply_text("Scusami ma non posso farlo, non ti conosco")

# FACES
@app.on_message(filters.command("face", "!"))
def face(client, message):
    try:
        img_data = requests.get("https://thispersondoesnotexist.com/image").content
        with open(f"{cache}/face.jpg", 'wb') as file:
            file.write(img_data)
        
        identity_data = requests.get("https://api.namefake.com/")
        name = identity_data.json()['name']
        age = str(random.randrange(100))

        message.reply_photo(photo=f"{cache}/face.jpg", caption=f"Nome: {name}\nEtà: {age}")

    except Exception as e:
        message.reply_text(f"{e}")

# FACES OPENAI
@app.on_message(filters.command("faceai", "!"))
def faceai(client, message):
    if message.from_user.id == admin1:
        try:
            img_data = requests.get("https://thispersondoesnotexist.com/image").content
            with open(f"{cache}/face.jpg", 'wb') as file:
                file.write(img_data)
            
            identity_data = requests.get("https://api.namefake.com/")
            name = identity_data.json()['name']
            age = str(random.randrange(100))

            openai.api_key = openai_apikey
            response = openai.Completion.create(
                engine="text-babbage-001",
                prompt=f"Name: {name}\nAge: {age}\nBiography:",
                temperature=0.7,
                max_tokens=64,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            message.reply_photo(photo=f"{cache}/face.jpg", caption=f"Nome: {name}\nEtà: {age}\nBiografia: {response['choices'][0]['text']}")
        
        except Exception as e:
            message.reply_text(f"{e}")
    else:
        message.reply_text("Scusami ma non posso farlo, non ti conosco")

# EXECUTE CODE **DANGEROUS**
@app.on_message(filters.command("exec", "!"))
def executecode(client, message):
    if message.from_user.id == admin1:
        try:
            exec_str = message.text[6:]
            exec(exec_str)
            app.send_message(text=f"Eseguito", chat_id=message.chat.id)
        except Exception as e:
            message.reply_text(f"{e}")
    else:
        message.reply_text("Ti piacerebbe")
    
    
# PRINT MESSAGE
@app.on_message(filters.command("print", "!"))
def printmessage(client, message):
    client.send_message(message.chat.id, f"<code>{message.reply_to_message}</code>")

# FIND MESSAGE
@app.on_message(filters.command("find", "!"))
def findmessage(client, message):
    group_id = message.chat.id
    if "@" in message.command[1]:
        search_str = ' '.join(message.command[2:])
        messages = []
        for message in app.search_messages(
            message.chat.id,
            query=search_str,
            limit=1000,
            offset=1,
            from_user=message.command[1]
            ):
            if message.text:
                if not message.text.startswith(("!", "/")):
                    messages.append(message)
        try:
            for message in random.sample(messages, 1):
                client.send_message(
                    text=f"Da: {message.from_user.first_name} ([link]({message.link}))\n\n{message.text}",
                    chat_id=group_id,
                    disable_web_page_preview=True
                    )
        except:
            client.send_message(text="Non trovo nulla", chat_id=group_id)
    else:
        search_str = ' '.join(message.command[1:])
        messages = []
        for message in app.search_messages(
            message.chat.id,
            query=search_str,
            limit=1000,
            offset=1
            ):
            if message.from_user.id != bot_id:
                if message.text:
                    if not message.text.startswith(("!", "/")):
                        messages.append(message)
        try:
            for message in random.sample(messages, 1):
                client.send_message(
                    text=f"Da: {message.from_user.first_name} ([link]({message.link}))\n\n{message.text}",
                    chat_id=group_id,
                    disable_web_page_preview=True
                    )
        except:
            client.send_message(text="Non trovo nulla", chat_id=group_id)

# DELETE GROUP
@app.on_message(filters.command("deletegroup", "!"))
def deletegroup(client, message):
    if message.from_user.id == admin1:
        try:
            app.delete_supergroup(message.chat.id)
        except Exception as e:
            message.reply_text(f"Eh scusa ma non posso cancellare questo gruppo\n\n{e}")
    else:
        message.reply_text("Scusami ma non posso farlo, non ti conosco")

# CREATE GROUP
@app.on_message(filters.command("creategroup", "!"))
def creategroup(client, message):
    if message.from_user.id == admin1:
        group_title = ' '.join(message.command[1:])
        try:
            group = app.create_supergroup(group_title)
            app.add_chat_members(group.id, message.from_user.id)
            group_link = app.create_chat_invite_link(group.id)
            message.reply_text(f'Ho creato il gruppo "[{group_title}]({group_link.invite_link})"')
        except Exception as e:
            message.reply_text(f"Errore:\n<code>{e}</code>")
    else:
        message.reply_text("Scusami ma non posso farlo, non ti conosco")

# GET MEDIA LIST
@app.on_message(filters.command("media", "!"))
def getmedialist(client, message):
    group_id = message.chat.id
    filename = f"{directory}/media.json"
    try:
        with open(filename) as file_media:
            data_media = json.load(file_media)
            messaggio = ""
            for key, value in data_media[f'{group_id}'].items():
                link = f"https://t.me/c/{group_id}/{value.split()[1]}"
                link = link.replace("-100", "")
                messaggio += f"{key} → [{value.split()[0]}]({link})\n"
            client.send_message(group_id, messaggio)
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# UNSET MEDIA
@app.on_message(filters.command("unsetmedia", "!"))
def unsetmedia(client, message):
    try:
        trigger = message.command[1]
        group_id = message.chat.id
        filename = f"{directory}/media.json"
        with open(filename, 'r') as file:
            file_data = json.load(file)
        del file_data[f'{group_id}'][f'{trigger}']
        with open(filename, 'w') as file:
            message.reply_text("Cancellato amo")
            json.dump(file_data, file, indent=4)
        return True
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# SET MEDIA
@app.on_message(filters.command("setmedia", "!"))
def setmedia(client, message):
    trigger = message.command[1]
    filename = f"{directory}/media.json"
    group_id = message.chat.id
    media_link = message.reply_to_message.link
    media_message_id = media_link.split("/")[5]
    media_type = message.reply_to_message.media
    with open(filename, 'r') as file:
        file_data = json.load(file)
    if not file_data.get(f'{group_id}'): 
        file_data[f'{group_id}'] = {}
    if media_type == "audio":
        file_data[f'{group_id}'][f'{trigger}'] = f'{media_type} {media_message_id}'
    elif media_type == "document":
        file_data[f'{group_id}'][f'{trigger}'] = f'{media_type} {media_message_id}'
    elif media_type == "photo":
        file_data[f'{group_id}'][f'{trigger}'] = f'{media_type} {media_message_id}'
    elif media_type == "sticker":
        file_data[f'{group_id}'][f'{trigger}'] = f'{media_type} {media_message_id}'
    elif media_type == "video":
        file_data[f'{group_id}'][f'{trigger}'] = f'{media_type} {media_message_id}'
    elif media_type == "animation":
        file_data[f'{group_id}'][f'{trigger}'] = f'{media_type} {media_message_id}'
    elif media_type == "voice":
        file_data[f'{group_id}'][f'{trigger}'] = f'{media_type} {media_message_id}'
    elif media_type == "video_note":
        file_data[f'{group_id}'][f'{trigger}'] = f'{media_type} {media_message_id}'
    else:
        pass
    with open(filename, 'w') as file:
        message.reply_text("Fatto amo")
        json.dump(file_data, file, indent=4)
    return True

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
        media_file = f"{directory}/media.json"
        bot_file = f"{directory}/pyro.py"
        config_ini_file = f"{directory}/config.ini"
        client.send_message(test_group, datetime.datetime.utcfromtimestamp(message.date + 3600).strftime('Backup eseguito il %d-%m-%Y alle ore %H:%M:%S.'))
        client.send_document(chat_id=test_group, document=sets_file)
        client.send_document(chat_id=test_group, document=reaccs_file)
        client.send_document(chat_id=test_group, document=media_file)
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
    with open(f"{directory}/cache/starting_quote.jpg", 'wb') as handler:
        handler.write(img_data)
    img = Image(filename=f"{directory}/cache/starting_quote.jpg")
    img.brightness_contrast(brightness=-20)
    quote_font1 = Font(f"{directory}/fonts/Vollkorn-Italic.ttf", color="black")
    quote_font2 = Font(f"{directory}/fonts/Vollkorn-Italic.ttf", color="white")
    author_font1 = Font(f"{directory}/fonts/Vollkorn-Regular.ttf", color="black")
    author_font2 = Font(f"{directory}/fonts/Vollkorn-Regular.ttf", color="white")

    if message.reply_to_message.forward_sender_name:
        author = message.reply_to_message.forward_sender_name
    elif message.reply_to_message.forward_from:
        author = message.reply_to_message.forward_from.first_name
    else:
        author = message.reply_to_message.from_user.first_name
    author = author.upper()

    with Drawing():
        img.caption(f'{message.reply_to_message.text}', left=62, top=62, width=680, height=270, font=quote_font1, gravity='west')
        img.caption(f'— {author}', left=62, top=352, width=680, height=70, font=author_font1, gravity='west')
        img.caption(f'{message.reply_to_message.text}', left=60, top=60, width=680, height=270, font=quote_font2, gravity='west')
        img.caption(f'— {author}', left=60, top=350, width=680, height=70, font=author_font2, gravity='west')
    img.save(filename=f"{directory}/cache/result_quote.jpg")
    message.reply_photo(f"{directory}/cache/result_quote.jpg")
    os.remove(f"{directory}/cache/starting_quote.jpg")
    os.remove(f"{directory}/cache/result_quote.jpg")

# READ DESCRIPTION
@app.on_message(filters.command("about", "!"))
def readgroupdescription(client, message):
    try:
        description = client.get_chat(message.chat.id).description
        message.reply_text(description)
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# SET DESCRIPTION
@app.on_message(filters.command("setabout", "!"))
def setgroupdescription(client, message):
    new_description = message.text[9 + 1:]
    try:
        chat_info = client.get_chat(message.chat.id)
        old_description = chat_info.description
        message.reply_text("Nuova descrizione impostata, quella vecchia era:\n" + old_description)
        client.set_chat_description(message.chat.id, new_description)
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# UNSET REACTION
@app.on_message(filters.command("unreacc", "!"))
def unsetreacc(client, message):
    trigger = message.command[1]
    group_id = message.chat.id
    filename = f"{directory}/reactions.json"
    with open(filename, 'r') as file:
        file_data = json.load(file)
    del file_data[f'{group_id}'][f'{trigger}']
    with open(filename, 'w') as file:
        message.reply_text("Cancellato amo")
        json.dump(file_data, file, indent=4)
    return True

# GET REACTION LIST
@app.on_message(filters.command("reaccs", "!"))
def getreacclist(client, message):
    group_id = message.chat.id
    filename = f"{directory}/reactions.json"
    try:
        with open(filename) as file_reaccs:
            data_reaccs = json.load(file_reaccs)
            messaggio = ""
            for key, value in data_reaccs[f'{group_id}'].items():
                messaggio += f"{key} → {value}\n"
            client.send_message(group_id, messaggio)
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# SET REACTION
@app.on_message(filters.command("setreacc", "!"))
def setreacc(client, message):
    trigger = message.command[1]
    reaction = message.command[2]
    group_id = message.chat.id
    filename = f"{directory}/reactions.json"
    reactions = ["👍", "👎", "❤️", "🔥", "🎉", "🤩", "😱", "😁", "😢", "💩", "🤮"]  
    if any(x in reaction for x in reactions):
        with open(filename, 'r') as file:
            file_data = json.load(file)
        if not file_data.get(f'{group_id}'): 
            file_data[f'{group_id}'] = {}
        file_data[f'{group_id}'][f'{trigger}'] = f'{reaction}'
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
    try:
        client.send_reaction(message.chat.id, message_id, "🤮")
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# VERSION
@app.on_message(filters.command("version", "!"))
def version(client, message):
    last_modified = os.path.getmtime(f"{directory}/pyro.py")
    versioning = datetime.datetime.utcfromtimestamp(last_modified + 3600).strftime('%Y.%m%d.%H%M')
    message.reply_text(f"Version {versioning}\nhttps://github.com/DDF95/TARSbot")

# SET CHAT PICTURE
@app.on_message(filters.command("setpicture", "!"))
def grouppropic(client, message):
    try:
        image = message.reply_to_message.photo.file_id
        client.set_chat_photo(chat_id=message.chat.id, photo=image)
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# TWITTER TIMELINE
@app.on_message(filters.command("tweets", "!"))
def timelineTW(client, message):
    userStr = ' '.join(message.command[1:])
    userStrFixed = userStr.replace("@", "")
    try:
        userResponse = tw_client.get_user(username=userStrFixed)
        twUserID = userResponse.data['id']
        tweets = tw_client.get_users_tweets(id=twUserID, tweet_fields=['context_annotations','created_at','geo'], max_results=5, exclude="replies,retweets")
        for tweet in tweets.data:
            client.send_message(message.chat.id, tweet)
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

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
    try:
        submissions = list(reddit.subreddit(redditStr).hot(limit=27))
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")
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
                message.reply_text("Scarico la galleria, potrebbe volerci qualche secondo...")
                ids = [i['media_id'] for i in submission.gallery_data['items']]
                for id in ids:
                    url = submission.media_metadata[id]['p'][0]['u']
                    url = url.split("?")[0].replace("preview", "i")
                    gallery.append(url)
                for index, url in enumerate(gallery):
                    link = urllib.request.urlopen(url)
                    try:
                        name = f"{directory}/cache/image{index+1}.jpg"
                        images.append(name)
                        with open(name, "wb") as output:
                            output.write(link.read())
                    except IOError:
                        print("Unable to create file")
                client.send_media_group(reply_to_message_id=message.message_id, chat_id=message.chat.id, media=[InputMediaPhoto(name) for name in images[:10]])
                client.send_message(message.chat.id, media_caption, disable_web_page_preview=True)
                files = glob.glob(f"{directory}/cache/*")
                for f in files:
                    os.remove(f)

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
                video_file = f"{directory}/cache/video.mp4"
                audio_file = f"{directory}/cache/audio.mp4"
                link_video = urllib.request.urlopen(url)
                link_audio = urllib.request.urlopen(url_audio)
                with open(video_file, "wb") as output:
                    output.write(link_video.read())
                with open(audio_file, "wb") as output:
                    output.write(link_audio.read())
                video_file_finale = f"{directory}/cache/video_con_audio.mp4"
                ff = ffmpy.FFmpeg(
                    inputs={url: None, url_audio: None},
                    outputs={video_file_finale: '-y -c:v copy -c:a aac -loglevel quiet'})
                ff.run()
                cv2video = cv2.VideoCapture(video_file_finale)
                height = cv2video.get(cv2.CAP_PROP_FRAME_HEIGHT)
                width  = cv2video.get(cv2.CAP_PROP_FRAME_WIDTH) 
                message.reply_video(video=video_file_finale, caption=media_caption, height=int(height), width=int(width))
                files = glob.glob(f"{directory}/cache/*")
                for f in files:
                    os.remove(f)
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
    try:
        message.reply_to_message.delete()
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# GOOGLE SEARCH
@app.on_message(filters.command("search", "!"))
def gsearch(client, message):
    searchStr = message.command[1:]
    page = 1
    start = (page - 1) * 10 + 1
    url = f"https://www.googleapis.com/customsearch/v1?key={google_apikey}&cx={google_cseid}&q={searchStr}&start={start}"
    try:
        data = requests.get(url).json()
        search_items = data.get("items")
        resultsStr = ""
        for search_item in enumerate(search_items, start=1):
            title = search_item.get("title")
            html_snippet = search_item.get("htmlSnippet")
            link = search_item.get("link")
            resultsStr += f"<b>{title}</b>\n<i>{html_snippet}</i>\n{link}\n\n"
        message.reply_text(resultsStr, disable_web_page_preview=True)
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# GOOGLE IMAGE SEARCH
@app.on_message(filters.command("img", "!"))
def gimgsearch(client, message):
    searchStr = ' '.join(message.command[1:])
    try:
        resource = build("customsearch", 'v1', developerKey=google_apikey).cse()
        result = resource.list(q=searchStr, cx=google_cseid, searchType='image').execute()
        randomInt = random.randrange(10)
        message.reply_photo(result['items'][randomInt]['link'])
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# LATEX
@app.on_message(filters.command("latex", "!"))
def latex(client, message):
    latexStr = ' '.join(message.command[1:])
    latexEscaped = urllib.parse.quote("\dpi{200}" + latexStr)
    try:
        latexRequest = "https://latex.codecogs.com/png.image?" + latexEscaped
        message.reply_photo(latexRequest)
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# FOX
@app.on_message(filters.command("fox", "!"))
def fox(client, message):
    try:
        foxRequest = requests.get("https://randomfox.ca/floof/")
        message.reply_photo(foxRequest.json()['image'])
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# UNFOLLOW
@app.on_message(filters.command("unfollow", "!"))
def unfollowTW(client, message):
    userStr = ' '.join(message.command[1:])
    userStrFixed = userStr.replace("@", "")
    try:
        userResponse = tw_client.get_user(username=userStrFixed)
        twUserID = userResponse.data['id']
        tw_client.unfollow_user(twUserID)
        message.reply_text("Ho unfollowato @" + userStrFixed + " su Twitter")
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# FOLLOW
@app.on_message(filters.command("follow", "!"))
def followTW(client, message):
    userStr = ' '.join(message.command[1:])
    userStrFixed = userStr.replace("@", "")
    try:
        userResponse = tw_client.get_user(username=userStrFixed)
        twUserID = userResponse.data['id']
        tw_client.follow_user(twUserID)
        message.reply_text("Ho followato @" + userStrFixed + " su Twitter")
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

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
    tweetStr = message.text[2 + 1:]
    try:
        response = tw_client.create_tweet(text=tweetStr)
        message.reply_text("Ho inviato il tweet amo: https://twitter.com/rTARSbot/status/" + response.data['id'])
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# HTML2PDF
@app.on_message(filters.command("html2pdf", "!"))
def html2pdf(client, message):
    html2pdfStr = ' '.join(message.command[1:])
    linkRequests = f"https://api.html2pdf.app/v1/generate?url={html2pdfStr}&apiKey={h2p_apiKey}"
    try:
        result = requests.get(linkRequests).content
        document = f"{directory}/cache/document.pdf"
        with open(document, "wb") as handler:
            handler.write(result)
            app.send_document(message.chat.id, document)
            os.remove(f"{directory}/cache/document.pdf")
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# QR CODE 
@app.on_message(filters.command("qr", "!"))
def qrcode(client, message):
    qrStr = message.text[2 + 1:]
    try:
        qrStrEsc = urllib.parse.quote(qrStr)
        message.reply_photo("https://api.qrserver.com/v1/create-qr-code/?size=500x500&data=" + qrStrEsc)
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# CAT
@app.on_message(filters.command("cat", "!"))
def cat(client, message):
    try:
        catRequest = requests.get("https://api.thecatapi.com/v1/images/search")
        message.reply_photo(catRequest.json()[0]['url'])
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# DOG
@app.on_message(filters.command("dog", "!"))
def dog(client, message):
    try:
        dogRequest = requests.get("https://dog.ceo/api/breeds/image/random")
        message.reply_photo(dogRequest.json()['message'])
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# GLASSES 
@app.on_message(filters.command("glasses", "!"))
def glasses(client, message):
    try:
        glassesStr = message.text[7 + 1:]
        phrase1and2 = glassesStr.split(" - ")
        phrase1 = phrase1and2[0]
        phrase2 = phrase1and2[1]
        message.reply_text(phrase1 + "\n\n<code>(•_•)\n( •_•)>⌐■-■\n(⌐■_■)</code> " + phrase2)
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# HELP
@app.on_message(filters.command("help", list("/.!")))
def help(client, message):
    message.reply_text("""<b>Chat commands</b>
• <code>!about</code>: Read group description.
• <code>!del</code>: Deletes the message you're replying to.
• <code>!find [text]</code>: Searchs for text messages inside the chat and returns a random result.
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
• <code>!reaccs</code>: Shows the list of saved reactions.
• <code>!setreacc [trigger] [reaction emoji]</code>: Saves a reaction that will automatically be sent when the trigger word appears.
• <code>!unreacc [trigger]</code>: Deletes the reaction. 
• <code>!vomita</code>: Reply this to vomit on a message.

<b>Set commands</b>
• <code>!get</code>: Returns the list of saved sets.
• <code>!set [trigger] [text]</code>: Saves a text that will automatically be sent when the trigger word appears.
• <code>!unset [trigger]</code>: Deletes the text associated with the trigger word.
• <code>!media</code>: Returns the list of media saved.
• <code>!setmedia [trigger]</code>: Reply this to a message to save a media object (photo, video, sticker, etc...) that will automatically be sent when the trigger word appears.
• <code>!unsetmedia [trigger]</code>: Deletes the media object associated with the trigger word.

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
    echo_str = message.text[6:]
    client.send_message(message.chat.id, echo_str)
    
# URBAN DICTIONARY
@app.on_message(filters.command("ud", "!"))
def ud(client, message):
    searchStr = ' '.join(message.command[1:])
    searchEscaped = urllib.parse.quote(searchStr)
    try:
        wordRequest = requests.get('http://api.urbandictionary.com/v0/define?term=' + searchEscaped)
        message.reply_text(
            '**' + wordRequest.json()['list'][0]['word'] + '**' + '\n' +
            wordRequest.json()['list'][0]['definition'] + '\n\nExamples: \n' +
            '__' + wordRequest.json()['list'][0]['example'] + '__', parse_mode = 'markdown'
            )
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# LYRICS 
@app.on_message(filters.command("lyrics", "!"))
def lyrics(client, message):
    searchStr = ' '.join(message.command[1:])
    authorandsong = searchStr.split(" - ")
    author = authorandsong[0]
    song = authorandsong[1]
    authorEsc = urllib.parse.quote(author)
    songEsc = urllib.parse.quote(song)
    try:
        lyricsRequest = requests.get("https://api.lyrics.ovh/v1/" + authorEsc + "/" + songEsc)
        message.reply_text(lyricsRequest.json()['lyrics'])
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

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
    try:
        locRequest = requests.get('http://api.openweathermap.org/geo/1.0/direct?q=' + locEscaped + '&limit=1&appid=' + owm_appid)
        client.send_location(message.chat.id, locRequest.json()[0]['lat'], locRequest.json()[0]['lon'])
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# JOIN CHAT
@app.on_message(filters.command("join", "!"))
def join(client, message):
    linkStr = ' '.join(message.command[1:])
    linkFixed = linkStr.replace("+", "joinchat/")
    try:
        client.join_chat(linkFixed)
        message.reply_text("Ho joinato amo")
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

# PIN
@app.on_message(filters.command("pin", "!"))
def pin(client, message):
    try:
        message.reply_to_message.pin()
    except Exception as e:
        message.reply_text(f"Errore:\n<code>{e}</code>")

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
    group_id = message.chat.id
    filename = f"{directory}/sets.json"
    with open(filename, 'r') as file:
        file_data = json.load(file)
    if not file_data.get(f'{group_id}'): 
        file_data[f'{group_id}'] = {}
    file_data[f'{group_id}'][f'{trigger}'] = f'{risposta}'
    with open(filename, 'w') as file:
        message.reply_text("Fatto amo")
        json.dump(file_data, file, indent=4)
    return True

# UNSET
@app.on_message(filters.command("unset", "!"))
def unset(client, message):
    trigger = message.command[1]
    group_id = message.chat.id
    filename = f"{directory}/sets.json"
    with open(filename, 'r') as file:
        file_data = json.load(file)
    del file_data[f'{group_id}'][f'{trigger}']
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
    mathExpr = message.text[4 + 1:]
    mathExprEscaped = urllib.parse.quote(mathExpr)
    mathjsRequest = requests.get('https://api.mathjs.org/v4/?expr=' + mathExprEscaped)
    risultato = mathjsRequest.text
    message.reply_text(risultato)

# GET LIST
@app.on_message(filters.command("get", "!"))
def getlist(client, message):
    group_id = message.chat.id
    filename = f"{directory}/sets.json"
    try:
        with open(filename) as file_sets:
            data_sets = json.load(file_sets)
            messaggio = ""
            for key, value in data_sets[f'{group_id}'].items():
                if len(value) > 20:
                    messaggio += f'{key} → "{value[:20]}..."\n'
                else:
                    messaggio += f'{key} → "{value}"\n'
            client.send_message(group_id, messaggio)
    except:
        pass

# GET
@app.on_message(filters.text)
def get(client, message):
    group_id = message.chat.id
    wordList = message.text.split() 
    getFirstWord = wordList[0]
    setsfilename = f"{directory}/sets.json"
    try:
        with open(setsfilename) as fileSets:
            dataSets = json.load(fileSets)
        client.send_message(group_id, dataSets[f'{group_id}'][f'{getFirstWord}'])
    except:
        pass

    # MEDIA
    media_filename = f"{directory}/media.json"
    try:
        with open(media_filename) as file_media:
            data_media = json.load(file_media)
    
        media_type = data_media[f'{group_id}'][f'{getFirstWord}'].split()[0]
        media_message_id = data_media[f'{group_id}'][f'{getFirstWord}'].split()[1]
        media_message = app.get_messages(group_id, int(media_message_id))

        if media_type == "audio":
            client.send_audio(group_id, media_message.audio.file_id)
        elif media_type == "document":
            client.send_document(group_id, media_message.document.file_id)
        elif media_type == "photo":
            client.send_photo(group_id, media_message.photo.file_id)
        elif media_type == "sticker":
            client.send_sticker(group_id, media_message.sticker.file_id)
        elif media_type == "video":
            client.send_video(group_id, media_message.video.file_id)
        elif media_type == "animation":
            client.send_animation(group_id, media_message.animation.file_id)
        elif media_type == "voice":
            client.send_voice(group_id, media_message.voice.file_id)
        elif media_type == "video_note":
            client.send_video_note(group_id, media_message.video_note.file_id)
        else:
            pass
    except:
        pass

    # REACTIONS
    message_id = message.message_id
    reaccsfilename = f"{directory}/reactions.json"
    try:
        with open(reaccsfilename) as fileReaccs:
            dataReaccs = json.load(fileReaccs)
        keys = dataReaccs[str(group_id)].keys()
        triggerWords = list(filter(lambda x: x in keys, wordList))
        if any(x in keys for x in wordList):
            try: 
                client.send_reaction(group_id, message_id, dataReaccs[str(group_id)][triggerWords[0]])
            except:
                pass
    except:
        pass

app.run()
