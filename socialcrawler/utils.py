from collections import namedtuple
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tweepy


def init_twitter_api():
    auth_tokens = get_config().twitter.auth
    auth = tweepy.OAuthHandler(auth_tokens.consumer_key, auth_tokens.consumer_secret)
    auth.set_access_token(auth_tokens.access_token, auth_tokens.access_token_secret)
    return tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def get_config():
    with open("config.json", 'r') as f:
        return json.load(f, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))


def connect_db():
    db_url = get_config().db.url
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()
