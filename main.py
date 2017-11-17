import click

from utils import authenticate, read_file, write_file
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
    screen_names = read_file("screen_names.json")
    data = {}
    api = authenticate()
    for screen_name in screen_names:
        crawler = UserCrawler(screen_name, api)
        data.update(crawler.crawl(depth=depth))
    write_file("data.json", data)


if __name__ == '__main__':
    cli()
