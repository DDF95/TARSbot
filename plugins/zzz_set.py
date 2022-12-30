import json
import os

from pyrogram import Client, enums, filters


reactions = ["👍", "👎", "❤️", "🔥", "🎉", "🤩", "😱", "😁", "😢", "💩", "🤮", "🤬", "🤯", "🤔", "🥰", "👏", "🙏", "👌", "🕊️", "🤡", "🥱", "🥴", "😍", "🐳", "❤️‍🔥", "🌚", "🌭", "💯", "🤣", "⚡️", "🍌", "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈", "😴", "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝", "✍️", "🤗", "🫡", "🎅", "🎄", "☃️"]


# Text
@Client.on_message(filters.command("set", "!"))
async def setter(client, message):
    if len(message.command) == 1 or len(message.command) == 2:
        await message.reply("Usage: `!set <trigger> <reply>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        if not os.path.isfile("sets.json"):
            with open("sets.json", "w") as f:
                json.dump({}, f)
        
        trigger = message.text.split(" ")[1]
        reply = message.text[1+3+1 + len(trigger) + 1:]

        if len(trigger) > 3:
            if "\"" in trigger or "\"" in reply:
                await message.reply("Pro tip: quotes are not needed in the trigger or reply!")

            with open("sets.json", 'r') as file:
                file_data = json.load(file)

            if not file_data.get(str(message.chat.id)):
                file_data[str(message.chat.id)] = {}

            file_data[str(message.chat.id)][trigger] = reply

            with open("sets.json", 'w') as file:
                json.dump(file_data, file, indent=4)

            await message.reply("Saved!")
        else:
            await message.reply("Error: the trigger must be at least 4 characters long!")


@Client.on_message(filters.command("unset", "!"))
async def unsetter(client, message):
    if len(message.command) == 1 or len(message.command) >= 3:
        await message.reply("Usage: `!unset <trigger>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        if not os.path.isfile("sets.json"):
            with open("sets.json", "w") as f:
                json.dump({}, f)
        
        trigger = message.text.split(" ")[1]

        with open("sets.json", 'r') as file:
            file_data = json.load(file)

        if file_data[str(message.chat.id)].get(trigger):
            del file_data[str(message.chat.id)][trigger]

            with open("sets.json", 'w') as file:
                json.dump(file_data, file, indent=4)

            await message.reply("Set deleted!")
        else:
            await message.reply("Set doesn't exist! Use `!set <trigger> <reply>` to create one.", parse_mode=enums.ParseMode.MARKDOWN)


@Client.on_message(filters.command(["get", "sets"], "!"))
async def sets_list(client, message):
    if not os.path.isfile("sets.json"):
        with open("sets.json", "w") as f:
            json.dump({}, f)

    with open("sets.json", 'r') as file:
        file_data = json.load(file)

    if file_data.get(str(message.chat.id)) and file_data[str(message.chat.id)].keys():
        set_list = ""
        for key, value in file_data[str(message.chat.id)].items():
            if len(value) > 20:
                set_list += f"{key} → \"{value[:20]}...\"\n"
            else:
                set_list += f"{key} → \"{value}\"\n"

        await message.reply(set_list)
    else:
        await message.reply("No sets found for this chat! Use `!set <trigger> <reply>` to create one.", parse_mode=enums.ParseMode.MARKDOWN)


@Client.on_message(filters.command("unsetall", "!"))
async def unset_all(client, message):
    if not os.path.isfile("sets.json"):
        with open("sets.json", "w") as f:
            json.dump({}, f)

    with open("sets.json", 'r') as file:
        file_data = json.load(file)

    if file_data.get(str(message.chat.id)):
        del file_data[str(message.chat.id)]

        with open("sets.json", 'w') as file:
            json.dump(file_data, file, indent=4)

        await message.reply("All sets deleted!")
    else:
        await message.reply("No sets found for this chat! Use `!set <trigger> <reply>` to create one.", parse_mode=enums.ParseMode.MARKDOWN)


# Reactions
@Client.on_message(filters.command(["setreact", "setreacc"], "!"))
async def set_reaction(client, message):
    if len(message.command) == 1 or len(message.command) == 2:
        await message.reply(f"Usage: `!setreact <trigger> <reaction emoji>`\n\nAvailable reaction emojis:\n{', '.join(reactions)}", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        if not os.path.isfile("reactions.json"):
            with open("reactions.json", "w") as f:
                json.dump({}, f)
        
        trigger = message.text.split(" ")[1]
        reaction = message.text[1+8+1 + len(trigger) + 1:]

        if "\"" in trigger or "\"" in reaction:
            await message.reply("Pro tip: quotes are not needed in the trigger or reaction!")
            
        if len(trigger) > 2:
            if any(x in reaction for x in reactions):
                with open("reactions.json", 'r') as file:
                    file_data = json.load(file)

                if not file_data.get(str(message.chat.id)):
                    file_data[str(message.chat.id)] = {}

                file_data[str(message.chat.id)][trigger] = reaction

                with open("reactions.json", 'w') as file:
                    json.dump(file_data, file, indent=4)

                await message.reply("Saved!")
            else:
                await message.reply("Invalid reaction emoji! Use one of the following:\n\n" + "".join(reactions))
        else:
            await message.reply("Error: the trigger must be at least 3 characters long!")


@Client.on_message(filters.command(["unsetreact", "unsetreacc"], "!"))
async def unset_reaction(client, message):
    if len(message.command) == 1 or len(message.command) >= 3:
        await message.reply("Usage: `!unsetreact <trigger>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        if not os.path.isfile("reactions.json"):
            with open("reactions.json", "w") as f:
                json.dump({}, f)
        
        trigger = message.text.split(" ")[1]

        with open("reactions.json", 'r') as file:
            file_data = json.load(file)

        if file_data[str(message.chat.id)].get(trigger):
            del file_data[str(message.chat.id)][trigger]

            with open("reactions.json", 'w') as file:
                json.dump(file_data, file, indent=4)

            await message.reply("Reaction deleted!")
        else:
            await message.reply("Reaction doesn't exist! Use `!setreact <trigger> <reaction emoji>` to create one.", parse_mode=enums.ParseMode.MARKDOWN)


@Client.on_message(filters.command(["reacts", "reaccs"], "!"))
async def reactions_list(client, message):
    if not os.path.isfile("reactions.json"):
        with open("reactions.json", "w") as f:
            json.dump({}, f)

    with open("reactions.json", 'r') as file:
        file_data = json.load(file)

    if file_data.get(str(message.chat.id)) and file_data[str(message.chat.id)].keys():
        reaction_list = ""
        for key, value in file_data[str(message.chat.id)].items():
            reaction_list += f"{key} → {value}\n"

        await message.reply(reaction_list)
    else:
        await message.reply("No reactions found for this chat! Use `!setreact <trigger> <reaction emoji>` to create one.", parse_mode=enums.ParseMode.MARKDOWN)


# Media
@Client.on_message(filters.command("setmedia", "!"))
async def set_media(client, message):
    if len(message.command) == 1 or len(message.command) >= 3 or not message.reply_to_message:
        await message.reply("Usage: `!setmedia <trigger>` in reply to a message", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        if not os.path.isfile("media.json"):
            with open("media.json", "w") as f:
                json.dump({}, f)
        
        trigger = message.text.split(" ")[1]

        if len(trigger) > 3:
            media_link = message.reply_to_message.link
            media_message_id = media_link.split("/")[5]
            media_type = message.reply_to_message.media

            with open("media.json", 'r') as file:
                file_data = json.load(file)

            if not file_data.get(str(message.chat.id)):
                file_data[str(message.chat.id)] = {}

            if media_type == enums.MessageMediaType.PHOTO:
                file_data[str(message.chat.id)][trigger] = f"photo {media_message_id}"
            elif media_type == enums.MessageMediaType.VIDEO:
                file_data[str(message.chat.id)][trigger] = f"video {media_message_id}"
            elif media_type == enums.MessageMediaType.AUDIO:
                file_data[str(message.chat.id)][trigger] = f"audio {media_message_id}"
            elif media_type == enums.MessageMediaType.DOCUMENT:
                file_data[str(message.chat.id)][trigger] = f"document {media_message_id}"
            elif media_type == enums.MessageMediaType.STICKER:
                file_data[str(message.chat.id)][trigger] = f"sticker {media_message_id}"
            elif media_type == enums.MessageMediaType.VOICE:
                file_data[str(message.chat.id)][trigger] = f"voice {media_message_id}"
            elif media_type == enums.MessageMediaType.VIDEO_NOTE:
                file_data[str(message.chat.id)][trigger] = f"video_note {media_message_id}"
            elif media_type == enums.MessageMediaType.ANIMATION:
                file_data[str(message.chat.id)][trigger] = f"animation {media_message_id}"
            else:
                await message.reply("Invalid media type!")
            
            with open("media.json", 'w') as file:
                json.dump(file_data, file, indent=4)

            await message.reply("Saved!")
        else:
            await message.reply("Error: the trigger must be at least 4 characters long!")


@Client.on_message(filters.command("unsetmedia", "!"))
async def unset_media(client, message):
    if len(message.command) == 1 or len(message.command) >= 3:
        await message.reply("Usage: `!unsetmedia <trigger>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        if not os.path.isfile("media.json"):
            with open("media.json", "w") as f:
                json.dump({}, f)
        
        trigger = message.text.split(" ")[1]

        with open("media.json", 'r') as file:
            file_data = json.load(file)

        if file_data[str(message.chat.id)].get(trigger):
            del file_data[str(message.chat.id)][trigger]

            with open("media.json", 'w') as file:
                json.dump(file_data, file, indent=4)

            await message.reply("Media deleted!")
        else:
            await message.reply("Media doesn't exist! Use `!setmedia <trigger>` to create one.", parse_mode=enums.ParseMode.MARKDOWN)


@Client.on_message(filters.command("media", "!"))
async def media_list(client, message):
    if not os.path.isfile("media.json"):
        with open("media.json", "w") as f:
            json.dump({}, f)

    with open("media.json", 'r') as file:
        file_data = json.load(file)

    if file_data.get(str(message.chat.id)) and file_data[str(message.chat.id)].keys():
        media_list = ""
        for key, value in file_data[str(message.chat.id)].items():
            link = f"https://t.me/c/{message.chat.id}/{value.split()[1]}"
            link = link.replace("-100", "")

            if message.chat.type == enums.ChatType.SUPERGROUP or message.chat.type == enums.ChatType.CHANNEL or message.chat.type == enums.ChatType.GROUP:
                media_list += f"{key} → [{value.split()[0]}]({link})\n"
            else:
                media_list += f"{key} → {value.split()[0]}\n"

        await message.reply(media_list)
    else:
        await message.reply("No media found for this chat! Use `!setmedia <trigger>` to create one.", parse_mode=enums.ParseMode.MARKDOWN)


@Client.on_message(filters.text)
async def getter(client, message):
    word_list = message.text.split(" ")

    # Text
    try:
        with open("sets.json", 'r') as sets_file:
            sets_data = json.load(sets_file)
        
        if sets_data.get(str(message.chat.id)):
            for key, value in sets_data[str(message.chat.id)].items():
                if key in word_list:
                    await message.reply(value)
                    break
    except:
        pass
    # TODO: maybe only check for the first word of the message, not for all words in the message. Right now it could be spammy if you use a lot of sets.

    # Reactions
    try:
        with open("reactions.json", 'r') as reacts_file:
            reacts_data = json.load(reacts_file)
        
        if reacts_data.get(str(message.chat.id)):
            for key, value in reacts_data[str(message.chat.id)].items():
                if key in word_list:
                    await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji=value)
                    break

    # Media
    try:
        with open("media.json", 'r') as media_file:
            media_data = json.load(media_file)

        if media_data.get(str(message.chat.id)):
            for key, value in media_data[str(message.chat.id)].items():
                if key in word_list:
                    media_message_id = media_data[str(message.chat.id)].get(key).split()[1]
                    media_message = await client.get_messages(chat_id=message.chat.id, message_ids=int(media_message_id))

                    if value.split()[0] == "photo":
                        await message.reply_photo(photo=media_message.photo.file_id)
                    elif value.split()[0] == "video":
                        await message.reply_video(video=media_message.video.file_id)
                    elif value.split()[0] == "audio":
                        await message.reply_audio(audio=media_message.audio.file_id)
                    elif value.split()[0] == "document":
                        await message.reply_document(document=media_message.document.file_id)
                    elif value.split()[0] == "sticker":
                        await message.reply_sticker(sticker=media_message.sticker.file_id)
                    elif value.split()[0] == "voice":
                        await message.reply_voice(voice=media_message.voice.file_id)
                    elif value.split()[0] == "video_note":
                        await message.reply_video_note(video_note=media_message.video_note.file_id)
                    elif value.split()[0] == "animation":
                        await message.reply_animation(animation=media_message.animation.file_id)
                    else:
                        pass
                    break
    except:
        pass
