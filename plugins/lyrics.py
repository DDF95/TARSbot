from pyrogram import Client, filters, enums


# TODO: fix bugs (sometimes the lyrics are doubled)
# TODO: find another way to get the lyrics
# TODO: add async requests
@Client.on_message(filters.command("lyrics", "!"))
async def lyrics(client, message):
    # print("• lyrics command found")
    if len(message.command) == 1:
        # print("they don't know how to use this command")
        await message.reply("Usage: `!lyrics <author> - <song>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        # print("they know how to use this command")
        if "-" in message.text:
            # print("hyphen found")
            if " - " not in message.text:
                # print("hyphen was not surrounded by spaces")
                message.text = message.text.replace("-", " - ")

            try:
                # print("wait_message sent, all is ready for the first request")
                wait_message = await message.reply("Searching the lyrics. This may take a while...")

                import urllib.parse
                author = urllib.parse.quote(message.text[1+6+1:].split(" - ")[0])
                song = urllib.parse.quote(message.text[1+6+1:].split(" - ")[1])

                import requests
                # print("first request sent...")
                r = requests.get("https://api.lyrics.ovh/v1/" + author + "/" + song)
                # print("first request successful")

                if r.status_code == 200:
                    # print("status code 200, lyrics found")
                    await message.reply(r.json()['lyrics'])
                    await wait_message.delete()
                    # print("lyrics sent, wait_message deleted")
                else: # maybe the user inverted the order of author and song?
                    # print("status code = " + str(r.status_code) + ", trying the other order")

                    # print("second request sent...")
                    r2 = requests.get("https://api.lyrics.ovh/v1/" + song + "/" + author)
                    # print("second request successful")

                    if r2.status_code == 200:
                        # print("status code 200, lyrics found")
                        await message.reply(r2.json()['lyrics'])
                        await wait_message.delete()
                        # print("lyrics sent, wait_message deleted")
                    else:
                        # print("status code = " + str(r2.status_code) + ", no lyrics found")
                        await message.reply("No lyrics found!")
                        await wait_message.delete()
                        # print("no lyrics found, error message sent, wait_message deleted")
            except Exception as e:
                # print(e)
                await message.reply("Error! Please try again!")
                await wait_message.delete()
                # print("error message sent, wait_message deleted")
        else:
            await message.reply("You forgot to put the hyphen '-' between the name of the author and the name of the song!")