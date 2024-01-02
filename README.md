# TARSbot
A Telegram userbot based on Pyrogram

## Setup
To install Pyrogram (fork by KurimuzonAkuma):
```
pip3 install -U git+https://github.com/KurimuzonAkuma/pyrogram.git@dev
```

To install all the dependencies (sorry, there are a lot of them!):
```
pip3 install pyrogram ffmpy praw youtube-search-python tweepy pytimeparse wand openai justwatch wikipedia spotify_token deeppyer spacy music21 pytz 
```

Install Spacy's Italian news core:
```
python3 -m spacy download it_core_news_sm
```

To get the `lyrics.py` plugin running, see [this simple tutorial](https://github.com/enriquegh/spotify-webplayer-token#usage) on how to retrieve the keys `sp_dc` and `sp_key`.
