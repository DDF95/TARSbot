from configparser import ConfigParser

import tweepy
from pyrogram import Client, enums, filters

cfg = ConfigParser(interpolation=None)
cfg.read("config.ini")

TW_CONSUMER_KEY = cfg.get("twitter", "tw_consumer_key")
TW_CONSUMER_SECRET = cfg.get("twitter", "tw_consumer_secret")
TW_ACCESS_TOKEN = cfg.get("twitter", "tw_access_token")
TW_ACCESS_TOKEN_SECRET = cfg.get("twitter", "tw_access_token_secret")
TW_BEARER_TOKEN = cfg.get("twitter", "tw_bearer_token")

tw_client = tweepy.Client(
    TW_BEARER_TOKEN,
    TW_CONSUMER_KEY,
    TW_CONSUMER_SECRET,
    TW_ACCESS_TOKEN,
    TW_ACCESS_TOKEN_SECRET
)


# TODO: better error handling
@Client.on_message(filters.command("tweet", "!"))
async def send_tweet(client, message):
    if len(message.command) == 1:
        await message.reply(text="Usage: `!tweet <text>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        if len(message.text[1+5+1:]) > 280:
            await message.reply(text=f"Your tweet is too long ({len(message.text[1+5+1:])} characters). Max length is 280 characters.")
        elif len(message.text[1+5+1:]) <= 280:
            try:
                sent_tweet = tw_client.create_tweet(text=message.text[1+5+1:])

                if sent_tweet:
                    await message.reply(text=f"Tweet sent: https://twitter.com/rTARSbot/status/{sent_tweet.data['id']}")
                else:
                    await message.reply(text="Error: something went wrong while sending the tweet.")
            except Exception as e:
                await message.reply(text=f"Error:\n<code>{e}</code>")


@Client.on_message(filters.command("follow", "!"))
async def follow_user(client, message):
    if len(message.command) == 1:
        await message.reply(text="Usage: `!follow <Twitter username>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        try:
            username = message.command[1].replace("@", "")

            user_to_follow = tw_client.get_user(username=username)
            tw_client.follow_user(user_to_follow.data['id'])

            await message.reply(text=f"Now following @{username} on Twitter.")
        except Exception as e:
            await message.reply(text=f"Error:\nUser doesn't exist (probably).\n<code>{e}</code>")


@Client.on_message(filters.command("unfollow", "!"))
async def unfollow_user(client, message):
    if len(message.command) == 1:
        await message.reply(text="Usage: `!unfollow <Twitter username>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        try:
            username = message.command[1].replace("@", "")

            user_to_unfollow = tw_client.get_user(username=username)
            tw_client.unfollow_user(user_to_unfollow.data['id'])

            await message.reply(text=f"Now unfollowing @{username} on Twitter.")
        except Exception as e:
            await message.reply(text=f"Error:\nUser doesn't exist (probably).\n<code>{e}</code>")


@Client.on_message(filters.command("twsearch", "!"))
async def search_tweets(client, message):
    if len(message.command) == 1:
        await message.reply(text="Usage: `!twsearch <query>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        try:
            tweets = tw_client.search_recent_tweets(query=message.text[1+8+1:], max_results=10)

            if tweets:
                for tweet in tweets.data:
                    await message.reply(text=tweet)
            else:
                await message.reply(text="No tweets found.")
        except Exception as e:
            await message.reply(text=f"Error:\n<code>{e}</code>")
# TODO: make it less spammy


@Client.on_message(filters.command("tweets", "!"))
async def get_tweets(client, message):
    if len(message.command) == 1:
        await message.reply(text="Usage: `!tweets <Twitter username>`", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        try:
            username = message.command[1].replace("@", "")

            user = tw_client.get_user(username=username)
            user_id = user.data['id']
            tweets = tw_client.get_users_tweets(
                id=user_id,
                tweet_fields=[
                    'context_annotations',
                    'created_at',
                    'geo'
                ],
                max_results=5,
                exclude="replies,retweets"
            )

            if tweets:
                for tweet in tweets.data:
                    await message.reply(text=tweet)
            else:
                await message.reply(text="No tweets found.")
        except Exception as e:
            await message.reply(text=f"Error:\nUser doesn't exist (probably).\n<code>{e}</code>")