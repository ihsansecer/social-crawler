import click

from socialcrawler.crawlers import UserCrawler, UserTweetCrawler
from socialcrawler.models import TwitterUser
from socialcrawler.networks import TwitterUserNetwork
from socialcrawler.utils import init_twitter_api, get_config, connect_db


@click.group()
def cli():
    pass


@cli.command()
@click.option("--depth", "-d", default=1, help="Depth level of crawler")
def crawl_users(depth):
    """
    Crawls users in screen_names.json using their friends and followers.
    """
    config = get_config()
    targets = config.twitter.targets
    api = init_twitter_api()
    session = connect_db()
    for target in targets:
        crawler = UserCrawler(api, session, target)
        crawler.crawl(depth=depth)


@cli.command()
def create_network():
    """
    Creates a twitter user network. (Not complete)
    """
    session = connect_db()
    network = TwitterUserNetwork(session)
    network.create()


@cli.command()
def crawl_tweets():
    """
    Crawls tweets using users in database.
    """
    api = init_twitter_api()
    session = connect_db()
    targets = session.query(TwitterUser).all()
    for user in targets:
        crawler = UserTweetCrawler(api, session, user.id)
        crawler.crawl()


if __name__ == '__main__':
    cli()
