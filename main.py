import datetime

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
@click.option(
    "--matchings/--community",
    default=False,
    help="Start crawling from matchings or community accounts",
)
@click.option(
    "--matches/--all",
    default=False,
    help="Use match ratio as a threshold to continue crawling or not",
)
@click.option(
    "--match-ratio",
    "-mr",
    default=80,
    help="Match ratio threshold to continue crawling",
)
@click.option(
    "--connection-limit",
    "-cl",
    default=15000,
    help="Connection limit to crawl connections",
)
def crawl_users(depth, matchings, matches, match_ratio, connection_limit):
    """
    Crawls users in screen_names.json using their friends and followers.
    """
    api = init_twitter_api()
    session = connect_db()
    targets = (
        get_rows(session, TwitterUser, match_ratio=match_ratio)
        if matchings
        else get_accounts()
    )
    for target in targets:
        crawler = (
            UserCrawler(api, session, target.id)
            if matchings
            else UserCrawler(api, session, target)
        )
        crawler.crawl(depth, matches, match_ratio, connection_limit)


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


if __name__ == "__main__":
    cli()
