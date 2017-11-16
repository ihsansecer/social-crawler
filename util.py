import json

import tweepy


def authenticate():
    auth_tokens = json.load(open("auth_tokens.json"))
    auth = tweepy.OAuthHandler(auth_tokens["consumer_key"], auth_tokens["consumer_secret"])
    auth.set_access_token(auth_tokens["access_token"], auth_tokens["access_token_secret"])
    return tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
