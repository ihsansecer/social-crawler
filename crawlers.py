import tweepy


class UserCrawler(object):
    def __init__(self, user_id, api):
        self._api = api
        self._user_id = user_id
        self._data = {}

    def _init_user(self, user_id):
        self._data.setdefault(user_id, {
            "friends": {},
            "followers": {}
        })

    def _extend_user(self, parent_id, user_id, connection_type):
        self._data[parent_id][connection_type].setdefault(user_id, {
            "friends": {},
            "followers": {}
        })

    def _fetch_connection_ids(self, user_id, connection_type):
        connection_fetcher = getattr(self._api, "{}_ids".format(connection_type))
        try:
            return connection_fetcher(user_id)
        except tweepy.TweepError:
            return []

    def _crawl_connections(self, connection_type, user_id, depth):
        self._init_user(user_id)
        connection_ids = self._fetch_connection_ids(user_id, connection_type)
        for connection_id in connection_ids:
            self._extend_user(user_id, connection_id, connection_type)
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
        self._crawl_all(self._user_id, depth)
        return self._data


class UserTweetCrawler(object):
    def __init__(self, user_id, api):
        self._api = api
        self._user_id = user_id
