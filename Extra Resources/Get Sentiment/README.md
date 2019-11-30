# Get Sentiment
This README file will explain how I obtained the sentiment data. The code can be found under `GetSentiment.py`.

## Game Plan
This was my plan for getting the sentiment data:
1. Scrape news articles about a certain company / stock
2. Generate sentiment values from each article
3. Place the sentiment values in a `.csv` file for easier parsing for the main model.

## Sentiment Source
I decided to use the [Straits Times](https://www.straitstimes.com/) as a base for scraping articles.

After toying around with the Straits Times' search function, I found out that the website had obtained all of its articles from `api.queryly.com`. Exploring the page for a bit, I found out that the articles were placed in a giant dictionary.

![AllTheArticles](https://user-images.githubusercontent.com/25820201/69646788-60533180-10a3-11ea-9ab2-6e38e1617f19.png)

From there, I could just run a simple `urllib.request.urlopen` request to obtain the articles' data.

There were two pieces of data that was important:
- The article's title (e.g. Bitcoin almost wipes out its mega gain as it came)
- The description of the article. This usually contains the first few sentences of the article, which will be useful for sentiment analysis.

## Sentiment Analysis
For sentiment analysis, I opted for NLTK's VADER sentiment analysis tool. This is because:
1. It was fast to implement
2. It didn't need to be trained before deployment
3. It was curated by humans

For the overall sentiment of the article, I decided to take the average of the title and the description. My reason for doing this is because the title is the "summary" of the article, and by proxy the sentiment of the title should be the "summary" of the sentiment of the article. The description was equally as important. What people want to read first is the most important details. Thus, the first few lines of the article was also very important when deciding the article's overall sentiment.

After all the articles for that particular day was compiled, I simply took the average of all of them. Doing this yields a list of date-sentiment pairs.

## Sentiment Deployment
After getting the date-sentiment pairs, I used `pandas` to export the list as a `.csv` file, which would be placed in the output folder.

This `.csv` file would later be placed in the `StockData` folder for model training.
