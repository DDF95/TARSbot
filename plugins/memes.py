import random
from configparser import ConfigParser
import aiohttp
from pyrogram import Client, enums, filters
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import json
import spacy
from typing import List


nlp = spacy.load("it_core_news_sm")


async def openai_response(engine, prompt, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, client, message):
    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)

        cfg = ConfigParser(interpolation=None)
        cfg.read("config.ini")
        openai_apikeys = cfg.items("openai_apikeys")
        api_key = random.choice(list(openai_apikeys))[1]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://api.openai.com/v1/engines/{engine}/completions", headers=headers, json=payload) as resp:
                resp_json = await resp.json()
                return resp_json
    except Exception as e:
        await message.reply(f"Error: {e}")
        await client.send_message(chat_id=int(cfg["admins"]["admin1"]), text=f"Broken OpenAI API key: {api_key[-5:]}")


async def fetch_random_image_url(word):
    try:
        with open("photos.json", "r") as json_file:
            photos_data = json.load(json_file)

        if word.lower() in photos_data:
            image_urls = photos_data[word.lower()]
            return f"https://jwlss.pw/markov-news/{random.choice(image_urls)}"
        else:
            all_image_urls = [f"https://jwlss.pw/markov-news/{url}" for urls in photos_data.values() for url in urls]
            return random.choice(all_image_urls)
    except Exception as e:
        raise e
    

def spacy_tokenizer(sentence: str) -> List[str]:
    tokens = nlp(sentence)
    tokens = [token.lemma_.lower() for token in tokens if not token.is_punct and not token.is_stop]
    return tokens


def format_sentence(sentence, max_width, font, draw):
    words = sentence.split()
    lines = []
    line = []
    line_width = 0

    for word in words:
        word_width = draw.textsize(word, font=font)[0]

        if line_width + word_width <= max_width:
            line.append(word)
            line_width += word_width + draw.textsize(' ', font=font)[0]
        else:
            lines.append(' '.join(line))
            line = [word]
            line_width = word_width + draw.textsize(' ', font=font)[0]

    lines.append(' '.join(line))
    return '\n'.join(lines)


async def create_meme_image(session, top_text, bottom_text, image_url):
    try:
        async with session.get(image_url) as response:
            image_bytes = await response.read()

        img = Image.open(BytesIO(image_bytes))
        draw = ImageDraw.Draw(img)

        font_path = 'Fonts/impact.ttf'
        fnt = ImageFont.truetype(font_path, 40)

        max_width, max_height = img.size
        top_text = format_sentence(top_text, max_width - 20, fnt, draw)
        bottom_text = format_sentence(bottom_text, max_width - 20, fnt, draw)

        top_text_width, top_text_height = draw.textsize(top_text, font=fnt)
        top_text_position = ((max_width - top_text_width) // 2, 20)

        bottom_text_width, bottom_text_height = draw.textsize(bottom_text, font=fnt)
        bottom_text_position = ((max_width - bottom_text_width) // 2, max_height - 20 - bottom_text_height)

        draw.text(top_text_position, top_text, font=fnt, fill="white", stroke_width=2, stroke_fill="black", align="center")

        draw.text(bottom_text_position, bottom_text, font=fnt, fill="white", stroke_width=2, stroke_fill="black", align="center")

        meme_bytes_io = BytesIO()
        img.save(meme_bytes_io, format='PNG')
        meme_bytes = meme_bytes_io.getvalue()

        return meme_bytes
    except Exception as e:
        raise e


@Client.on_message(filters.command("meme", "!"))
async def create_meme(client, message):
    input_text = ""
    if message.reply_to_message:
        if message.text == "!meme":
            input_text = str(message.reply_to_message.text)
        else:
            input_text = message.text[1 + 4 + 1:]
    else:
        input_text = message.text[1 + 4 + 1:]

    if message.text == "!meme" and not message.reply_to_message:
        await message.reply(text="Usage: `!meme <text>`", parse_mode=enums.ParseMode.MARKDOWN)
        return
    
    prompt = f"Dato un argomento, crea un meme (in italiano) che sia inusuale e scandaloso. Dovrai scegliere top e bottom text. Usa questo formato per l'output:\ntop_text: \"top text\"\nbottom_text: \"bottom text\"\n\nArgomento: {input_text}.\n\ntop_text: \""
    response = await openai_response("text-davinci-003", prompt, 0.9, 300, 1, 0, 0.6, client, message)
    
    top_text, bottom_text = extract_meme_text(f"top_text: \"{response['choices'][0]['text']}".strip())

    input_tokens = spacy_tokenizer(input_text)
    print(input_tokens)

    random_word = random.choice(input_tokens)

    image_url = await fetch_random_image_url(random_word)

    async with aiohttp.ClientSession() as session:
        meme_bytes = await create_meme_image(session, top_text, bottom_text, image_url)

        await message.reply_photo(photo=BytesIO(meme_bytes), caption=f"**Prompt:** {input_text}\n\n**Top text:** \"{top_text}\"\n\n**Bottom text:** \"{bottom_text}\"", parse_mode=enums.ParseMode.MARKDOWN)


def extract_meme_text(meme_text):
    meme_data = meme_text.splitlines()

    top_text = meme_data[0].split("ext:")[1].upper().strip()[1:-1] if len(meme_data[0].split("ext:")) > 1 else "TOP TEXT"
    bottom_text = meme_data[1].split("ext:")[1].upper().strip()[1:-1] if len(meme_data[1].split("ext:")) > 1 else "BOTTOM TEXT"

    return top_text, bottom_text