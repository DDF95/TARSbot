import os
import re
from pyrogram import Client, filters
from googleapiclient.discovery import build

YT_API_KEY = os.environ.get("YT_API_KEY")
if not YT_API_KEY:
    raise RuntimeError("Set YT_API_KEY environment variable")

youtube = build("youtube", "v3", developerKey=YT_API_KEY, cache_discovery=False)

def iso8601_duration_to_hms(duration_iso: str) -> str:
    pattern = re.compile(
        r"^P(?:\d+Y)?(?:\d+M)?(?:\d+W)?(?:\d+D)?"
        r"(?:T(?:(?P<h>\d+)H)?(?:(?P<m>\d+)M)?(?:(?P<s>\d+)S)?)?$"
    )
    m = pattern.match(duration_iso)
    if not m:
        return duration_iso
    h = int(m.group("h")) if m.group("h") else 0
    mm = int(m.group("m")) if m.group("m") else 0
    s = int(m.group("s")) if m.group("s") else 0
    if h:
        return f"{h}:{mm:02d}:{s:02d}"
    else:
        return f"{mm}:{s:02d}"

def search_first_video(query: str):
    res = youtube.search().list(q=query, part="snippet", maxResults=1, type="video").execute()
    items = res.get("items", [])
    if not items:
        return None
    vid = items[0]
    return {"video_id": vid["id"]["videoId"], "title": vid["snippet"]["title"], "channel": vid["snippet"]["channelTitle"]}

def get_video_details(video_id: str):
    res = youtube.videos().list(part="contentDetails,statistics,snippet", id=video_id).execute()
    items = res.get("items", [])
    if not items:
        return None
    it = items[0]
    return {
        "duration_iso": it["contentDetails"].get("duration"),
        "view_count": it.get("statistics", {}).get("viewCount"),
        "title": it["snippet"]["title"],
        "channel": it["snippet"]["channelTitle"],
    }

@Client.on_message(filters.regex(r"(?i)alexa play (.+)"))
async def alexa(client, message):
    query = message.matches[0].group(1).strip()

    try:
        v = search_first_video(query)
        if not v:
            await message.reply("No video found for that query.")
            return

        details = get_video_details(v["video_id"])
        if not details:
            await message.reply("Could not fetch video details.")
            return

        duration = iso8601_duration_to_hms(details["duration_iso"]) if details.get("duration_iso") else "N/A"
        views = details.get("view_count") or "N/A"
        url = f"https://www.youtube.com/watch?v={v['video_id']}"

        text = (
            f"{details['title']}\n\n"
            f"{duration} | {views} views\n\n"
            f"{url}"
        )
        await message.reply(text)
    except Exception as e:
        print("YouTube API error:", e)
        await message.reply("❌ Error contacting YouTube API. Check server logs.")
