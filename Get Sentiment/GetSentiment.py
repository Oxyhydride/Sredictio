"""
GetSentiment.py
Version 2.0.6

Created on 2019-04-29
Updated on 2019-11-26

Copyright Ryan Kan

Description: A helper program to scrap sentiments and generate the {NAME}_Sentiments.csv file for model training.
             The sentiments are taken from the Straits Times' website.
"""

# IMPORTS
import time
import json
from datetime import datetime
from urllib.request import Request, urlopen

import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# CONSTANTS
STOCK_SYMBOL = "BTC"  # What is the symbol for the stock?
STOCK_NAME = "Bitcoin"  # What's the company's name?

OUTPUT_DIR = "./output/"  # Where should the sentiment csv go?

BATCH_SIZE = 20  # How many articles to be read every time?
TIME_OFFSET = 8  # What's the timezone offset? E.g. for GMT+8, put 8

END_DATE = "2018-01-01"  # At what date should the program stop searching for articles? Leave in YYYY-MM-DD.

IRRELEVANT_POST_TOLERANCE = 20  # How many irrelevant posts to process before halting?

# CODE
sia = SentimentIntensityAnalyzer()  # The VADER sentiment analyser
hoursToSearch = (datetime.today() - datetime.strptime(END_DATE, "%Y-%m-%d")).days * 24

# Search for articles and generate sentiment
pageNo = 1
date_sentiments = {}
endedSearch = False

irrelevantPosts = 0
truePostCount = -1
totalPosts = 0

while True:
    print(f"\n{'-' * 50}\nPAGE {pageNo}\n{'-' * 50}")

    time.sleep(0.1)  # We don't want to overload the website, right?

    pageURL = "http://api.queryly.com/json.aspx?queryly_key=a7dbcffb18bb41eb&query={}&endindex={}&batchsize={}&timezoneoffset={}&facetedvalue={}&facetedkey=pubDate".format("%20".join(STOCK_NAME.lower().split()), (pageNo - 1) * BATCH_SIZE, BATCH_SIZE, TIME_OFFSET, hoursToSearch)
    header = {'User-Agent': 'Mozilla/5.0'}  # Do not modify!
    request = Request(pageURL, headers=header)

    page = urlopen(request).read()  # Returns the articles from the straits times

    pageData = str(page, "UTF-8")
    pageDict = json.loads(pageData)  # Hilariously, the articles are arranged in a dictionary
    
    allPosts = pageDict["items"]  # All the articles on the page can be found here
    truePostCount = pageDict["metadata"]["total"]  # The actual number of articles

    for post in allPosts:
        postTitle = post["title"]  # The title of the article
        postDesc = post["description"]  # The description of the article
        postUnix = post["pubdateunix"]  # Unix time of when the article was posted

        if ((postTitle.lower().find(STOCK_NAME.lower()) != -1) and (postDesc.lower().find(STOCK_NAME.lower()) != -1)):  # If the stock's name is found in the title and the description
            irrelevantPosts = 0
            postDate = datetime.fromtimestamp(postUnix).strftime("%Y-%m-%d")

            sentimentTitle = sia.polarity_scores(postTitle)['compound']  # Take the compound sentiment of the title
            sentimentDesc = sia.polarity_scores(postDesc)['compound']  # Take the compound sentiment of the description

            print("\n\n" + postDate + ": " + postTitle + "\n" + postDesc)
            print(f"\nSENTIMENTS\nTITLE: {sentimentTitle:.6f} | DESCRIPTION: {sentimentDesc:.6f}")

            if postDate not in date_sentiments.keys():  # If an article on that date has yet to be processed
                date_sentiments[postDate] = []  # Make a new list

            avgSentiment = (sentimentTitle + sentimentDesc) / 2
            date_sentiments[postDate].append(avgSentiment)

            totalPosts += 1

        else:
            irrelevantPosts += 1

    if irrelevantPosts > IRRELEVANT_POST_TOLERANCE:
        print(f"{'!' * 50}\nSEARCH ENDED ON PAGE {pageNo}\n{'!' * 50}")
        break
    
    pageNo += 1

# Arrange data in a list
date_sentiment = []
dates = []

for date, sentiments in date_sentiments.items():
    dates.append(date)
    date_sentiment.append([date, round(sum(sentiments) / len(sentiments), 6)])

# Sort data according to date
sortedDates = sorted(dates)[::-1]  # From most recent to least recent
sortedSentiments = [None] * len(date_sentiment)

for i, date in enumerate(sortedDates):
    sortedSentiments[i] = date_sentiment[dates.index(date)]

# Output statistics
print(f"Number of Sentiments Collected:    {len(sortedSentiments): 6d}")
print(f"Total number of posts processed:   {totalPosts: 6d}")
print(f"Actual total number of posts:      {truePostCount: 6d}")
print(f"Post Collection Efficiency:        {totalPosts / truePostCount:.4f}")

# Generate sentiment csv file
sentimentDataframe = pd.DataFrame(sortedSentiments)
sentimentDataframe.columns = ["Date", "Sentiment"]  # Set columns

sentimentDataframe.to_csv(OUTPUT_DIR + STOCK_SYMBOL + "_sentiments.csv", index=False)  # Remove indexes in the csv file

