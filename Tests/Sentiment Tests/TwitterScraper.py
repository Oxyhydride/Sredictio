"""
TwitterScraper.py

Created on 2019-12-28
Updated on 2019-12-28

Copyright Ryan Kan 2019

Description: A test on a new sentiment retrieval method.
"""

# IMPORTS
import re

import twitterscraper

# CODE
# Scrape from @BusinessTimes on twitter
tweets = twitterscraper.query_tweets_from_user("BusinessTimes", limit=10)

# Only keep the text part of the tweet
tweets = [{"Timestamp": tweet.__dict__["timestamp"], "Content": tweet.__dict__["text"]} for tweet in tweets]

# Remove the ugly http://bit.ly thing at the end
for tweet in tweets:
    tweetContent = tweet["Content"]
    tweetContent = tweetContent[:re.search(r"(https|http):", tweetContent).start()]

    tweet["Content"] = tweetContent

print(tweets)
