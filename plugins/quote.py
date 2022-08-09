import os
import random
from io import BytesIO

import requests
from pyrogram import Client, filters
from wand.drawing import Drawing
from wand.font import Font
from wand.image import Image


# TODO: there has to be a proper way to not use four different Font objects
@Client.on_message(filters.command("quote", "!"))
async def quotes(client, message):
    if message.reply_to_message:
        if os.path.exists("Fonts"):
            try:
                r = requests.get(f"https://picsum.photos/800/500?{str(random.randrange(99999))}").content
                
                img = Image(file=BytesIO(r))
                img.brightness_contrast(brightness=-25)

                italic_black = Font("Fonts/Vollkorn-Italic.ttf", color="black")
                italic_white = Font("Fonts/Vollkorn-Italic.ttf", color="white")
                regular_black = Font("Fonts/Vollkorn-Regular.ttf", color="black")
                regular_white = Font("Fonts/Vollkorn-Regular.ttf", color="white")

                if message.reply_to_message.forward_sender_name:
                    author = message.reply_to_message.forward_sender_name
                elif message.reply_to_message.forward_from:
                    author = message.reply_to_message.forward_from.first_name
                elif message.reply_to_message.from_user.first_name:
                    author = message.reply_to_message.from_user.first_name
                else:
                    author = "Unknown"
                author = author.upper()

                if message.reply_to_message.text:
                    quote = message.reply_to_message.text
                elif message.reply_to_message.caption:
                    quote = message.reply_to_message.caption
                else:
                    quote = f"Lmao {message.from_user.first_name}, I just shitted my pants."

                with Drawing():
                    img.caption(
                        quote,
                        left=62, top=62, width=680, height=270,
                        font=italic_black,
                        gravity='west'
                    )

                    img.caption(
                        f'— {author}',
                        left=62, top=352, width=680, height=70,
                        font=regular_black,
                        gravity='west'
                    )

                    img.caption(
                        quote,
                        left=60, top=60, width=680, height=270,
                        font=italic_white,
                        gravity='west'
                    )

                    img.caption(
                        f'— {author}',
                        left=60, top=350, width=680, height=70,
                        font=regular_white,
                        gravity='west'
                    )
                
                output = BytesIO()
                img.save(file=output)

                await message.reply_photo(photo=output)
            except Exception as e:
                await message.reply(f"Error:\n<code>{e}</code>")
        else:
            os.mkdir("Fonts")
            await message.reply(text="Error: put the Vollkorn font in the Fonts folder to use this command.")
    else:
        await message.reply("Usage: `!quote` in reply to a message")
        