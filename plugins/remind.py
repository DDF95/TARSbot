import datetime

from pyrogram import Client, enums, filters
from pytimeparse import parse


@Client.on_message(filters.command("remind", "!"))
async def remind(client, message):
    if len(message.command) == 1 or len(message.command) == 2:
        await message.reply("Usage: `!remind <time> <message>`\n\nExamples:\n`!remind 1h30m Buy vegan milk`\n`!remind 1d Touch grass`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        time_from_now = message.command[1]
        text_to_remind = message.text[1+6+1 + len(time_from_now) + 1:]
        
        now = datetime.datetime.now()
        delay = parse(time_from_now)
        t = now + datetime.timedelta(seconds=delay)

        await client.send_message(message.chat.id, text_to_remind, schedule_date=t)

        await message.reply(f"Reminder saved, it will be sent on {t.strftime('%d/%m/%Y')} at {t.strftime('%H:%M:%S')}.")
# TODO: add a way to show all saved reminders
# TODO: add a way to delete reminders
# TODO: add an option to save the reminder as a reply to a message
