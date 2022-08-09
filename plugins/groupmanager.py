from configparser import ConfigParser

from pyrogram import Client, enums, filters
from pyrogram.errors.exceptions import bad_request_400


cfg = ConfigParser(interpolation=None)
cfg.read("config.ini")

ADMIN1_ID = int(cfg.get("admins", "admin1"))


@Client.on_message(filters.command("title", "!"))
async def set_title(client, message):
    if message.chat.type == enums.ChatType.GROUP or message.chat.type == enums.ChatType.SUPERGROUP or message.chat.type == enums.ChatType.CHANNEL:
        if len(message.command) == 1:
            if message.reply_to_message:
                if message.reply_to_message.text:
                    try:
                        await client.set_chat_title(chat_id=message.chat.id, title=message.reply_to_message.text)
                    except bad_request_400.ChatAdminRequired:
                        await message.reply("Error: I need to be an admin in this chat to set the title!")
                    except bad_request_400.ChatNotModified:
                        await message.reply("Error: you set the same title as before!")
                    except Exception as e:
                        print(e)
                        await message.reply("Error: could not set the title!")
                elif message.reply_to_message.caption:
                    try:
                        await client.set_chat_title(chat_id=message.chat.id, title=message.reply_to_message.caption)
                    except bad_request_400.ChatAdminRequired:
                        await message.reply("Error: I need to be an admin in this chat to set the title!")
                    except bad_request_400.ChatNotModified:
                        await message.reply("Error: you set the same title as before!")
                    except Exception as e:
                        print(e)
                        await message.reply("Error: could not set the title!")
                else:
                    await message.reply("Error: this message has no text or caption!")
            else:
                await message.reply("Usage: `!title <title>` or `!title` in reply to a message", parse_mode=enums.ParseMode.MARKDOWN)

        elif len(message.command) >= 2:
            try:
                await client.set_chat_title(chat_id=message.chat.id, title=message.text[5+1:])
            except bad_request_400.ChatAdminRequired:
                await message.reply("Error: I need to be an admin in this chat to set the title!")
            except bad_request_400.ChatNotModified:
                await message.reply("Error: you set the same title as before!")
            except Exception as e:
                print(e)
                await message.reply("Error: could not set the title!")
        
    else:
        await message.reply("Error: this command can be used in groups and channels only!")


@Client.on_message(filters.command("pin", "!"))
async def pin(client, message):
    if message.reply_to_message:
        try:
            await message.reply_to_message.pin(both_sides=True)
        except bad_request_400.ChatAdminRequired:
            await message.reply("Error: I need to be an admin in this chat to pin messages!")
        except Exception as e:
            print(e)
            await message.reply("Error: could not pin the message!")
    else:
        await message.reply("Usage: `!pin` in reply to a message", parse_mode=enums.ParseMode.MARKDOWN)
# TODO: add a way to disable notification and to pin for both sides (private)


# TODO: figure out how to get the most recent pinned message and unpin it
# TODO: add a way to unpin all the messages
# @Client.on_message(filters.command("unpin", "!"))
# async def unpin(client, message):
#     try:
#         await message.unpin()
#     except bad_request_400.ChatAdminRequired:
#         await message.reply("Error: I need to be an admin in this chat to unpin messages!")
#     except Exception as e:
#         print(e)
#         await message.reply("Error: could not unpin the message!")


@Client.on_message(filters.command("setpicture", "!"))
async def set_picture(client, message):
    if message.reply_to_message.photo:
        try:
            await client.set_chat_photo(chat_id=message.chat.id, photo=message.reply_to_message.photo.file_id)
        except bad_request_400.ChatAdminRequired:
            await message.reply("Error: I need to be an admin in this chat to set the picture!")
        except Exception as e:
            print(e)
            await message.reply("Error: could not set the picture!")
    else:
        await message.reply("Usage: `!setpicture` in reply to an image", parse_mode=enums.ParseMode.MARKDOWN)


@Client.on_message(filters.command("setabout", "!"))
async def set_about(client, message):
    if len(message.command) == 1:
        await message.reply("Usage: `!setabout <description>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        new_description = message.text[1+8+1:]

        if len(new_description) > 255:
            await message.reply(f"Error: the description is too long ({len(new_description)} characters). Max length is 255 characters.")
        else:
            try:
                this_chat = await client.get_chat(message.chat.id)

                if this_chat.description:
                    old_description = this_chat.description

                    await client.set_chat_description(chat_id=message.chat.id, description=new_description)
                    await message.reply(f"The description has been updated. In case you need it, here's the old description:\n`{old_description}`")
                else:
                    await client.set_chat_description(chat_id=message.chat.id, description=new_description)
                    await message.reply("The description has been set!")
            except bad_request_400.ChatAdminRequired:
                await message.reply("Error: I need to be an admin in this chat to set the description!")
            except bad_request_400.ChatAboutNotModified:
                await message.reply("Error: you set the same description as before!")
            except Exception as e:
                print(e)
                await message.reply("Error: could not set the description!")


@Client.on_message(filters.command("about", "!"))
async def about(client, message):
    this_chat = await client.get_chat(message.chat.id)

    if this_chat.description:
        await message.reply(f"The description of this chat is:\n`{this_chat.description}`")
    else:
        await message.reply("This chat has no description!")


@Client.on_message(filters.command("creategroup", "!"))
async def create_group(client, message):
    if len(message.command) == 1:
        await message.reply("Usage: `!creategroup <group title>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        if message.from_user.id == ADMIN1_ID:
            group_title = message.text[1+11+1:]

            try:
                group = await client.create_supergroup(title=group_title)
                await client.add_chat_members(group.id, message.from_user.id)
                group_link = await client.create_chat_invite_link(group.id)
                await message.reply(f'I created the group "[{group_title}]({group_link.invite_link})".')
            except Exception as e:
                await message.reply(f"Error:\n<code>{e}</code>")
        else:
            await message.reply("Sorry but you have to be the bot's admin to use this command!")


@Client.on_message(filters.command("deletegroup", "!"))
async def delete_group(client, message):
    if message.from_user.id == ADMIN1_ID:
        try:
            await client.delete_supergroup(message.chat.id)
        except bad_request_400.ChatAdminRequired:
            await message.reply("Error: I need to be the owner of this chat to delete it!")
        except Exception as e:
            await message.reply(f"Error:\n<code>{e}</code>")
    else:
        await message.reply("Sorry but you have to be the bot's admin to use this command!")
# TODO: there still are some errors to handle


@Client.on_message(filters.command(["del", "delete", "remove"], "!"))
async def delete_message(client, message):
    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
        except bad_request_400.ChatAdminRequired:
            await message.reply("Error: I need to be an admin in this chat to delete other people's messages!")
        except Exception as e:
            await message.reply(f"Error:\n<code>{e}</code>")
    else:
        await message.reply("Usage: `!delete` in reply to a message", parse_mode=enums.ParseMode.MARKDOWN)
# TODO: add a way to delete someone's last n messages
# TODO: add a way to delete all messages of a person