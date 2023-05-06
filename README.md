# Mastodon annual post stats

A python script for counting the number of Mastodon posts your account made each year.


## Set-up

You'll need to create a Mastodon API app, add or change configuration in a `.env` file, and install python requirements.

1. Create an application. Go to Preferences > Development, then click the "New application" button

2. Give it a name and choose what permissions it should have (at a minimum, Read Posts).

3. Copy `.env.dist` to `.env`

4. Add your app's Access Token, Client Key and Client Secret to `.env`

5. If your Mastodon instance isn't `https://mastodon.social` replace that value in `.env`

6. If you don't want to count direct or private posts in your counts, set one or both of those `EXCLUDE_...` values in `.env` to `True`.

7. Install the python requirements from `requirements.txt`: e.g. `pip -r requirements.txt`


## Run the script

By default, the script will count the number of posts made in the current year:

    $ python get_annual_stats.py
	philgyford made this many posts in:

	2023     221
	2022     199
	2021      10

Or specify the year to fetch the count for using `-y` or `--year`:

    $ python get_annual_stats.py -y 2022

or:

    $ python get_annual_stats.py --year=2022


## Caveats

This is was a hasty bit of coding so there might be errors!

It fetches statuses from the most recent backwards, 40 at a time, so it gets slower and slower for each year you go back.
