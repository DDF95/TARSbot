import json
import requests

from imdb import IMDb
from pyrogram import Client, enums, filters


def trim_description(caption, description):
    max_caption_length = 1024
    if len(caption) > max_caption_length:
        trim_length = max_caption_length - (len(caption) - len(description) + 5)
        return description[:trim_length] + "[...]"
    return description


def get_director(imdb_id):
    try:
        ia = IMDb()
        movie = ia.get_movie(imdb_id.lstrip("tt"))
        directors = movie.get('directors')
        return directors[0]['name'] if directors else ""
    except Exception as e:
        return str(e)


def get_preferred_torrent(torrents):
    preferred_torrent = None
    for torrent in torrents:
        if torrent['quality'] == "1080p":
            is_bluray_x264 = torrent['type'].lower() == "bluray" and torrent['video_codec'].lower() == "x264"
            is_webrip_x264 = torrent['type'].lower() in ["web", "webrip"] and torrent['video_codec'].lower() == "x264"
            is_x265 = torrent['video_codec'].lower() == "x265"
            size_bytes = torrent.get('size_bytes', 0)

            if is_bluray_x264:
                if size_bytes <= 4 * 1024**3:
                    return torrent
                preferred_torrent = preferred_torrent or (torrent if is_x265 else preferred_torrent)
            elif is_webrip_x264 and not preferred_torrent:
                preferred_torrent = torrent
            elif not preferred_torrent:
                preferred_torrent = torrent
    return preferred_torrent or torrents[0]


@Client.on_message(filters.command("yts", "!"))
async def movie_search(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)

    try:
        query = " ".join(message.command[1:])
        url = "https://yts.mx/api/v2/list_movies.json"
        params = {"query_term": query, "limit": 1}
        r = requests.get(url, params=params)
        movies = r.json().get("data", {}).get("movies", [])

        if not movies:
            await message.reply("No movies found.")
            return
        
        movie = movies[0]
        title = movie['title']
        year = movie['year']
        rating = movie['rating']
        imdb_id = movie.get('imdb_code')
        description = movie['summary'] if movie['summary'] else ""
        genres = ", ".join(movie['genres']) if movie.get('genres') else ""
        poster_url = movie['large_cover_image']
        
        director = get_director(imdb_id) if imdb_id else ""
        details_url = f"https://yts.mx/api/v2/movie_details.json?movie_id={movie['id']}&with_cast=true"
        details_response = requests.get(details_url)
        movie_details = details_response.json().get("data", {}).get("movie", {})
        cast_data = movie_details.get("cast", [])
        cast = "\n".join([f"• **{actor['name']}** as __{actor['character_name']}__" for actor in cast_data]) if cast_data else ""

        torrents = movie.get('torrents', [])
        preferred_torrent = get_preferred_torrent(torrents)
        if preferred_torrent:
            torrent_url = preferred_torrent['url']
            torrent_type = f"{preferred_torrent['type']} {preferred_torrent['video_codec']}"
            torrent_size = preferred_torrent['size']

            torrent_response = requests.get(torrent_url)
            if torrent_response.status_code == 200:
                content_disposition = torrent_response.headers.get('content-disposition')
                if content_disposition:
                    filename = content_disposition.split("filename=")[1].strip('"')
                else:
                    filename = f"{torrent_url.split('/')[-1]}"
                
                with open(filename, 'wb') as f:
                    f.write(torrent_response.content)
                torrent_file_path = filename
            else:
                await message.reply("Torrent file not found.")
                return
            
            caption_parts = [
                f"**{title} ({year})**",
                f"**Directed by:** {director}" if director else "",
                f"**Rating:** {rating}/10" if rating else "",
                f"**Genres:** {genres}" if genres else "",
                f"**Description:** {description}" if description else "",
                f"**Cast:**\n{cast}" if cast else ""
            ]
            caption = "\n\n".join(part for part in caption_parts if part)
            caption = caption.replace(description, trim_description(caption, description))
            
            await message.reply_photo(poster_url, caption=caption)
            await message.reply_document(torrent_file_path, caption=f"Torrent file for `{title} ({year})`\nSize: {torrent_size} ({torrent_type})")
        
        else:
            await message.reply(f"`{title} ({year})`\n\n**Rating:** {rating}/10\n\nNo suitable torrents available.")
        
    except Exception as e:
        await message.reply(f"Error:\n<code>{e}</code>")


