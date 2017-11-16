class UserCrawler(object):
    def __init__(self, user_id, api):
        self.api = api
        self.user = api.get_user(user_id)
        self.user_id = self.user.id
        self.data = {}
        self.data.setdefault(self.user.id, {
            "friends": {},
            "followers": {}
        })

    def _crawl_connections(self, connection_type):
        connection_fetcher = getattr(self.api, "{}_ids".format(connection_type))
        connections = connection_fetcher(self.user_id)
        for connection in connections:
            self.data[self.user_id][connection_type].setdefault(connection, {
                "friends": {},
                "followers": {}
            })

    def _crawl_friends(self):
        self._crawl_connections("friends")

    def _crawl_followers(self):
        self._crawl_connections("followers")

    def crawl(self):
        self._crawl_friends()
        self._crawl_followers()
        return self.data
