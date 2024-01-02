import random
import urllib.request
from configparser import ConfigParser
from io import BytesIO

import cv2
import ffmpy
import praw
from pyrogram import Client, enums, filters
from pyrogram.types import InputMediaPhoto


cfg = ConfigParser(interpolation=None)
cfg.read("config.ini")

CLIENT_ID = cfg.get("reddit", "reddit_client_id")
CLIENT_SECRET = cfg.get("reddit", "reddit_client_secret")
USER_AGENT = cfg.get("reddit", "reddit_user_agent")

reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)


@Client.on_message(filters.command("reddit", "!"))
async def reddit_download(client, message):
    if len(message.command) == 1 or len(message.command) > 3: 
        await message.reply(text="Usage:\n`!reddit <subreddit>`\n`!reddit <subreddit> <1-27>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        sub_to_search = message.command[1]

        submissions = list(reddit.subreddit(sub_to_search).hot(limit=27))
    
        if len(message.command) == 2:
            submission = random.choice(submissions)
        else:
            submission = submissions[int(message.command[2])]

        title = submission.title
        upvotes = submission.score
        url = submission.url
        permalink = f"https://reddit.com{submission.permalink}"
        sub = f"r/{submission.subreddit}"

        gallery = []
        media_caption = f"<b>{title}</b>\n{upvotes} upvotes | <a href='{permalink}'>{sub}</a>"

        if submission.is_self == True:
            text_self = f"<b>{title}</b>\n{upvotes} upvotes | <a href='{permalink}'>{sub}</a>\n\n{submission.selftext}"
            if len(text_self) > 4096:
                for x in range(0, len(text_self), 4096):
                    await message.reply(text_self[x:x + 4096], disable_web_page_preview=True)
            else:
                await message.reply(text_self, disable_web_page_preview=True)
        else:
            if "redd" in url:
                if "gallery" in url:
                    wait_message = await message.reply("Downloading gallery...")

                    ids = [i['media_id'] for i in submission.gallery_data['items']]
                    for index, id in enumerate(ids):
                        url = submission.media_metadata[id]['p'][0]['u']
                        url = url.split("?")[0].replace("preview", "i")
                        r = urllib.request.urlopen(url)
                        image = BytesIO(r.read())
                        image.name = f"{index}.jpg"
                        gallery.append(image)

                    await message.reply_media_group(media=[InputMediaPhoto(item) for item in gallery[:10]])
                    await message.reply(media_caption, disable_web_page_preview=True)
                    await wait_message.delete()


                elif submission.url.endswith(".gif"):
                    videourl = submission.preview['images'][0]['variants']['mp4']['source']['url']
                    await message.reply_video(video=videourl, caption=media_caption)

                elif "v.redd.it" in url:
                    await message.reply("Downloading video...")
                    url = submission.media['reddit_video']['fallback_url']
                    url = url.replace("?source=fallback", "")
                    url_audio = url.replace("1080", "audio")
                    url_audio = url_audio.replace("720", "audio")
                    url_audio = url_audio.replace("360", "audio")

                    output_file = BytesIO()

                    ff = ffmpy.FFmpeg(inputs={url: None, url_audio: None}, outputs={output_file: '-y -c:v copy -c:a aac -loglevel quiet'})
                    ff.run()
                    cv2video = cv2.VideoCapture(output_file)
                    height = cv2video.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    width  = cv2video.get(cv2.CAP_PROP_FRAME_WIDTH)

                    await message.reply_video(video=output_file, caption=media_caption, height=int(height), width=int(width))
                else:
                    await message.reply_photo(photo=url, caption=media_caption)

            elif "imgur" in url:
                if submission.url.endswith(".gif") or submission.url.endswith(".gifv"):
                    videourl = url.replace("gifv", "mp4")
                    videourl = url.replace("gif", "mp4")
                    await message.reply_video(video=videourl, caption=media_caption)
                else:
                    url += ".jpeg"
                    await message.reply_photo(photo=url, caption=media_caption)

            elif "gfycat" in url:
                url = submission.media['oembed']['thumbnail_url'][:-20]
                videourl = f"{url}-mobile.mp4"
                await message.reply_video(video=videourl, caption=media_caption)

            elif "redgifs.com" in url:
                videourl = submission.preview['reddit_video_preview']['fallback_url']
                await message.reply_video(video=videourl, caption=media_caption)
            else:
                await message.reply_text(f"<b>{title}</b>\n{url}\n\n{upvotes} upvotes | <a href='{permalink}'>{sub}</a>")
            
