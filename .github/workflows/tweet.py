
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
import tweepy

link_repo = "https://github.com/dssg-pt/dados-SICOeVM"

# Login

# to verify the tweet content without publishing, use
# export TWITTER_CONSUMER_KEY=DEBUG
consumer_key = os.environ['TWITTER_CONSUMER_KEY']
if consumer_key != 'DEBUG':
    consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
    access_token = os.environ['TWITTER_ACCESS_TOKEN']
    access_token_secret = os.environ['TWITTER_ACCESS_SECRET']

def autenticar_twitter():
    # authentication of consumer key and secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    # authentication of access token and secret
    auth.set_access_token(access_token, access_token_secret)
    try:
        api = tweepy.API(auth)
        return api
    except Exception as e:
        print("Erro a autenticar")
        print(e)
        pass

def compor_tweets():
    """
    TODO: More complex message.
    """

    # Main tweet
    tweet_message = (
        "🆕Dados do portal SICO-eVM atualizados:\n"
        "https://github.com/dssg-pt/dados-SICOeVM"
    )

    return tweet_message

def tweet_len(s):
    # quick hack to kind of count emojis as 2 chars
    # not 100% to spec
    return sum( (2 if ord(c)>0x2100 else 1) for c in s)


if __name__ == '__main__':

    texto_tweet_1 = compor_tweets()

    if consumer_key == 'DEBUG':
        print(f"Tweet 1 {tweet_len(texto_tweet_1)} '''\n{texto_tweet_1}\n'''")
        exit(0)

    api = autenticar_twitter()
    try:
      api.me()
    except Exception as ex:
        print("Erro na autenticação. Programa vai fechar")
        exit(0)

    # Update status and create thread
    try:
        tweet1 = api.update_status(status = texto_tweet_1)
    except Exception as e:
        print("Erro a enviar o tweet")
        print(e)
        pass
