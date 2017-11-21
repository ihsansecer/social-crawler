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

<<<<<<< HEAD
class UserTweetCrawler(object):
    def __init__(self, user_list):
        self.user_list = user_list
        self.user_tweets = []
        self.result = []

    def catch_user(self):
        for user_id in self.user_list:
            crawl_tweets.get_all_tweets(user_id)

        return self.result

    def get_all_tweets(self, user_id):
        all_tweets = []
        new_tweets = api.user_timeline(id=user_id, count=200)
        all_tweets.extend(new_tweets)
        oldest = all_tweets[-1].id - 1

        while len(new_tweets) > 0:
            new_tweets = api.user_timeline(id=user_id, count=200, max_id=oldest)
            all_tweets.extend(new_tweets)
            oldest = all_tweets[-1].id - 1

        self.user_tweets = [{user_id: {"tweet_id": tweet.id_str, "date": str(tweet.created_at),
                                  "tweet": tweet.text.encode("utf-8")}} for tweet in all_tweets]

        crawl_tweets.convert_json()

    def convert_json(self):
        try:
            old_results = json.loads(self.result)
            self.result = json.dumps(old_results + self.user_tweets)

        except TypeError:
            self.result = json.dumps(self.user_tweets)
=======

class UserTweetCrawler(object):
    def __init__(self, user_id, api):
        self._api = api
        self._user_id = user_id
>>>>>>> 0a6711a3bfa7ee6f5baefd448303b3a9127845cd
