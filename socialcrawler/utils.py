from collections import namedtuple
import json
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fuzzywuzzy import process
import tweepy


CONTACTS_FILE = "./data/contacts.csv"
ACCOUNTS_FILE = "./data/accounts.txt"


def init_twitter_api():
    auth_tokens = get_config().twitter_auth
    auth = tweepy.OAuthHandler(
        auth_tokens.consumer_key, auth_tokens.consumer_secret
    )
    auth.set_access_token(
        auth_tokens.access_token, auth_tokens.access_token_secret
    )
    return tweepy.API(
        auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True
    )


def get_config():
    with open("config.json", "r") as f:
        config = json.load(
            f, object_hook=lambda d: namedtuple("X", d.keys())(*d.values())
        )
    return config


def get_accounts():
    with open(ACCOUNTS_FILE, "r") as file:
        accounts = file.readlines()
    return accounts


def connect_db():
    db_url = get_config().db.url
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()


def get_full_names():
    full_names = []
    with open(CONTACTS_FILE, "r") as csvfile:
        text = csv.reader(csvfile)
        for row in text:
            full_names.append(" ".join(row[1:3]))
    return full_names


full_names = get_full_names()
match_name = lambda name: dict(
    zip(("name", "ratio"), process.extractOne(name, full_names))
)
