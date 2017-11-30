import click

from socialcrawler.crawlers import UserCrawler, UserTweetCrawler
from socialcrawler.networks import UserNetwork
from socialcrawler.utils import init_twitter_api, get_config, connect_db


@click.group()
def cli():
    """
    Steps: 1) Crawl users 2) Filter users 3) Crawl tweets
    """
    pass


@cli.command()
@click.option("--depth", "-d", default=1, help="Depth level of crawler")
def crawl_users(depth):
    """
    Crawls users in screen_names.json using their friends and followers. Then saves it to data.json with
    crawled_users key.
    """
    config = get_config()
    targets = config.twitter.targets
    api = init_twitter_api()
    session = connect_db()
    for target in targets:
        crawler = UserCrawler(api, session, target)
        crawler.crawl(depth=depth)


@cli.command()
@click.option("--incoming", "-in", default=1, help="Number of incoming edges")
@click.option("--outgoing", "-out", default=1, help="Number of outgoing edges")
def filter_users(incoming, outgoing):
    """
    Filters users by number of incoming and outgoing edges. Then saves it to data.json with filtered_users key.
    """
    targets = []
    network = UserNetwork(targets)
    network.create()
    network.filter(incoming, outgoing)


@cli.command()
def crawl_tweets():
    """
    Crawls tweets using filtered user ids inside data.json. Then saves it to data.json with crawled_tweets key.
    """
    targets = []
    api = init_twitter_api()
    for user in targets:
        crawler = UserTweetCrawler(api, user)
        crawler.crawl()


if __name__ == '__main__':
    cli()
