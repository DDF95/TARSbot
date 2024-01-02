import tempfile

import deeppyer
from PIL import Image
from pyrogram import Client, filters


@Client.on_message(filters.command(["fry", "deepfry", "friggi"], "!"))
async def fry(client, message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply("Usage: `!fry` in reply to an image")
        return

    with tempfile.NamedTemporaryFile(suffix=".jpg") as temp:
        await client.download_media(message.reply_to_message, file_name=temp.name)

        image = Image.open(temp.name)
        fried_image = await deeppyer.deepfry(image, flares=False)

        fried_file = tempfile.NamedTemporaryFile(suffix=".jpg")
        fried_image.save(fried_file.name, "JPEG")

        await message.reply_photo(fried_file.name)

        fried_file.close()

    temp.close()

# TODO: add face detection