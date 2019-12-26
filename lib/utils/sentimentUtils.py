"""
sentimentUtils.py

Created on 2019-04-29
Updated on 2019-12-16

Copyright Ryan Kan 2019

Description: A program to scrap sentiments from the Straits Times' website and generate the {NAME}_sentiments.csv file
             or a sentiment dataframe for model training.
"""

# IMPORTS
import json
import time
from datetime import datetime
from urllib.request import Request, urlopen

import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from lib.utils.miscUtils import natural_sort


# FUNCTIONS
def get_sentiment_data(stock_symbol, stock_name, start_date, end_date, batch_size=20, verbose=True,
                       time_offset=8, irrelevant_post_tolerance=20, save_as_csv=False, output_dir=None):
    """
    Obtains sentiment data from Straits Times' articles on the company.

    NOTE: If `to_csv` is True, then:
    - The output directory is `output_dir`
    - The file name of the output file will be {`stock_symbol`}_sentiments.csv

    Args:
        stock_symbol (str): Stock symbol. Also known as the Stock ticker.
                            For example, "FB", "TSLA" and "AMZN" are all valid stock symbols.

        stock_name (str): The name of the stock.

                          For example, "Facebook", "Tesla" and "Amazon" are all valid stock
                          names.

        start_date (str): The first date to scrape the data. Note that the start date has to be
                          OLDER than the end date.

                          Note that the date has to be in the form YYYY-MM-DD.

        end_date (str): The last date to scrape the data. Note that the end date has to be MORE
                        RECENT than the start date.

                        The end date has to be in the form YYYY-MM-DD.

        batch_size (int): Batch size for each page on the Straits Times' website. (Default = 20)

                          Note that the value of `batch_size` must be in the following range:
                                                1 <= batch_size < 100

        verbose (bool): Should the program show intermediate output? (Default = True)

        time_offset (int): The timezone offset. (Default = 8)

                           For example, if the timezone is GMT+6 / UTC+6, the `time_offset` will
                           be 6.

        irrelevant_post_tolerance (int): How many irrelevant posts to process before stopping?
                                         (Default = 20)

                                         An `irrelevant` post refers to a post which does not
                                         contain the `stock_name` in its title OR its description.

                                         As soon as `irrelevant_post_tolerance` irrelevant posts have
                                         been observed consecutively, the program will automatically
                                         halt and output the sentiment dataframe.

        save_as_csv (bool): Should the sentiment data be placed in a csv file? (Default = True)

        output_dir (str): Directory to place the .csv file. (Default = None)

                          This parameter is only required if `save_as_csv = True`.

    Returns:
        pd.DataFrame: Dataframe of the sentiment data. Will only return if `to_csv = True`.

    Raises:
        AssertionError: If the value of `batch_size` does not fall in the range
                        `1 <= batch_size < 100`

    """

    # Data validation checks
    assert 1 <= batch_size < 100, "Batch size has to be in the range `1 <= batch_size < 100`."

    # Generate sentiment analyser
    sia = SentimentIntensityAnalyzer()  # The VADER sentiment analyser

    # Calculate the oldest allowed article to be searched (i.e. find the `age` of the oldest article)
    oldest_article_age = (datetime.today() - datetime.strptime(start_date, "%Y-%m-%d")).days * 24  # Age is in hours

    # Search for relevant articles
    page_no = 1
    date_sentiments = {}

    irrelevant_posts = 0
    total_posts = 0

    while True:
        if verbose:
            print("-" * 50)
            print(f"PAGE {page_no}".center(50))
            print("-" * 50)

        time.sleep(0.1)  # Wait for 0.1s to not overload the website

        # Generate the URL
        page_url = f"http://api.queryly.com/json.aspx?" + \
                   f"queryly_key=a7dbcffb18bb41eb" + \
                   f"&query={'%20'.join(stock_name.lower().split())}" + \
                   f"&endindex={(page_no - 1) * batch_size}" + \
                   f"&batchsize={batch_size}" + \
                   f"&timezoneoffset={time_offset}" + \
                   f"&facetedvalue={oldest_article_age}" + \
                   f"&facetedkey=pubDate"

        header = {'User-Agent': 'Mozilla/5.0'}  # This is Macintosh's browser header
        request = Request(page_url, headers=header)

        page = urlopen(request).read()  # Returns the articles from the Straits Times

        page_data = str(page, "UTF-8")  # Returns a JSON dictionary

        # Get articles from JSON dictionary
        page_dict = json.loads(page_data)  # Load `page_data` as a dictionary

        all_posts = page_dict["items"]  # All the articles on the page can be found here

        # Iterate through posts to generate sentiment
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
                    print(f"\nTITLE: {sentiment_title:.6f} | DESCRIPTION: {sentiment_desc:.6f}")

                if post_date not in date_sentiments.keys():
                    date_sentiments[post_date] = []  # Make a new list for sentiments

                # Calculate sentiment for that article
                avg_sentiment = (sentiment_title + sentiment_desc) / 2

                # Add article's sentiment to that date's sentiments
                date_sentiments[post_date].append(avg_sentiment)

                total_posts += 1

            else:
                # Post was not relevant, so increment `irrelevant_posts` by 1
                irrelevant_posts += 1

        # Check if the current page's posts are no longer relevant
        if irrelevant_posts > irrelevant_post_tolerance:
            if verbose:
                print("!" * 50)
                print(f"SEARCH ENDED ON PAGE {page_no}".center(50))
                print("!" * 50)

            break

        page_no += 1

    # Organise sentiments according to date
    date_sentiment_arr = []  # Each element would be a [str, float] list
    dates = []  # This is for date sorting later

    for date, sentiments in date_sentiments.items():
        dates.append(date)
        date_sentiment_arr.append([date, round(sum(sentiments) / len(sentiments), 6)])

    # Sort dates
    sorted_dates = natural_sort(dates)[::-1]  # From most recent to least recent

    # Sort sentiment according to the sorted dates
    sorted_sentiments = list([0] * len(dates))

    for i, date in enumerate(dates):
        sorted_sentiments[sorted_dates.index(date)] = date_sentiment_arr[i]

    # Create the sentiment dataframe
    sentiment_dataframe = pd.DataFrame(sorted_sentiments)
    sentiment_dataframe.columns = ["Date", "Sentiment"]  # Set the columns to be "Date" and "Sentiment"

    # Set all values in the Date column to be `pd.Timestamp`s
    sentiment_dataframe["Date"] = pd.to_datetime(sentiment_dataframe["Date"])

    # Convert both `start_date` and `end_date` to `datetime.datetime`
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Make a boolean mask to find the relevant dates
    mask = (sentiment_dataframe["Date"] >= start_date) & (sentiment_dataframe["Date"] <= end_date)

    # Select all the relevant rows
    sentiment_dataframe = sentiment_dataframe.loc[mask]

    # Output the compiled dataframe
    if save_as_csv:
        sentiment_dataframe.to_csv(output_dir + stock_symbol + "_sentiments.csv", index=False)

    else:
        # Just return the dataframe as a `pd.DataFrame`
        return sentiment_dataframe


# DEBUG CODE
if __name__ == "__main__":
    # Ask for user input
    stockName = input("Please enter the stock name: ")
    stockSymbol = input("Please enter the stock symbol: ")
    outputAsFile = input("Should the output be a .csv file? [Y]es or [N]o: ") == ("Y" or "Yes")

    print("\nFor the ENDING date, ensure that it is MORE RECENT than the STARTING date.")
    startDate = input("Please enter the starting date in the form YYYY-MM-DD: ")
    endDate = input("Please enter the ending date in the form YYYY-MM-DD:   ")

    # Get the sentiment dataframe
    sentimentDF = get_sentiment_data(stockSymbol, stockName, startDate, endDate, save_as_csv=outputAsFile,
                                     output_dir="../../Training Data/" + stockSymbol + "/")

    # Output
    if not outputAsFile:
        print(sentimentDF)

    else:
        print("Done!")
