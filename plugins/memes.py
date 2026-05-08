import asyncio
import json
import logging
import random
from io import BytesIO
from typing import List, Optional, Tuple

import aiohttp
import spacy
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from pyrogram import Client, enums, filters

# Configuration and error Logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

PHOTOS_JSON_PATH = "photos.json"
FONT_PATH = "Fonts/impact.ttf"

DEFAULT_FONT_SIZE = 42
IMAGE_FETCH_TIMEOUT = 15

# Load spaCy model
try:
    nlp = spacy.load("it_core_news_sm")
except Exception as e:
    logger.error(f"Failed to load spaCy model 'it_core_news_sm': {e}")
    try:
        nlp = spacy.blank("it")
    except Exception:
        nlp = None


# Text processing (used for image selection)
def spacy_tokenizer(sentence: str) -> List[str]:
    """
    Return lemmatized, lowercase tokens excluding punctuation and stopwords.
    Falls back to simple splitting if spaCy isn't available.
    """
    try:
        if not sentence or not sentence.strip():
            return []
        if nlp:
            doc = nlp(sentence)
            return [token.lemma_.lower() for token in doc if not token.is_punct and not token.is_stop]
        else:
            return [w.strip().lower() for w in sentence.split() if w.strip()]
    except Exception as e:
        logger.error(f"Tokenizer error: {e}")
        return []


