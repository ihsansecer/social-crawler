import json

import click

from util import authenticate
from crawlers import UserCrawler


@click.group()
def cli():
    pass


@cli.command()
@click.option("--depth", "-d", default=1, help="Depth level of crawler")
def crawl_users(depth):
    """
    Crawl users in screen_names.json using their friends and followers.Then saves it to data.json
    """
    with open("screen_names.json", 'r') as f:
        screen_names = json.load(f)

    data = {}
    api = authenticate()
    for screen_name in screen_names:
        crawler = UserCrawler(screen_name, api)
        data.update(crawler.crawl(depth=depth))

    with open("data.json", 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    cli()
