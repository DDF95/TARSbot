import random
from configparser import ConfigParser

import openai
from pyrogram import Client, enums, filters


@Client.on_message(filters.command("askdavinci", "!"))
async def askdavinci(client, message):
    cfg = ConfigParser(interpolation=None)
    cfg.read("config.ini")

    openai_values = cfg.items("openai")

    RANDOM_API_KEY = random.choice(list(openai_values))[1]

    premium_users = [int(cfg["admins"]["admin1"]), 8093420, 87526036, 98188090, 22795657, 19778723, 32410719, 1753509701, 102889983, 173120171, 474799562, 1735623047, 104117139, 149844390, 1155237714, 578482472, 481519570, 95357956, 573963993, 1478812362, 319719099, 178173240, 518619034, 156346143, 47107732, 378844752, 5448250840, 142908761, 361368699, 212531450, 327414309, 1310374399, 1993079742, 228034043]
    
    if message.from_user.id in premium_users:
        try:
            openai.api_key = RANDOM_API_KEY
            response = openai.Completion.create(
                engine="text-davinci-001",
                prompt=message.text[1+10+1:],
                temperature=0.9,
                max_tokens=200,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6
            )
        
            await message.reply(text=f"**{message.text[1+10+1:]}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
        except Exception as e:
            await message.reply(f"{e}")
            await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")
    else:
        await message.reply("Sorry, you're not premium. Register on openai.com and give the `API key` to @diddieffe. It's free!\n\nAlternatively, use `!askcurie`. It's less intelligent but it gets the job done.")


@Client.on_message(filters.command("askcurie", "!"))
async def askcurie(client, message):
    cfg = ConfigParser(interpolation=None)
    cfg.read("config.ini")

    openai_values = cfg.items("openai")

    RANDOM_API_KEY = random.choice(list(openai_values))[1]

    try:
        openai.api_key = RANDOM_API_KEY
        response = openai.Completion.create(
            engine="text-curie-001",
            prompt=message.text[1+8+1:],
            temperature=0.9,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
    
        await message.reply(text=f"**{message.text[1+8+1:]}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"{e}")
        await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")


@Client.on_message(filters.command("askbabbage", "!"))
async def askbabbage(client, message):
    cfg = ConfigParser(interpolation=None)
    cfg.read("config.ini")

    openai_values = cfg.items("openai")

    RANDOM_API_KEY = random.choice(list(openai_values))[1]

    try:
        openai.api_key = RANDOM_API_KEY
        response = openai.Completion.create(
            engine="text-babbage-001",
            prompt=message.text[1+10+1:],
            temperature=0.9,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
    
        await message.reply(text=f"**{message.text[1+10+1:]}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"{e}")
        await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")


@Client.on_message(filters.command("askada", "!"))
async def askada(client, message):
    cfg = ConfigParser(interpolation=None)
    cfg.read("config.ini")

    openai_values = cfg.items("openai")

    RANDOM_API_KEY = random.choice(list(openai_values))[1]

    try:
        openai.api_key = RANDOM_API_KEY
        response = openai.Completion.create(
            engine="text-ada-001",
            prompt=message.text[1+6+1:],
            temperature=0.9,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
    
        await message.reply(text=f"**{message.text[1+6+1:]}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"{e}")
        await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")


@Client.on_message(filters.command("ask", "!"))
async def ask_help(client, message):
    if message.from_user.id == 5448250840:
        cfg = ConfigParser(interpolation=None)
        cfg.read("config.ini")

        openai_values = cfg.items("openai")

        RANDOM_API_KEY = random.choice(list(openai_values))[1]

        try:
            openai.api_key = RANDOM_API_KEY
            response = openai.Completion.create(
                engine="text-curie-001",
                prompt=message.text[1+3+1:],
                temperature=0.9,
                max_tokens=200,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6
            )
        
            await message.reply(text=f"**{message.text[1+3+1:]}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
        except Exception as e:
            await message.reply(f"{e}")
            await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")

    else:
        await message.reply(
            text="Usage:\n"
            "• `!askdavinci <text>` - the smartest engine (requires premium, infos down below)\n"
            "• `!askcurie <text>`\n"
            "• `!askbabbage <text>`\n"
            "• `!askada <text>` - the least intelligent engine\n\n"
            "**Premium (actually it's FREE!):**\n"
            "The DaVinci engine requires more computational power and is more intelligent than the others. It's free to use, but you need to register an account on openai.com and give the `API key` to @diddieffe. This won't cost you anything, you don't even need credit cards or anything like that.",
            parse_mode=enums.ParseMode.MARKDOWN,
        )


@Client.on_message(filters.command("continue", "!"))
async def continue_text(client, message):
    if len(message.command) == 1 or len(message.command) >= 3 and not message.reply_to_message.text:
        await message.reply(
            text="Usage: `!continue <engine>` in reply to a text message\n\n"
            "Available engines:\n\n"
            "• `davinci` (requires premium, use `!ask` to learn more\n"
            "• `curie`\n"
            "• `babbage`\n"
            "• `ada`",
            parse_mode=enums.ParseMode.MARKDOWN
        )

    else:
        cfg = ConfigParser(interpolation=None)
        cfg.read("config.ini")

        openai_values = cfg.items("openai")

        RANDOM_API_KEY = random.choice(list(openai_values))[1]

        if message.command[1] == "davinci":
            premium_users = [int(cfg["admins"]["admin1"]), 8093420, 87526036, 98188090, 22795657, 19778723, 32410719, 1753509701, 102889983, 173120171, 474799562, 1735623047, 104117139, 149844390, 1155237714, 578482472, 481519570, 95357956, 573963993, 1478812362, 319719099, 178173240, 518619034, 156346143, 47107732, 378844752, 5448250840, 142908761, 361368699, 212531450, 327414309, 1310374399, 1993079742, 228034043]
            
            if message.from_user.id in premium_users:
                try:
                    openai.api_key = RANDOM_API_KEY
                    response = openai.Completion.create(
                        engine="text-davinci-001",
                        prompt=message.reply_to_message.text,
                        temperature=0.9,
                        max_tokens=200,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0.6
                    )
                
                    await message.reply(text=f"**{message.reply_to_message.text}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
                except Exception as e:
                    await message.reply(f"{e}")
                    await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")

        elif message.command[1] == "curie":
            try:
                openai.api_key = RANDOM_API_KEY
                response = openai.Completion.create(
                    engine="text-curie-001",
                    prompt=message.reply_to_message.text,
                    temperature=0.9,
                    max_tokens=200,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0.6
                )
            
                await message.reply(text=f"**{message.reply_to_message.text}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
            except Exception as e:
                await message.reply(f"{e}")
                await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")

        elif message.command[1] == "babbage":
            try:
                openai.api_key = RANDOM_API_KEY
                response = openai.Completion.create(
                    engine="text-babbage-001",
                    prompt=message.reply_to_message.text,
                    temperature=0.9,
                    max_tokens=200,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0.6
                )
            
                await message.reply(text=f"**{message.reply_to_message.text}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
            except Exception as e:
                await message.reply(f"{e}")
                await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")
            
        elif message.command[1] == "ada":
            try:
                openai.api_key = RANDOM_API_KEY
                response = openai.Completion.create(
                    engine="text-ada-001",
                    prompt=message.reply_to_message.text,
                    temperature=0.9,
                    max_tokens=200,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0.6
                )
            
                await message.reply(text=f"**{message.reply_to_message.text}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
            except Exception as e:
                await message.reply(f"{e}")
                await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")
        
        else:
            await message.reply(
                text="Usage: `!continue <engine>` in reply to a text message\n\n"
                "Available engines:\n\n"
                "• `davinci` (requires premium, use `!ask` to learn more\n"
                "• `curie`\n"
                "• `babbage`\n"
                "• `ada`",
                parse_mode=enums.ParseMode.MARKDOWN
            )


@Client.on_message(filters.command("face", "!"))
async def face(client, message):
    try:
        import requests
        from io import BytesIO
        face_img = requests.get("https://thispersondoesnotexist.com/image").content
        
        identity_data = requests.get("https://api.namefake.com/")
        name = identity_data.json()['name']
        age = str(random.randrange(100))

        await message.reply_photo(photo=BytesIO(face_img), caption=f"Name: {name}\nAge: {age}")

    except Exception as e:
        await message.reply(f"Error: `{e}`")


@Client.on_message(filters.command("faceai", "!"))
async def faceai(client, message):
    try:
        import requests
        from io import BytesIO
        face_img = requests.get("https://thispersondoesnotexist.com/image").content
        
        identity_data = requests.get("https://api.namefake.com/")
        name = identity_data.json()['name']
        age = str(random.randrange(100))

        cfg = ConfigParser(interpolation=None)
        cfg.read("config.ini")

        openai_values = cfg.items("openai")

        RANDOM_API_KEY = random.choice(list(openai_values))[1]

        openai.api_key = RANDOM_API_KEY
        response = openai.Completion.create(
            engine="text-curie-001",
            prompt=f"Name: {name}\nAge: {age}\nWeird biography:",
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        await message.reply_photo(photo=BytesIO(face_img), caption=f"<b>Name:</b> {name}\n<b>Age:</b> {age}\n\n{response['choices'][0]['text'].strip()}")
    
    except Exception as e:
        await message.reply(f"{e}")
        await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")
    RANDOM_API_KEY = random.choice(list(openai_values))[1]

    try:
        openai.api_key = RANDOM_API_KEY
        response = openai.Completion.create(
            engine="text-curie-001",
            prompt=message.text[1+8+1:],
            temperature=0.9,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
    
        await message.reply(text=f"**{message.text[1+8+1:]}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"{e}")
        await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")


@Client.on_message(filters.command("askbabbage", "!"))
async def askbabbage(client, message):
    cfg = ConfigParser(interpolation=None)
    cfg.read("config.ini")

    openai_values = cfg.items("openai")

    RANDOM_API_KEY = random.choice(list(openai_values))[1]

    try:
        openai.api_key = RANDOM_API_KEY
        response = openai.Completion.create(
            engine="text-babbage-001",
            prompt=message.text[1+10+1:],
            temperature=0.9,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
    
        await message.reply(text=f"**{message.text[1+10+1:]}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"{e}")
        await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")


@Client.on_message(filters.command("askada", "!"))
async def askada(client, message):
    cfg = ConfigParser(interpolation=None)
    cfg.read("config.ini")

    openai_values = cfg.items("openai")

    RANDOM_API_KEY = random.choice(list(openai_values))[1]

    try:
        openai.api_key = RANDOM_API_KEY
        response = openai.Completion.create(
            engine="text-ada-001",
            prompt=message.text[1+6+1:],
            temperature=0.9,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
    
        await message.reply(text=f"**{message.text[1+6+1:]}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"{e}")
        await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")


@Client.on_message(filters.command("ask", "!"))
async def ask_help(client, message):
    await message.reply(
        text="Usage:\n"
        "• `!askdavinci <text>` - the smartest engine (requires premium, infos down below)\n"
        "• `!askcurie <text>`\n"
        "• `!askbabbage <text>`\n"
        "• `!askada <text>` - the least intelligent engine\n\n"
        "**Premium (actually it's FREE!):**\n"
        "The DaVinci engine requires more computational power and is more intelligent than the others. It's free to use, but you need to register an account on openai.com and give the `API key` to @diddieffe. This won't cost you anything, you don't even need credit cards or anything like that.",
        parse_mode=enums.ParseMode.MARKDOWN,
    )


@Client.on_message(filters.command("continue", "!"))
async def continue_text(client, message):
    if len(message.command) == 1 or len(message.command) >= 3 and not message.reply_to_message.text:
        await message.reply(
            text="Usage: `!continue <engine>` in reply to a text message\n\n"
            "Available engines:\n\n"
            "• `davinci` (requires premium, use `!ask` to learn more\n"
            "• `curie`\n"
            "• `babbage`\n"
            "• `ada`",
            parse_mode=enums.ParseMode.MARKDOWN
        )

    else:
        cfg = ConfigParser(interpolation=None)
        cfg.read("config.ini")

        openai_values = cfg.items("openai")

        RANDOM_API_KEY = random.choice(list(openai_values))[1]

        if message.command[1] == "davinci":
            premium_users = [int(cfg["admins"]["admin1"]), 8093420, 87526036, 98188090, 22795657, 19778723, 32410719, 1753509701, 102889983, 173120171, 474799562, 1735623047, 104117139, 149844390, 1155237714, 578482472, 481519570, 95357956, 573963993, 1478812362, 319719099, 178173240, 518619034, 156346143, 47107732, 378844752, 5448250840, 142908761, 361368699]
            
            if message.from_user.id in premium_users:
                try:
                    openai.api_key = RANDOM_API_KEY
import random
from configparser import ConfigParser

import openai
from pyrogram import Client, enums, filters


@Client.on_message(filters.command("askdavinci", "!"))
async def askdavinci(client, message):
    cfg = ConfigParser(interpolation=None)
    cfg.read("config.ini")

    openai_values = cfg.items("openai")

    RANDOM_API_KEY = random.choice(list(openai_values))[1]

    premium_users = [int(cfg["admins"]["admin1"]), 8093420, 87526036, 98188090, 22795657, 19778723, 32410719, 1753509701, 102889983, 173120171, 474799562, 1735623047, 104117139, 149844390, 1155237714, 578482472, 481519570, 95357956, 573963993, 1478812362, 319719099, 178173240, 518619034, 156346143, 47107732, 378844752, 5448250840, 142908761, 361368699, 212531450, 327414309, 1310374399, 1993079742, 228034043]
    
    if message.from_user.id in premium_users:
        try:
            openai.api_key = RANDOM_API_KEY
            response = openai.Completion.create(
                engine="text-davinci-001",
                prompt=message.text[1+10+1:],
                temperature=0.9,
                max_tokens=200,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6
            )
        
            await message.reply(text=f"**{message.text[1+10+1:]}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
        except Exception as e:
            await message.reply(f"{e}")
            await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")
    else:
        await message.reply("Sorry, you're not premium. Register on openai.com and give the `API key` to @diddieffe. It's free!\n\nAlternatively, use `!askcurie`. It's less intelligent but it gets the job done.")


@Client.on_message(filters.command("askcurie", "!"))
async def askcurie(client, message):
    cfg = ConfigParser(interpolation=None)
    cfg.read("config.ini")

    openai_values = cfg.items("openai")

    RANDOM_API_KEY = random.choice(list(openai_values))[1]

    try:
        openai.api_key = RANDOM_API_KEY
        response = openai.Completion.create(
            engine="text-curie-001",
            prompt=message.text[1+8+1:],
            temperature=0.9,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
    
        await message.reply(text=f"**{message.text[1+8+1:]}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"{e}")
        await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")


@Client.on_message(filters.command("askbabbage", "!"))
async def askbabbage(client, message):
    cfg = ConfigParser(interpolation=None)
    cfg.read("config.ini")

    openai_values = cfg.items("openai")

    RANDOM_API_KEY = random.choice(list(openai_values))[1]

    try:
        openai.api_key = RANDOM_API_KEY
        response = openai.Completion.create(
            engine="text-babbage-001",
            prompt=message.text[1+10+1:],
            temperature=0.9,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
    
        await message.reply(text=f"**{message.text[1+10+1:]}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"{e}")
        await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")


@Client.on_message(filters.command("askada", "!"))
async def askada(client, message):
    cfg = ConfigParser(interpolation=None)
    cfg.read("config.ini")

    openai_values = cfg.items("openai")

    RANDOM_API_KEY = random.choice(list(openai_values))[1]

    try:
        openai.api_key = RANDOM_API_KEY
        response = openai.Completion.create(
            engine="text-ada-001",
            prompt=message.text[1+6+1:],
            temperature=0.9,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
    
        await message.reply(text=f"**{message.text[1+6+1:]}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"{e}")
        await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")


@Client.on_message(filters.command("ask", "!"))
async def ask_help(client, message):
    await message.reply(
        text="Usage:\n"
        "• `!askdavinci <text>` - the smartest engine (requires premium, infos down below)\n"
        "• `!askcurie <text>`\n"
        "• `!askbabbage <text>`\n"
        "• `!askada <text>` - the least intelligent engine\n\n"
        "**Premium (actually it's FREE!):**\n"
        "The DaVinci engine requires more computational power and is more intelligent than the others. It's free to use, but you need to register an account on openai.com and give the `API key` to @diddieffe. This won't cost you anything, you don't even need credit cards or anything like that.",
        parse_mode=enums.ParseMode.MARKDOWN,
    )


@Client.on_message(filters.command("continue", "!"))
async def continue_text(client, message):
    if len(message.command) == 1 or len(message.command) >= 3 and not message.reply_to_message.text:
        await message.reply(
            text="Usage: `!continue <engine>` in reply to a text message\n\n"
            "Available engines:\n\n"
            "• `davinci` (requires premium, use `!ask` to learn more\n"
            "• `curie`\n"
            "• `babbage`\n"
            "• `ada`",
            parse_mode=enums.ParseMode.MARKDOWN
        )

    else:
        cfg = ConfigParser(interpolation=None)
        cfg.read("config.ini")

        openai_values = cfg.items("openai")

        RANDOM_API_KEY = random.choice(list(openai_values))[1]

        if message.command[1] == "davinci":
            premium_users = [int(cfg["admins"]["admin1"]), 8093420, 87526036, 98188090, 22795657, 19778723, 32410719, 1753509701, 102889983, 173120171, 474799562, 1735623047, 104117139, 149844390, 1155237714, 578482472, 481519570, 95357956, 573963993, 1478812362, 319719099, 178173240, 518619034, 156346143, 47107732, 378844752, 5448250840, 142908761, 361368699, 212531450, 327414309, 1310374399, 1993079742, 228034043]
            
            if message.from_user.id in premium_users:
                try:
                    openai.api_key = RANDOM_API_KEY
                    response = openai.Completion.create(
                        engine="text-davinci-001",
                        prompt=message.reply_to_message.text,
                        temperature=0.9,
                        max_tokens=200,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0.6
                    )
                
                    await message.reply(text=f"**{message.reply_to_message.text}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
                except Exception as e:
                    await message.reply(f"{e}")
                    await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")

        elif message.command[1] == "curie":
            try:
                openai.api_key = RANDOM_API_KEY
                response = openai.Completion.create(
                    engine="text-curie-001",
                    prompt=message.reply_to_message.text,
                    temperature=0.9,
                    max_tokens=200,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0.6
                )
            
                await message.reply(text=f"**{message.reply_to_message.text}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
            except Exception as e:
                await message.reply(f"{e}")
                await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")

        elif message.command[1] == "babbage":
            try:
                openai.api_key = RANDOM_API_KEY
                response = openai.Completion.create(
                    engine="text-babbage-001",
                    prompt=message.reply_to_message.text,
                    temperature=0.9,
                    max_tokens=200,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0.6
                )
            
                await message.reply(text=f"**{message.reply_to_message.text}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
            except Exception as e:
                await message.reply(f"{e}")
                await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")
            
        elif message.command[1] == "ada":
            try:
                openai.api_key = RANDOM_API_KEY
                response = openai.Completion.create(
                    engine="text-ada-001",
                    prompt=message.reply_to_message.text,
                    temperature=0.9,
                    max_tokens=200,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0.6
                )
            
                await message.reply(text=f"**{message.reply_to_message.text}**{response['choices'][0]['text']}", parse_mode=enums.ParseMode.MARKDOWN)
            except Exception as e:
                await message.reply(f"{e}")
                await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")
        
        else:
            await message.reply(
                text="Usage: `!continue <engine>` in reply to a text message\n\n"
                "Available engines:\n\n"
                "• `davinci` (requires premium, use `!ask` to learn more\n"
                "• `curie`\n"
                "• `babbage`\n"
                "• `ada`",
                parse_mode=enums.ParseMode.MARKDOWN
            )


@Client.on_message(filters.command("face", "!"))
async def face(client, message):
    try:
        import requests
        from io import BytesIO
        face_img = requests.get("https://thispersondoesnotexist.com/image").content
        
        identity_data = requests.get("https://api.namefake.com/")
        name = identity_data.json()['name']
        age = str(random.randrange(100))

        await message.reply_photo(photo=BytesIO(face_img), caption=f"Name: {name}\nAge: {age}")

    except Exception as e:
        await message.reply(f"Error: `{e}`")


@Client.on_message(filters.command("faceai", "!"))
async def faceai(client, message):
    try:
        import requests
        from io import BytesIO
        face_img = requests.get("https://thispersondoesnotexist.com/image").content
        
        identity_data = requests.get("https://api.namefake.com/")
        name = identity_data.json()['name']
        age = str(random.randrange(100))

        cfg = ConfigParser(interpolation=None)
        cfg.read("config.ini")

        openai_values = cfg.items("openai")

        RANDOM_API_KEY = random.choice(list(openai_values))[1]

        openai.api_key = RANDOM_API_KEY
        response = openai.Completion.create(
            engine="text-curie-001",
            prompt=f"Name: {name}\nAge: {age}\nWeird biography:",
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        await message.reply_photo(photo=BytesIO(face_img), caption=f"<b>Name:</b> {name}\n<b>Age:</b> {age}\n\n{response['choices'][0]['text'].strip()}")
    
    except Exception as e:
        await message.reply(f"{e}")
        await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {RANDOM_API_KEY[-5:]}")
