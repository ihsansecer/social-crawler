# Social Crawler

This cli tool uses Twitter api to crawl friends and followers of institutional accouns of Şehir to build a network of the university. It also matches users with their e-mail accounts through their names. Tweets of the users are collected afterwards.

### Setup

Create a virtual environment

`virtualenv venv`

Activate virtual environment

`source venv/bin/activate`

Install requirements

`pip install -r requirements.txt`

Create a Postgres database

`CREATE DATABASE mydatabase`

Create config.json [file](#config-file) or copy sample_config.json and fill it

`cp sample_config.json config.json`

Run database migrations

`alembic upgrade head`

And ask for help!

`python main.py --help`

### Config file

twitter_auth:

&nbsp;&nbsp;&nbsp;&nbsp; authentication tokens taken from [apps.twitter.com](https://apps.twitter.com/)

db:

&nbsp;&nbsp;&nbsp;&nbsp; url: database address in the format of "driver://user:pass@localhost/dbname"
