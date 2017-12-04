import snap as sp

from socialcrawler.models import TwitterUser, TwitterConnection


class TwitterUserNetwork(object):
    def __init__(self, session):
        self._session = session
        self._graph = sp.TNGraph.New()
        self._users = session.query(TwitterUser).all()

    @staticmethod
    def _get_id_attr(obj, connection_type, is_user):
        direction = "from" if (is_user and connection_type == "friend") \
                       or not (is_user and connection_type == "follower") else "to"
        return getattr(obj, "{}_user_id".format(direction))

    def _find_connection_index(self, connection_id_attr):
        return next(i for i, user in enumerate(self._users) if user.id == connection_id_attr)

    def _create_edges(self, connection_type, user, user_index):
        user_id_attr = self._get_id_attr(TwitterConnection, connection_type, True)
        connections = self._session.query(TwitterConnection).filter(user_id_attr == user.id).all()
        for connection in connections:
            connection_id_attr = self._get_id_attr(connection, connection_type, False)
            connection_index = self._find_connection_index(connection_id_attr)
            if not self._graph.IsNode(connection_index):
                self._graph.AddNode(connection_index)
            self._graph.AddEdge(connection_index, user_index)

    def _create_friend_edges(self, *args):
        self._create_edges("friend", *args)

    def _create_follower_edges(self, *args):
        self._create_edges("follower", *args)

    def _create_all(self, *args):
        self._create_friend_edges(*args)
        self._create_follower_edges(*args)

    def create(self):
        for user_index, user in enumerate(self._users):
            if not self._graph.IsNode(user_index):
                self._graph.AddNode(user_index)
            self._create_all(user, user_index)

    def get(self):
        return self._graph
