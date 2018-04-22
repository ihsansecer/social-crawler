import click

from socialcrawler.crawlers import UserCrawler, UserTweetCrawler
from socialcrawler.models import TwitterUser
from socialcrawler.queries import get_rows
from socialcrawler.utils import init_twitter_api, connect_db, get_accounts


@click.group()
def cli():
    pass


@cli.command()
@click.option("--depth", "-d", default=1, help="Depth level of crawler")
@click.option('--matchings/--community', default=False)
@click.option("--match-ratio", "-mr", default=80, help="Match ratio threshold to continue crawling")
@click.option("--connection-limit", "-cl", default=15000, help="Connection limit to crawl connections")
def crawl_users(depth, matchings, match_ratio, connection_limit):
    """
    Crawls users in screen_names.json using their friends and followers.
    """
    api = init_twitter_api()
    session = connect_db()
    if matchings:
        crawl_matched_accounts(depth, match_ratio, connection_limit, session, api)
    else:
        crawl_community_accounts(depth, match_ratio, connection_limit, session, api)


def crawl_community_accounts(depth, match_ratio, connection_limit, session, api):
    targets = get_accounts()
    for target in targets:
        crawler = UserCrawler(api, session, target)
        crawler.crawl(depth, match_ratio, connection_limit)


def crawl_matched_accounts(depth, match_ratio, connection_limit, session, api):
    targets = get_rows(session, TwitterUser, match_ratio=match_ratio)
    for target in targets:
        crawler = UserCrawler(api, session, target.id)
        crawler.crawl(depth, match_ratio, connection_limit)


@cli.command()
def crawl_tweets():
    """
    Crawls tweets using users in database.
    """
    api = init_twitter_api()
    session = connect_db()
    targets = get_rows(TwitterUser)
    for user in targets:
        crawler = UserTweetCrawler(api, session, user.id)
        crawler.crawl()


if __name__ == '__main__':
    cli()
