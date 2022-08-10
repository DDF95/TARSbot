from justwatch import JustWatch
from pyrogram import Client, enums, filters


@Client.on_message(filters.command("watch", "!"))
async def watch(client, message):
    if len(message.command) == 1:
        await message.reply(text="Usage: `!watch <movie or show>` - this will only show Italian results for now", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        query = message.text[1+5+1:]
        just_watch = JustWatch(country='IT')

        message_jw = ""
        results = just_watch.search_for_item(query=query)
        offers = {}

        try:
            for offer in results['items'][0]['offers']:
                if offer['monetization_type'] == 'flatrate':
                    offer_type = "Streaming"
                elif offer['monetization_type'] == 'buy':
                    offer_type = "Buy"
                elif offer['monetization_type'] == 'rent':
                    offer_type = "Rent"
                elif offer['monetization_type'] == 'ads':
                    offer_type = "Streaming (ads)"
                else:
                    offer_type = offer['monetization_type']

                if offer['package_short_name'] == 'dnp':
                    urls = offer['urls']['standard_web'].split("u=")
                    url = urls[1].split("&")
                    url = url[0]
                else:
                    url = offer['urls']['standard_web']

                if url not in offers:
                    offers[url] = {"providers": "", "type": set(), "stagioni": 0}
                offers[url]['providers'] = offer['package_short_name']
                offers[url]['type'].add(offer_type)
        except KeyError:
            await message.reply("No results found.")
            return
        except IndexError:
            await message.reply("No streams found.")
            return

        providers = {
            "nfx": "Netflix",
            "prv": "Amazon Prime Video",
            "dnp": "Disney Plus",
            "wki": "Rakuten TV",
            "itu": "Apple iTunes",
            "atp": "Apple TV Plus",
            "hay": "hayu",
            "ply": "Google Play Movies",
            "skg": "Sky Go",
            "ntv": "Now TV",
            "msp": "Mediaset Play",
            "chi": "Chili",
            "mbi": "Mubi",
            "tvi": "Tim Vision",
            "inf": "Infinity",
            "rai": "Rai Play",
            "uci": "UCIcinemas",
            "gdc": "GuideDoc",
            "nxp": "Nexo Plus",
            "cru": "Crunchyroll",
            "ytr": "YouTube Premium",
            "msf": "Microsoft Store",
            "dpe": "Discovery Plus",
            "vvv": "VVVVID",
            "cts": "Curiosity Stream",
            "dsv": "DOCSVILLE",
            "sfx": "Spamflix",
            "ast": "Starz Play Amazon Channel",
            "plx": "Plex",
            "wow": "WOW Presents Plus",
            "mgl": "Magellan TV",
            "bhd": "BroadwayHD",
            "fmz": "Filmzie",
            "dkk": "Dekkoo",
            "trs": "True Story",
            "daf": "DocAlliance Films",
            "hoc": "Hoichoi",
            "amz": "Amazon Video",
            "stz": "Starz",
            "ptv": "Pluto TV",
            "eve": "Eventive",
            "atv": "ShortsTV Amazon Channel"
        }

        summary = ""
        summary += f"<b>{results['items'][0]['title']}</b>, "
        summary += f"<i>{results['items'][0]['object_type']}</i>, "
        summary += f"{results['items'][0]['original_release_year']}\n"

        id = results['items'][0]['id']
        imdb_id = 0
        imdb_url = ""
        infos = just_watch.get_title(title_id=id, content_type=results['items'][0]['object_type'])
        external_ids = infos['external_ids']
        for ids in external_ids:
            if ids['provider'] == 'imdb':
                imdb_id = ids['external_id']
                imdb_url = f'https://www.imdb.com/title/{imdb_id}/'
                rarbg_url = f'https://proxyrarbg.org/torrents.php?imdb={imdb_id}'
                break

        for k in results['items'][0]['scoring']:
            if k['provider_type'] == 'imdb:score':
                if imdb_url:
                    summary += f"{k['value']}/10 on <a href='{imdb_url}'>IMDb</a>\n<a href='{rarbg_url}'>⬇️ Search torrent</a>\n"
                else:
                    summary += f"{k['value']}/10 on IMDb\n<a href='{rarbg_url}'>⬇️ Search torrent</a>\n"

        message_jw += summary
        message_jw += "\n"

        for url, details in offers.items():
            types_list = ""
            for type_item in details['type']:
                types_list += type_item + ", "
            provider = providers.get(details['providers'], details['providers'])
            
            import requests
            message_jw += f"[{provider}]: <a href='{requests.utils.unquote(url)}'>{types_list[:-2]}</a>\n"

        await message.reply(message_jw, disable_web_page_preview=True)