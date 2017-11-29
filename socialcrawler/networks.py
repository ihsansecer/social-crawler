import networkx as nx


class UserNetwork(object):
    def __init__(self, user_data):
        self._g = nx.DiGraph()
        self._user_data = user_data

    def _create_network(self, user_data):
        for user in user_data:
            self._g.add_node(user)
            self._extend_network(user, user_data)

    def _extend_network(self, user, user_data):
        friends, followers = user_data[user]["friends"], user_data[user]["followers"]
        if friends:
            self._create_friends_network(user, friends)
            self._create_network(friends)
        if followers:
            self._create_followers_network(user, followers)
            self._create_network(followers)

    def _create_connections_network(self, connection_type, user, connections):
        self._g.add_nodes_from(connections)
        edges = [(user, connection) if connection_type == "fr" else (connection, user) for connection in connections]
        self._g.add_edges_from(edges)

    def _create_friends_network(self, *args):
        self._create_connections_network("fr", *args)

    def _create_followers_network(self, *args):
        self._create_connections_network("fo", *args)

    def create(self):
        self._create_network(self._user_data)
        return self._g

    def filter(self, incoming, outgoing):
        filtered = []
        for node in self._g:
            if incoming <= len(self._g.in_edges(node)) and outgoing <= len(self._g.out_edges(node)):
                filtered.append(node)
        return filtered