@Client.on_message(filters.command("searchyts", "!"))
async def movie_search_list(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)

    try:
        query = " ".join(message.command[1:])
        url = "https://yts.mx/api/v2/list_movies.json"
        params = {"query_term": query, "limit": 5}
        r = requests.get(url, params=params)
        movies = r.json().get("data", {}).get("movies", [])

        if not movies:
            await message.reply("No movies found.")
            return

        response = ""
        for movie in movies:
            title = movie['title']
            year = movie['year']
            imdb_id = movie.get('imdb_code')
            director = get_director(imdb_id) if imdb_id else None

            torrents = movie.get('torrents', [])
            preferred_torrent = get_preferred_torrent(torrents)
            if preferred_torrent:
                torrent_hash = preferred_torrent['hash']
                torrent_type = f"{preferred_torrent['type']} {preferred_torrent['video_codec']}"
                torrent_size = preferred_torrent['size']
                response += f"**{title} ({year})**\n"
                if director:
                    response += f"Directed by: {director}\n"
                response += f"/ytstorrent_{torrent_hash} ({torrent_type}, {torrent_size})\n\n"

        await message.reply(response)
        
    except Exception as e:
        await message.reply(f"Error:\n<code>{e}</code>")


@Client.on_message(filters.regex(r"^/ytstorrent_([a-zA-Z0-9]+)$"))
async def download_torrent(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_DOCUMENT)

    try:
        torrent_hash = message.matches[0].group(1)
        torrent_url = f"https://yts.mx/torrent/download/{torrent_hash}"

        torrent_response = requests.get(torrent_url)
        if torrent_response.status_code == 200:
            content_disposition = torrent_response.headers.get('content-disposition')
            if content_disposition:
                filename = content_disposition.split("filename=")[1].strip('"')
            else:
                filename = f"{torrent_hash}.torrent"

            with open(filename, 'wb') as f:
                f.write(torrent_response.content)
            await message.reply_document(filename)
        else:
            await message.reply("Torrent file not found.")
        
    except Exception as e:
        await message.reply(f"Error:\n<code>{e}</code>")


@Client.on_message(filters.command("debugyts", "!"))
async def debug_movie(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_DOCUMENT)

    try:
        query = " ".join(message.command[1:])
        
        search_url = "https://yts.mx/api/v2/list_movies.json"
        search_params = {"query_term": query, "limit": 5}
        search_response = requests.get(search_url, params=search_params)
        search_data = search_response.json()

        movie_url = "https://yts.mx/api/v2/list_movies.json"
        movie_params = {"query_term": query, "limit": 1}
        movie_response = requests.get(movie_url, params=movie_params)
        movie_data = movie_response.json()
        
        if movie_data.get("data", {}).get("movies"):
            movie_id = movie_data["data"]["movies"][0]["id"]
            details_url = f"https://yts.mx/api/v2/movie_details.json?movie_id={movie_id}&with_cast=true"
            details_response = requests.get(details_url)
            movie_details = details_response.json()
        else:
            movie_details = {}

        with open("search_data.txt", "w") as f:
            json.dump(search_data, f, indent=4)
        with open("movie_data.txt", "w") as f:
            json.dump(movie_data, f, indent=4)
        with open("movie_details.txt", "w") as f:
            json.dump(movie_details, f, indent=4)
        
        await message.reply_document("search_data.txt", caption="Search data")
        await message.reply_document("movie_data.txt", caption="Main movie data")
        await message.reply_document("movie_details.txt", caption="Detailed movie data with cast")
        
    except Exception as e:
        await message.reply(f"Error:\n<code>{e}</code>")