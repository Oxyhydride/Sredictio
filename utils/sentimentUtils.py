"""
sentimentUtils.py
Version 3.1.1

Created on 2019-04-29
Updated on 2019-12-06

Copyright Ryan Kan

Description: A program to scrap sentiments from the Straits Times' website and generate the {NAME}_Sentiments.csv file
             for model training.
"""

# IMPORTS
import json
import time
from datetime import datetime
from urllib.request import Request, urlopen

import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from utils.miscUtils import natural_sort


# FUNCTIONS
def get_sentiment(stock_symbol: str, stock_name: str, end_date: str, output_dir: str = "./trainingData/",
                  batch_size: int = 20, time_offset: int = 8, irrelevant_post_tolerance: int = 20, to_csv: bool = True,
                  verbose: bool = True):
    """
    Generate sentiment data given stock data.

    Keyword arguments:
    - stock_symbol, str: Stock symbol. E.g. FB, TSLA, AMZN
    - stock_name, str: Stock name. E.g. Facebook, Tesla, Amazon
    - end_date, str: Date to stop scraping. Must be in the form YYYY-MM-DD.
    - output_dir, str: Directory to place the .csv file. (Default = "./trainingData/")
    - batch_size, int: Batch size of the website. Must be in the range 1 <= batch_size < 100 (Default = 20)
    - time_offset, int: Timezone offset. E.g. if timezone is GMT+6 / UTC+6, time_offset will be 6. (Default = 8)
    - irrelevant_post_tolerance, int: How many irrelevant posts to process before halting? (Default = 20)
    - to_csv, bool: Should the sentiment data be placed in a csv file? (Default = True)
    - verbose, bool: Should the program show intermediate output? (Default = True)
    """
    sia = SentimentIntensityAnalyzer()  # The VADER sentiment analyser
    hours_to_search = (datetime.today() - datetime.strptime(end_date, "%Y-%m-%d")).days * 24

    # Search for articles and generate sentiment
    page_no = 1
    date_sentiments = {}

    irrelevant_posts = 0
    total_posts = 0

    while True:
        if verbose:
            print(f"\n{'-' * 50}\nPAGE {page_no}\n{'-' * 50}")

        time.sleep(0.1)  # We don't want to overload the website, right?

        page_url = f"http://api.queryly.com/json.aspx?queryly_key=a7dbcffb18bb41eb&query={'%20'.join(stock_name.lower().split())}&endindex={(page_no - 1) * batch_size}&batchsize={batch_size}&timezoneoffset={time_offset}&facetedvalue={hours_to_search}&facetedkey=pubDate"
        header = {'User-Agent': 'Mozilla/5.0'}  # Do not modify!
        request = Request(page_url, headers=header)

        page = urlopen(request).read()  # Returns the articles from the straits times

        page_data = str(page, "UTF-8")
        page_dict = json.loads(page_data)  # Hilariously, the articles are arranged in a dictionary

        all_posts = page_dict["items"]  # All the articles on the page can be found here

        for post in all_posts:
            post_title = post["title"]  # The title of the article
            post_desc = post["description"]  # The description of the article
            post_unix = post["pubdateunix"]  # Unix time of when the article was posted

            if ((post_title.lower().find(stock_name.lower()) != -1) and (post_desc.lower().find(
                    stock_name.lower()) != -1)):  # If the stock's name is found in the title and the description
                irrelevant_posts = 0
                post_date = datetime.fromtimestamp(post_unix).strftime("%Y-%m-%d")

                sentiment_title = sia.polarity_scores(post_title)['compound']  # Take the sentiment of the title
                sentiment_desc = sia.polarity_scores(post_desc)['compound']  # Take the sentiment of the description

                if verbose:
                    print("\n\n" + post_date + ": " + post_title + "\n" + post_desc)
                    print(f"\nSENTIMENTS\nTITLE: {sentiment_title:.6f} | DESCRIPTION: {sentiment_desc:.6f}")

                if post_date not in date_sentiments.keys():  # If an article on that date has yet to be processed
                    date_sentiments[post_date] = []  # Make a new list

                avg_sentiment = (sentiment_title + sentiment_desc) / 2
                date_sentiments[post_date].append(avg_sentiment)

                total_posts += 1

            else:
                irrelevant_posts += 1

        if irrelevant_posts > irrelevant_post_tolerance:
            if verbose:
                print(f"{'!' * 50}\nSEARCH ENDED ON PAGE {page_no}\n{'!' * 50}")

            break

        page_no += 1

    # Arrange data in a list
    date_sentiment_arr = []
    dates = []

    for date, sentiments in date_sentiments.items():
        dates.append(date)
        date_sentiment_arr.append([date, round(sum(sentiments) / len(sentiments), 6)])

    # Sort data according to date
    sorted_dates = natural_sort(dates)[::-1]  # From most recent to least recent
    sorted_sentiments = list([0] * len(dates))

    # Sort sentiment according to date
    for i, date in enumerate(dates):
        sorted_sentiments[sorted_dates.index(date)] = date_sentiment_arr[i]

    # Generate sentiment csv file
    sentiment_dataframe = pd.DataFrame(sorted_sentiments)
    sentiment_dataframe.columns = ["Date", "Sentiment"]  # Set the columns

    if to_csv:
        sentiment_dataframe.to_csv(output_dir + stock_symbol + "_sentiments.csv", index=False)

    else:
        return sentiment_dataframe


if __name__ == "__main__":
    # Debugging
    sentimentDF = get_sentiment("FB", "Facebook", "2019-11-20", to_csv=False)
    print(sentimentDF)
