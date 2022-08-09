from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions import bad_request_400, forbidden_403


@Client.on_message(filters.command("join", "!"))
async def join_chat(client, message):
    if len(message.command) == 1 or len(message.command) == 3:
        await message.reply("Usage: `!join <chat or @handle>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        chat_to_join = message.command[1].replace("+", "joinchat/")
        try:
            chat_joined = await client.join_chat(chat_to_join)
            if chat_joined:
                await message.reply(f"Joined \"{chat_joined.title}\".")
        except bad_request_400.ChannelsTooMuch:
            await message.reply("Error: I joined in too many groups and channels!")
        except bad_request_400.UsernameNotOccupied:
            await message.reply("Error: the group or the channel doesn't exist!")
        except forbidden_403.ChannelPublicGroupNa:
            await message.reply("Error: group or channel not available!")
        except Exception as e:
            await message.reply(f"Error:\n<code>{e}</code>")