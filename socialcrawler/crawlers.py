from __future__ import print_function

import tweepy

from socialcrawler.models import TwitterUser, TwitterConnection, TwitterEntry, TwitterConnectionChange
from socialcrawler.queries import get_row, row_exist, get_recent_connection_change, get_recent_connection_ids
from socialcrawler.utils import match_screen_name


class UserCrawler(object):
    def __init__(self, api, session, user_id):
        self._api = api
        self._session = session
        self._user_id = user_id

    def _create_user(self, user, match, match_ratio):
        twitter_user = TwitterUser(
            id=user.id,
            name=user.name,
            screen_name=user.screen_name,
            match_name = match["name"],
            match_ratio = match["ratio"],
            lang=user.lang
        )
        self._session.add(twitter_user)
        self._session.commit()

    def _create_connection(self, from_user_id, to_user_id):
        twitter_connection = TwitterConnection(
            from_user_id=from_user_id,
            to_user_id=to_user_id
        )
        self._session.add(twitter_connection)
        self._session.commit()
        self._create_connection_change(True, twitter_connection.id)

    def _create_connection_change(self, is_added, connection_id):
        twitter_connection_change = TwitterConnectionChange(
            is_added=is_added,
            connection_id=connection_id
        )
        self._session.add(twitter_connection_change)
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

    def _check_fetch_user(self, user_id, match_ratio):
        row = get_row(self._session, TwitterUser, id=user_id)
        user = self._fetch_user(user_id) if not row else row
        if user:
            match = match_screen_name(user.screen_name)
            if not row:
                self._create_user(user, match, match_ratio)
        return user, match

    def _crawl_connections(self, connection_type, user_id, depth, matches, match_ratio, connection_limit):
        connection_ids = self._fetch_connection_ids(user_id, connection_type)
        while True:
            try:
                connection_id = connection_ids.next()
                user, match = self._check_fetch_user(connection_id, match_ratio)
                if not user:
                    continue
                self._crawl_connection(connection_type, user_id, match, depth, matches, match_ratio, connection_limit, connection_id)
            except tweepy.TweepError:
                print("not authorized to see {} of user, {}.".format(connection_type, self._user_id))
                return
            except StopIteration:
                return

    def _crawl_connection(self, connection_type, user_id, match, depth, matches, match_ratio, connection_limit, connection_id):
        if connection_type == "friends":
            connection_id in self._friends and self._friends.remove(connection_id)
            self._create_connection_addition(user_id, connection_id)
        elif connection_type == "followers":
            connection_id in self._friends and self._followers.remove(connection_id)
            self._create_connection_addition(connection_id, user_id)

        if depth > 1 and (not matches or match["ratio"] >= match_ratio):
            crawler = UserCrawler(self._api, self._session, connection_id)
            crawler.crawl(depth - 1, matches, match_ratio, connection_limit)

    def _create_connection_addition(self, from_user_id, to_user_id):
        connection = get_row(self._session, TwitterConnection, from_user_id=from_user_id, to_user_id=to_user_id)
        if connection is None:
            self._create_connection(from_user_id, to_user_id)
        elif not get_recent_connection_change(self._session, connection.id).is_added:
            self._create_connection_change(True, connection.id)

    def _create_connection_deletions(self):
        remaining_connections = self._friends + self._followers
        for connection in remaining_connections:
            self._create_connection_change(False, connection.id)

    def _crawl_friends(self, *args):
        self._crawl_connections("friends", *args)

    def _crawl_followers(self, *args):
        self._crawl_connections("followers", *args)

    def _crawl_all(self, *args):
        self._crawl_friends(*args)
        self._crawl_followers(*args)
        self._create_connection_deletions()

    def crawl(self, depth, matches, match_ratio, connection_limit):
        user = self._fetch_user(self._user_id)
        print("Crawling {}.".format(user.screen_name))
        if not user:
            return
        if not row_exist(self._session, TwitterUser, id=user.id):
            match = match_screen_name(user.screen_name)
            self._create_user(user, match, match_ratio)
        if user.followers_count + user.friends_count > connection_limit:
            return
        self._user_id = user.id
        self._friends, self._followers = get_recent_connection_ids(self._session, user.id)
        self._crawl_all(self._user_id, depth, matches, match_ratio, connection_limit)


class UserTweetCrawler(object):
    def __init__(self, api, session, user_id):
        self._api = api
        self._user_id = user_id
        self._session = session

    def _create_entry(self, tweet):
        twitter_entry = TwitterEntry(
            id=tweet.id,
            user_id=self._user_id,
            text=tweet.text
        )
        self._session.add(twitter_entry)
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
