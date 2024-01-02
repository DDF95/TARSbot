import datetime

import pytz
from pyrogram import Client, enums, filters
from pyrogram.raw import functions
from pytimeparse import parse


def get_user_timezone():
    return pytz.timezone("Europe/Rome")


def parse_reminder_time(time_string):
    delay_seconds = parse(time_string)
    return datetime.timedelta(seconds=delay_seconds)


def get_current_time_in_user_timezone():
    now = datetime.datetime.now(pytz.utc)
    user_timezone = get_user_timezone()
    return now.astimezone(user_timezone)


def format_datetime(dt):
    return dt.strftime('%d/%m/%Y at %H:%M'), dt.strftime('%H:%M')


def format_reminder_list(reminders):
    formatted_list = []
    now = datetime.datetime.now(pytz.utc)
    for reminder in reminders:
        reminder_time = datetime.datetime.fromtimestamp(reminder.date, tz=pytz.utc)
        italy_time_str = format_datetime(reminder_time.astimezone(get_user_timezone()))[0]
        utc_time_str = format_datetime(reminder_time.astimezone(pytz.utc))[1]

        time_left = reminder_time - now
        time_left_str = format_time_left(time_left)

        formatted_list.append(
            f"\"{reminder.message}\"\n{italy_time_str} ({utc_time_str} UTC)\n-{time_left_str}"
        )
    return formatted_list


def format_time_left(time_left):
    seconds = int(time_left.total_seconds())
    time_left_str = ""

    if seconds < 0:
        time_left_str = "-"
        seconds = abs(seconds)

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60

    if days > 0:
        time_left_str += f"{days}d"
    if hours > 0:
        time_left_str += f"{hours}h"
    if minutes > 0:
        time_left_str += f"{minutes}m"

    return time_left_str


@Client.on_message(filters.command("remind", "!"))
async def remind(client, message):
    if len(message.command) == 1 or len(message.command) == 2:
        await message.reply(
            "Usage:\n`!remind <time> <message>`\nExamples:\n`!remind 1h30m Buy vegan milk`\n`!remind 1d Touch grass`\n\n" +
            "`!reminders` to see your saved reminders.\n" +
            "`!delreminder <number>` to delete a reminder.\n" +
            "`!delallreminders` to delete all reminders.",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
        return    

    if any(x in message.command[1] for x in [":", ".", ","]):
        # Handle time format HH:MM
        time = message.command[1]
        text_to_remind = message.text[1+6+1 + len(time) + 1:]

        if ":" in time:
            time_parts = time.split(":")
        elif "." in time:
            time_parts = time.split(".")
        elif "," in time:
            time_parts = time.split(",")
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        current_time = get_current_time_in_user_timezone()
        reminder_time = current_time.replace(hour=hours, minute=minutes)

    elif any(x in message.command[1] for x in ["/", "-"]) and any(x in message.command[2] for x in [":", ".", ","]):
        # Handle date format DD/MM/YYYY HH:MM
        date = message.command[1]
        time = message.command[2]
        text_to_remind = message.text[1+6+1 + len(date) + 1 + len(time) + 1:]

        if "/" in date:
            if len(date) == 5:
                date += f"/{get_current_time_in_user_timezone().year}"
            day, month, year = map(int, date.split("/"))
        elif "-" in date:
            if len(date) == 5:
                date += f"-{get_current_time_in_user_timezone().year}"
            day, month, year = map(int, date.split("-"))
        if ":" in time:
            time_parts = time.split(":")
        elif "." in time:
            time_parts = time.split(".")
        elif "," in time:
            time_parts = time.split(",")
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        current_time = get_current_time_in_user_timezone()
        reminder_time = current_time.replace(year=year, month=month, day=day, hour=hours, minute=minutes)

    elif any(x in message.command[1] for x in ["/", "-"]) and not any(x in message.command[2] for x in [":", ".", ","]):
        # Handle date format DD/MM/YYYY
        date = message.command[1]
        text_to_remind = message.text[1+6+1 + len(date) + 1:]

        if "/" in date:
            if len(date) == 5:
                date += f"/{get_current_time_in_user_timezone().year}"
            day, month, year = map(int, date.split("/"))
        elif "-" in date:
            if len(date) == 5:
                date += f"-{get_current_time_in_user_timezone().year}"
            day, month, year = map(int, date.split("-"))
        current_time = get_current_time_in_user_timezone()
        reminder_time = current_time.replace(year=year, month=month, day=day, hour=0, minute=0)

    else:
        # Handle delay format (e.g., 1h30m)
        delay_string = message.command[1]
        text_to_remind = message.text[1+6+1 + len(delay_string) + 1:]

        delay = parse_reminder_time(delay_string)
        current_time = get_current_time_in_user_timezone()
        reminder_time = current_time + delay

    await client.send_message(message.chat.id, text_to_remind, schedule_date=reminder_time)

    italy_time_str = format_datetime(reminder_time)[0]
    utc_time_str = format_datetime(reminder_time.astimezone(pytz.utc))[1]

    await message.reply(f"Reminder saved! It will be sent on {italy_time_str} ({utc_time_str} UTC).")


@Client.on_message(filters.command("reminders", "!"))
async def show_reminders(client, message):
    scheduled_messages = await client.invoke(
        functions.messages.GetScheduledHistory(
            peer=await client.resolve_peer(message.chat.id),
            hash=0
        )
    )
    reminders = scheduled_messages.messages
    if len(reminders) == 0:
        await message.reply("You have no saved reminders.")
    else:
        formatted_reminders = format_reminder_list(reminders)
        n = 1
        reminders_list = ""
        for reminder in reversed(formatted_reminders):
            reminders_list += f"{n}. {reminder}\n\n"
            n += 1
        await message.reply(f"{reminders_list}")


@Client.on_message(filters.command("delreminder", "!"))
async def delete_reminder(client, message):
    if len(message.command) != 2:
        await message.reply("Usage: `!delreminder <number>`")
        return

    reminder_number = int(message.command[1])

    scheduled_messages = await client.invoke(
        functions.messages.GetScheduledHistory(
            peer=await client.resolve_peer(message.chat.id),
            hash=0
        )
    )
    reminders = scheduled_messages.messages

    if reminder_number < 1 or reminder_number > len(reminders):
        await message.reply("Invalid reminder number.")
        return

    reminder_index = len(reminders) - reminder_number

    reminder_to_delete = reminders[reminder_index]

    await client.invoke(
        functions.messages.DeleteScheduledMessages(
            peer=await client.resolve_peer(message.chat.id),
            id=[reminder_to_delete.id]
        )
    )

    await message.reply("Reminder deleted successfully.")


@Client.on_message(filters.command("delallreminders", "!"))
async def delete_all_reminders(client, message):
    scheduled_messages = await client.invoke(
        functions.messages.GetScheduledHistory(
            peer=await client.resolve_peer(message.chat.id),
            hash=0
        )
    )
    reminders = scheduled_messages.messages
    if len(reminders) == 0:
        await message.reply("You have no saved reminders.")
    else:
        for reminder in reminders:
            await client.invoke(functions.messages.DeleteScheduledMessages(
                peer=await client.resolve_peer(message.chat.id),
                id=[reminder.id]
            ))
        await message.reply("All reminders have been deleted.")

# TODO: add an option to save the reminder as a reply to a message