# Image selection
def load_photos_data(path: str = PHOTOS_JSON_PATH) -> dict:
    """Load photos JSON and normalise keys to lowercase."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {k.lower(): v for k, v in data.items()}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading photos JSON '{path}': {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading photos JSON: {e}")
        return {}


async def fetch_random_image_url(word: str, photos_data: Optional[dict] = None) -> str:
    """
    Returns a full image URL chosen randomly from the dataset.
    Raises ValueError on failure.
    """
    try:
        if photos_data is None:
            photos_data = load_photos_data()

        if not photos_data:
            raise ValueError("No image data available")

        lookup_key = word.lower() if word else ""
        if lookup_key and lookup_key in photos_data and photos_data[lookup_key]:
            urls = photos_data[lookup_key]
        else:
            all_urls = [u for urls in photos_data.values() for u in (urls or [])]
            if not all_urls:
                raise ValueError("No images available in database")
            urls = all_urls

        file_or_path = random.choice(urls)
        return f"https://jwlss.pw/markov-news/{file_or_path}"
    except Exception as e:
        logger.error(f"Image URL error: {e}")
        raise


# Meme image creation
def format_sentence(sentence: str, max_width: int, font: ImageFont.FreeTypeFont, draw: ImageDraw.ImageDraw) -> str:
    """
    Wrap words into lines to fit within max_width (pixels).
    """
    try:
        if not sentence:
            return ""
        words = sentence.split()
        lines: List[str] = []
        current_line: List[str] = []
        current_width = 0
        space_w = draw.textlength(" ", font=font)

        for word in words:
            w_w = draw.textlength(word, font=font)
            if current_line and (current_width + w_w + space_w) > max_width:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_width = w_w + space_w
            else:
                current_line.append(word)
                current_width += w_w + (space_w if current_line and len(current_line) > 1 else 0)

        if current_line:
            lines.append(" ".join(current_line))
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Format sentence error: {e}")
        return sentence


async def create_meme_image(session: aiohttp.ClientSession, top_text: str, bottom_text: str, image_url: str) -> bytes:
    """
    Fetch image and draw top/bottom text, returning PNG bytes.
    """
    try:
        try:
            async with session.get(image_url, timeout=IMAGE_FETCH_TIMEOUT) as resp:
                if resp.status != 200:
                    raise ValueError(f"Invalid image URL: {image_url}")
                image_bytes = await resp.read()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            raise ValueError(f"Failed to fetch image: {e}")

        try:
            img = Image.open(BytesIO(image_bytes)).convert("RGB")
        except UnidentifiedImageError:
            raise ValueError("Invalid image format received")
        except Exception as e:
            logger.error(f"Image open error: {e}")
            raise ValueError("Failed to open image")

        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(FONT_PATH, DEFAULT_FONT_SIZE)
        except IOError:
            logger.warning("Impact font not found, using default font")
            font = ImageFont.load_default()

        # Calculate maximum width and height for the image
        max_w, max_h = img.size

        # Set padding around the text to avoid drawing too close to edges
        padding = 10

        # Calculate usable width for text after accounting for padding
        usable_width = max_w - padding * 2

        # Format text into multiple lines if necessary to fit within usable width
        top_wrapped = format_sentence(top_text or "", usable_width, font, draw)
        bottom_wrapped = format_sentence(bottom_text or "", usable_width, font, draw)

        # Position
        try: # Calculate bounding box for top text to determine its width and height
            # Calculate bounding box for top text to determine its width and height
            top_bbox = draw.multiline_textbbox((0, 0), top_wrapped, font=font)

            # Calculate width and height of the top text from the bounding box
            top_w = top_bbox[2] - top_bbox[0]

            # Calculate height of the top text from the bounding box
            top_h = top_bbox[3] - top_bbox[1]

            # Calculate x position for the top text
            top_x = max((max_w - top_w) // 2, padding)

            # Set y position for the top text to be at the top with padding
            top_y = padding
        except Exception as e:
            logger.error(f"Top text bounding box error: {e}")

            # Fallback to default positions if bounding box calculation fails
            top_x, top_y = padding, padding

        try: # Calculate bounding box for bottom text to determine its width and height
            # Calculate bounding box for bottom text to determine its width and height
            bottom_bbox = draw.multiline_textbbox((0, 0), bottom_wrapped, font=font)

            # Calculate width of the bottom text from the bounding box
            bottom_w = bottom_bbox[2] - bottom_bbox[0]

            # Calculate height of the bottom text from the bounding box
            bottom_h = bottom_bbox[3] - bottom_bbox[1]

            # Calculate x position for the bottom text to be centered horizontally
            bottom_x = max((max_w - bottom_w) // 2, padding)

            # Set y position for the bottom text to be at the bottom with padding, accounting for text height
            bottom_y = max_h - padding - padding - padding - bottom_h
        except Exception as e:
            logger.error(f"Bottom text bounding box error: {e}")

            # Fallback to default positions if bounding box calculation fails
            bottom_x = padding
            bottom_y = max_h - padding - DEFAULT_FONT_SIZE

        # Draw text on image
        try:
            draw.multiline_text((top_x, top_y), top_wrapped, font=font, fill="white",
                                stroke_width=2, stroke_fill="black", align="center")
            draw.multiline_text((bottom_x, bottom_y), bottom_wrapped, font=font, fill="white",
                                stroke_width=2, stroke_fill="black", align="center")
        except Exception as e:
            logger.error(f"Text drawing error: {e}")

        # Save
        try:
            buf = BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Image save error: {e}")
            raise ValueError("Failed to save image")

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Meme creation error: {e}")
        raise ValueError("Failed to create meme image")


# Actual Telegram command handler
@Client.on_message(filters.command("meme", "!"))
async def create_meme(client: Client, message):
    """
    Handler for !meme command.
    Parses user input for top/bottom text, fetches an image, creates and sends the meme.
    """
    msg_text = (message.text or "").strip()
    is_reply = bool(message.reply_to_message)

    # Determine if command is bare "!meme" (no additional text)
    bare_command = msg_text == "!meme"

    # Bare command with no reply -> show help
    if bare_command and not is_reply:
        help_text = (
            "**Usage:**\n"
            "• \"`!meme <top text>`\" - top text only\n"
            "• \"`!meme <top text> / <bottom text>`\" - top and bottom texts are separated by ` / ` (with spaces)\n"
            "• \"`!meme`\" (in reply to a message) - reply to a message with `!meme` to use the message's text as top text"
        )
        await message.reply(help_text, parse_mode=enums.ParseMode.MARKDOWN)
        return

    # Bare command in reply -> use replied message as top text
    if bare_command and is_reply:
        top_text = message.reply_to_message.text or ""
        bottom_text = ""
        input_text = top_text
    else:
        # Extract text after "!meme" (skip leading space)
        if len(msg_text) > 5:
            raw = msg_text[5:].strip()
        else:
            raw = ""
        if not raw:
            await message.reply("Please provide meme text.", parse_mode=enums.ParseMode.MARKDOWN)
            return

        # Split on " / " (space-slash-space) for top / bottom
        if " / " in raw:
            parts = raw.split(" / ", 1)
            top_text = parts[0].strip()
            bottom_text = parts[1].strip() if len(parts) > 1 else ""
        else:
            top_text = raw.strip()
            bottom_text = ""

        # The full raw text is used for image selection (tokenization)
        input_text = raw

    # Validate at least top text present
    if not top_text:
        await message.reply("Please provide meme text.", parse_mode=enums.ParseMode.MARKDOWN)
        return

    # Image selection
    try:
        tokens = spacy_tokenizer(input_text)
        if not tokens:
            tokens = ["meme"]
        chosen_word = random.choice(tokens)
        photos_data = load_photos_data()
        image_url = await fetch_random_image_url(chosen_word, photos_data)
    except Exception as e:
        logger.error(f"Image selection error: {e}")
        await message.reply("⚠️ Error selecting meme image. Please try again.")
        return

    # Meme creation
    try:
        async with aiohttp.ClientSession() as session:
            meme_bytes = await create_meme_image(session, top_text.upper(), bottom_text.upper(), image_url)
    except ValueError as e:
        logger.error(f"Meme creation failed: {e}")
        await message.reply("⚠️ Failed to create meme image. Please try again.")
        return
    except Exception as e:
        logger.error(f"Meme creation unexpected error: {e}")
        await message.reply("⚠️ Failed to create meme image. Please try again.")
        return

    # Send result
    try:
        caption = f"**Top text:** {top_text}"
        if bottom_text:
            caption += f"\n**Bottom text:** {bottom_text}"

        await message.reply_photo(
            photo=BytesIO(meme_bytes),
            caption=caption,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Message sending error: {e}")
        await message.reply("⚠️ Failed to send meme. Please try again.")
