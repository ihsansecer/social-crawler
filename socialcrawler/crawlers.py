import tweepy

from socialcrawler.models import TwitterUser, TwitterConnection


class UserCrawler(object):
    def __init__(self, api, session, user_id):
        self._api = api
        self._session = session
        self._user_id = user_id

    def _create_user(self, user_id, is_init=False):
        user = self._api.get_user(user_id)
        self._session.merge(TwitterUser(
            id=user.id,
            name=user.name,
            screen_name=user.screen_name,
            description=user.description
        ))
        if is_init:
            self._user_id = user.id

    def _create_connection(self, from_user_id, to_user_id):
        self._session.merge(TwitterConnection(
            from_user_id=from_user_id,
            to_user_id=to_user_id
        ))

    def _fetch_connection_ids(self, user_id, connection_type):
        connection_fetcher = getattr(self._api, "{}_ids".format(connection_type))
        try:
            return tweepy.Cursor(connection_fetcher, id=user_id).items()
        except tweepy.TweepError:
            return []

    def _crawl_connections(self, connection_type, user_id, depth):
        connection_ids = self._fetch_connection_ids(user_id, connection_type)
        for connection_id in connection_ids:
            self._create_user(connection_id)
            if connection_type == "friends":
                self._create_connection(user_id, connection_id)
            else:
                self._create_connection(connection_id, user_id)
            if depth > 1:
                self._crawl_all(connection_id, depth - 1)

    def _crawl_friends(self, *args):
        self._crawl_connections("friends", *args)

    def _crawl_followers(self, *args):
        self._crawl_connections("followers", *args)

    def _crawl_all(self, *args):
        self._crawl_friends(*args)
        self._crawl_followers(*args)

    def crawl(self, depth=1):
        self._create_user(self._user_id, is_init=True)
        self._crawl_all(self._user_id, depth)


class UserTweetCrawler(object):
    def __init__(self, api, user_id):
        self._api = api
        self._user_id = user_id
        self._data = {}
        self._data.setdefault(user_id, {"tweets": {}})

    def crawl(self):
        try:
            tweets = tweepy.Cursor(self._api.user_timeline, id=self._user_id).items()
            for tweet in tweets:
                self._data[self._user_id]["tweets"] \
                    .setdefault(tweet.id_str, {"date": str(tweet.created_at), "tweet": tweet.text})
            return self._data
        except tweepy.TweepError:
            return []
