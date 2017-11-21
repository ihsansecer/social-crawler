# Social Crawler

This cli tool uses Twitter api to:
- Crawls friends and followers of users inside screen_names.json
- Filters crawled users using their connections to build a network
- Crawls tweets of built network (filtered users)

### Setup

Create virtual environment with Python 3 interpreter

`virtualenv -p /usr/bin/python3.5 venv`

Activate virtual environment

`source venv/bin/activate`

Install requirements

`pip install -r requirements.txt`

And ask for help!

`python main.py --help`