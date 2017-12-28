from __future__ import print_function

import tweepy

from socialcrawler.models import TwitterUser, TwitterConnection, TwitterEntry
from socialcrawler.utils import row_exist


class UserCrawler(object):
    def __init__(self, api, session, user_id):
        self._api = api
        self._session = session
        self._user_id = user_id

    def _create_user(self, user):
        self._session.add(TwitterUser(
            id=user.id,
            name=user.name,
            screen_name=user.screen_name,
            description=user.description,
            followers_count=user.followers_count,
            friends_count=user.friends_count,
            favourites_count=user.favourites_count,
            statuses_count=user.statuses_count,
            lang=user.lang
        ))
        self._session.commit()

    def _create_connection(self, from_user_id, to_user_id):
        self._session.add(TwitterConnection(
            from_user_id=from_user_id,
            to_user_id=to_user_id
        ))
        self._session.commit()

    def _fetch_connection_ids(self, user_id, connection_type):
        connection_fetcher = getattr(self._api, "{}_ids".format(connection_type))
        return tweepy.Cursor(connection_fetcher, id=user_id).items()

    def _fetch_user(self, user_id):
        try:
            return self._api.get_user(user_id)
        except tweepy.TweepError as e:
            if e.api_code == 50:
                print("user, {} not found.".format(self._user_id))
            return None

    def _crawl_connections(self, connection_type, user_id, depth, con_limit):
        connection_ids = self._fetch_connection_ids(user_id, connection_type)
        while True:
            try:
                connection_id = connection_ids.next()
                if not row_exist(self._session, TwitterUser, id=connection_id):
                    user = self._fetch_user(connection_id)
                    if not user:
                        continue
                    self._create_user(user)
                self._crawl_connection(connection_type, user_id, depth, con_limit, connection_id)
            except tweepy.TweepError:
                print("not authorized to see {} of user, {}.".format(connection_type, self._user_id))
                return
            except StopIteration:
                return

    def _crawl_connection(self, connection_type, user_id, depth, con_limit, connection_id):
        if connection_type == "friends" and \
                not row_exist(self._session, TwitterConnection, from_user_id=user_id, to_user_id=connection_id):
            self._create_connection(user_id, connection_id)
        elif connection_type == "followers" and \
                not row_exist(self._session, TwitterConnection, from_user_id=connection_id, to_user_id=user_id):
            self._create_connection(connection_id, user_id)

        if depth > 1:
            crawler = UserCrawler(self._api, self._session, connection_id)
            crawler.crawl(depth - 1, con_limit)

    def _crawl_friends(self, *args):
        self._crawl_connections("friends", *args)

    def _crawl_followers(self, *args):
        self._crawl_connections("followers", *args)

    def _crawl_all(self, *args):
        self._crawl_friends(*args)
        self._crawl_followers(*args)

    def crawl(self, depth, con_limit):
        user = self._api.get_user(self._user_id)
        if not user:
            return
        if not row_exist(self._session, TwitterUser, id=user.id):
            self._create_user(user)
        if user.followers_count + user.friends_count > con_limit:
            return
        self._user_id = user.id
        self._crawl_all(self._user_id, depth, con_limit)


class UserTweetCrawler(object):
    def __init__(self, api, session, user_id):
        self._api = api
        self._user_id = user_id
        self._session = session

    def _create_entry(self, tweet):
        self._session.merge(TwitterEntry(
            id=tweet.id,
            user_id=self._user_id,
            text=tweet.text
        ))
        self._session.commit()

    def crawl(self):
        cursor = tweepy.Cursor(self._api.user_timeline, id=self._user_id).items()
        while True:
            try:
                tweet = cursor.next()
                self._create_entry(tweet)
            except tweepy.TweepError:
                print("not authorized to see tweets of user, {}.".format(self._user_id))
                return
            except StopIteration:
                return
