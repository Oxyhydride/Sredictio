"""
TwitterScraper.py

Created on 2019-12-28
Updated on 2019-12-28

Copyright Ryan Kan 2019

Description: A test on a new sentiment retrieval method.

NOTE: This is currently unreliable. Hence, the sentiment file will NOT be replaced by this yet.

"""

# IMPORTS
import re
import datetime

from pprint import pprint
import twitterscraper

# CONSTANTS
COMPANY_NAME = "Facebook"

START_DATE = "2019-12-28"
END_DATE = "2019-12-29"

# CODE
noDaysPassed = 0
noArticles = 0
relevantArticles = {"Date": [], "Titles": []}

# Parse the `START_DATE` and `END_DATE`
startDate = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")
endDate = datetime.datetime.strptime(END_DATE, "%Y-%m-%d")

# Get how many days differ between `START_DATE` and `END_DATE`
dateDiff = (endDate - startDate).days

# Get articles
while noDaysPassed < dateDiff:
    # Get next window to scrape
    beginDate = datetime.datetime

    # Scrape from @BusinessTimes on twitter
    tweets = twitterscraper.query_tweets("@BusinessTimes", poolsize=20,
                                         begindate=startDate.date() + datetime.timedelta(days=noDaysPassed),
                                         enddate=startDate.date() + datetime.timedelta(days=(noDaysPassed + 1)))

    # Organise the tweets into a better dictionary
    articles = {"Timestamps": [], "Titles": []}

    for tweet in tweets:
        articles["Timestamps"].append(tweet.__dict__["timestamp"])
        articles["Titles"].append(tweet.__dict__["text"])

    # Process the gathered articles
    pprint(articles)
    pprint(list(zip(*articles.values())))
    print(len(list(zip(*articles.values()))))
    for article in zip(*articles.values()):  # Arrange by rows, and not by column
        articleTitle = article[1]

        # Check if `articleTitle` contains the company's name
        if articleTitle.upper().find(COMPANY_NAME.upper()) != -1:  # This article is relevant
            # Remove the ugly http://bit.ly thing at the end
            title = articleTitle[:re.search(r"(https|http):", articleTitle).start()]
            print(title)

            # Append title to `relevantArticles`
            relevantArticles["Date"].append(article[0].date().strftime("%Y-%m-%d"))
            relevantArticles["Titles"].append(title)

            noArticles += 1

    noDaysPassed += 1
    # print(relevantArticles)
