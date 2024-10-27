import aiofiles
import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

from imdb import IMDb
from pyrogram import Client, enums, filters


ia = IMDb()
executor = ThreadPoolExecutor()


def trim_description(caption, description):
    max_caption_length = 1024
    if len(caption) > max_caption_length:
        trim_length = max_caption_length - (len(caption) - len(description) + 5)
        return description[:trim_length] + "[...]"
    return description


async def get_director(imdb_id):
    loop = asyncio.get_running_loop()
    try:
        movie = await loop.run_in_executor(executor, ia.get_movie, imdb_id.lstrip("tt"))
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
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                data = await r.json()
        movies = data.get("data", {}).get("movies", [])

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
        
        director = await get_director(imdb_id) if imdb_id else ""
        
        details_url = f"https://yts.mx/api/v2/movie_details.json?movie_id={movie['id']}&with_cast=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(details_url) as details_response:
                movie_details = await details_response.json()
        
        cast_data = movie_details.get("data", {}).get("movie", {}).get("cast", [])
        cast = "\n".join([f"• **{actor['name']}** as __{actor['character_name']}__" for actor in cast_data]) if cast_data else ""

        torrents = movie.get('torrents', [])
        preferred_torrent = get_preferred_torrent(torrents)
        if preferred_torrent:
            torrent_url = preferred_torrent['url']
            torrent_type = f"{preferred_torrent['type']} {preferred_torrent['video_codec']}"
            torrent_size = preferred_torrent['size']

            async with aiohttp.ClientSession() as session:
                async with session.get(torrent_url) as torrent_response:
                    if torrent_response.status == 200:
                        content_disposition = torrent_response.headers.get('content-disposition')
                        if content_disposition:
                            filename = content_disposition.split("filename=")[1].strip('"')
                        else:
                            filename = f"{torrent_url.split('/')[-1]}"
                        with open(filename, 'wb') as f:
                            f.write(await torrent_response.read())
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
            await message.reply_document(filename, caption=f"Torrent file for `{title} ({year})`\nSize: {torrent_size} ({torrent_type})")
        
        else:
            await message.reply(f"`{title} ({year})`\n\n**Rating:** {rating}/10\n\nNo suitable torrents available.")
        
    except Exception as e:
        await message.reply(f"Error:\n<code>{e}</code>")


@Client.on_message(filters.command("searchyts", "!"))
async def movie_search_list(client, message):
    results_message = await message.reply("Searching... (this can take a while)")

    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)

    try:
        query = " ".join(message.command[1:])
        url = "https://yts.mx/api/v2/list_movies.json"
        params = {"query_term": query, "limit": 10}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                data = await r.json()
        movies = data.get("data", {}).get("movies", [])

        if not movies:
            await message.reply("No movies found.")
            return

        response = ""
        for movie in movies:
            title = movie['title']
            year = movie['year']
            imdb_id = movie.get('imdb_code')
            director = await get_director(imdb_id) if imdb_id else None

            torrents = movie.get('torrents', [])
            preferred_torrent = get_preferred_torrent(torrents)
            if preferred_torrent:
                torrent_hash = preferred_torrent['hash']
                torrent_type = f"{preferred_torrent['type']} {preferred_torrent['video_codec']}"
                torrent_size = preferred_torrent['size']
                response += f"**{title} ({year})**\n"
                if director:
                    response += f"Directed by: {director}\n"
                if message.chat.type == enums.ChatType.GROUP or message.chat.type == enums.ChatType.SUPERGROUP:
                    response += f"/yts{torrent_hash} ({torrent_type}, {torrent_size})\n\n"
                else:
                    response += f"Tap to copy: `/yts{torrent_hash}` ({torrent_type}, {torrent_size})\n\n"
        await results_message.edit(response)
        
    except Exception as e:
        await results_message.edit(f"Error:\n<code>{e}</code>")


@Client.on_message(filters.regex(r"^/yts([a-zA-Z0-9]+)$"))
async def download_torrent(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_DOCUMENT)

    try:
        torrent_hash = message.matches[0].group(1)
        torrent_url = f"https://yts.mx/torrent/download/{torrent_hash}"

        async with aiohttp.ClientSession() as session:
            async with session.get(torrent_url) as torrent_response:
                if torrent_response.status == 200:
                    content_disposition = torrent_response.headers.get('content-disposition')
                    if content_disposition:
                        filename = content_disposition.split("filename=")[1].strip('"')
                    else:
                        filename = f"{torrent_hash}.torrent"

                    with open(filename, 'wb') as f:
                        f.write(await torrent_response.read())
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
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=search_params) as search_response:
                search_data = await search_response.json()
            
            movie_url = "https://yts.mx/api/v2/list_movies.json"
            movie_params = {"query_term": query, "limit": 1}
            async with session.get(movie_url, params=movie_params) as movie_response:
                movie_data = await movie_response.json()
        
            movie_details = {}
            if movie_data.get("data", {}).get("movies"):
                movie_id = movie_data["data"]["movies"][0]["id"]
                details_url = f"https://yts.mx/api/v2/movie_details.json?movie_id={movie_id}&with_cast=true"
                async with session.get(details_url) as details_response:
                    movie_details = await details_response.json()

        async with aiofiles.open("search_data.txt", "w") as f:
            await f.write(json.dumps(search_data, indent=4))
        async with aiofiles.open("movie_data.txt", "w") as f:
            await f.write(json.dumps(movie_data, indent=4))
        async with aiofiles.open("movie_details.txt", "w") as f:
            await f.write(json.dumps(movie_details, indent=4))

        await message.reply_document("search_data.txt", caption="Search data")
        await message.reply_document("movie_data.txt", caption="Main movie data")
        await message.reply_document("movie_details.txt", caption="Detailed movie data with cast")
        
    except Exception as e:
        await message.reply(f"Error:\n<code>{e}</code>")
