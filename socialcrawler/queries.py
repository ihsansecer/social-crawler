from sqlalchemy import desc

from socialcrawler.models import TwitterConnection, TwitterConnectionChange


def get_row(session, model, **kwargs):
    return session.query(model).filter_by(**kwargs).first()


def get_rows(session, model, **kwargs):
    return session.query(model).filter_by(**kwargs).all()


def row_exist(session, model, **kwargs):
    return get_row(session, model, **kwargs) is not None


def get_connections(session, user_id):
    return session.query(TwitterConnection).\
        filter(TwitterConnection.from_user_id==user_id,
        TwitterConnection.to_user_id==user_id)


def get_recent_connection_change(session, connection_id):
    return session.query(TwitterConnectionChange).\
        filter(TwitterConnectionChange.connection_id==connection_id).\
        order_by(desc("created_at")).first()


def get_recent_connection_ids(session, user_id):
    friends, followers = [], []
    connections = get_connections(session, user_id)
    for connection in connections:
        last_change = get_recent_connection_change(session, connection.id)
        if last_change.is_added:
            if connection.from_user_id == user_id:
                friends.append(connection.to_user_id)
            else:
                followers.append(connection.from_user_id)
    return friends, followers
