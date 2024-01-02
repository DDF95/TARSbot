from pyrogram import Client, filters
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

async def get_author_name(message):
    if message.reply_to_message.forward_sender_name:
        return message.reply_to_message.forward_sender_name
    elif message.reply_to_message.forward_from:
        return message.reply_to_message.forward_from.first_name
    elif message.reply_to_message.from_user.first_name:
        return message.reply_to_message.from_user.first_name
    else:
        return "Unknown"

async def get_quote(message):
    if message.reply_to_message.text:
        return message.reply_to_message.text
    elif message.reply_to_message.caption:
        return message.reply_to_message.caption
    else:
        return f"Lmao {message.from_user.first_name}, I just shitted my pants."

def create_instagram_quote(sentence, author, date, font_size=30):
    # Instagram default post size
    x1, y1 = 612, 612

    # Choose a font
    font_path = '/root/Fonts/Vollkorn-Regular.ttf'
    fnt = ImageFont.truetype(font_path, font_size)

    img = Image.new('RGB', (x1, y1), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Add line breaks and center the text
    formatted_sentence = format_sentence(sentence, x1, fnt, d)
    
    # Render the text in the center of the box
    dim = d.textsize(formatted_sentence, font=fnt)
    x2, y2 = dim[0], dim[1]
    
    qx, qy = (x1 // 2 - x2 // 2), (y1 // 2 - y2 // 2)

    d.text((qx, qy), formatted_sentence, align="center", font=fnt, fill=(100, 100, 100))

    # Add author and date to the image
    author_date_text = f"{author}, {date}"
    d.text((qx, qy + y2 + 10), author_date_text, align="center", font=fnt, fill=(100, 100, 100))

    # Save the image as bytes
    img_bytes_io = BytesIO()
    img.save(img_bytes_io, format='PNG')
    img_bytes = img_bytes_io.getvalue()
    img_bytes_io.close()
    
    return img_bytes

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

@Client.on_message(filters.command("testing", "!"))
async def quotes(client, message):
    if message.reply_to_message:
        author = await get_author_name(message)
        quote_text = await get_quote(message)

        # Get the current date in the format 'dd/mm/yyyy'
        current_date = datetime.now().strftime("%d/%m/%Y")

        # Create Instagram quote image
        instagram_quote_bytes = create_instagram_quote(quote_text, author, current_date)

        # Send the Instagram quote image
        await client.send_photo(chat_id=message.chat.id, photo=BytesIO(instagram_quote_bytes))
    else:
        await message.reply("Usage: `!quote` in reply to a message")
