import argparse
from datetime import datetime, timezone
import os

from dotenv import load_dotenv
from mastodon import Mastodon


# Loads env variables from .env:
load_dotenv()

EXCLUDE_DIRECT_POSTS = os.getenv("EXCLUDE_DIRECT_POSTS", default="False") == "True"
EXCLUDE_PRIVATE_POSTS = os.getenv("EXCLUDE_PRIVATE_POSTS", default="False") == "True"


# Which year are we fetching, if any?

parser = argparse.ArgumentParser(
    description="Fetch the number of Mastodon posts an account posted in a year"
)
parser.add_argument("-y", "--year", type=int, help="Year to fetch")
args = parser.parse_args()

year_to_fetch = args.year

if year_to_fetch:
    start_of_year = datetime(year=year_to_fetch, month=1, day=1, tzinfo=timezone.utc)
    end_of_year = datetime(
        year=year_to_fetch,
        month=12,
        day=31,
        hour=23,
        minute=59,
        second=59,
        tzinfo=timezone.utc,
    )


# Log in

client = Mastodon(
    client_id=os.getenv("CLIENT_KEY"),
    client_secret=os.getenv("CLIENT_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    api_base_url=os.getenv("MASTODON_INSTANCE_URL"),
)

account = client.account_verify_credentials()


# Fetch all the posts (or all the posts for the chosen year)

posts = []
max_id = None

while True:
    kwargs = {"max_id": max_id, "limit": 40}
    if year_to_fetch:
        kwargs["since_id"] = start_of_year

    timeline = client.account_statuses(account["id"], **kwargs)

    if not timeline:
        break

    # Remove any posts we don't want to count:
    filtered_timeline = timeline
    if EXCLUDE_DIRECT_POSTS:
        filtered_timeline = [
            t for t in filtered_timeline if t["visibility"] != "direct"
        ]
    if EXCLUDE_PRIVATE_POSTS:
        filtered_timeline = [
            t for t in filtered_timeline if t["visibility"] != "private"
        ]

    posts += filtered_timeline
    max_id = timeline[-1]["id"]

    if year_to_fetch and timeline[-1]["created_at"] < start_of_year:
        # No need to carry on beyond the start of chosen year
        break


# Count the number of posts per year

counts = {}
for post in posts:
    if year_to_fetch:
        if (
            start_of_year
            <= post["created_at"].replace(tzinfo=timezone.utc)
            <= end_of_year
        ):
            if year_to_fetch in counts:
                counts[year_to_fetch] += 1
            else:
                counts[year_to_fetch] = 1
    else:
        post_year = str(post["created_at"].replace(tzinfo=timezone.utc).year)
        if post_year in counts:
            counts[post_year] += 1
        else:
            counts[post_year] = 1


# Output

if EXCLUDE_DIRECT_POSTS and EXCLUDE_PRIVATE_POSTS:
    constraints = " not-direct, not-private"
elif EXCLUDE_DIRECT_POSTS:
    constraints = " not-direct"
elif EXCLUDE_PRIVATE_POSTS:
    constraints = " not-private"
else:
    constraints = ""

print(f"{account['username']} made this many{constraints} posts in:\n")

for count_year, count in counts.items():
    print(f"{count_year}{count:>8}")
