![SredictioImage](https://user-images.githubusercontent.com/25820201/69715400-246fa900-1143-11ea-91e1-7f9107c652a0.jpg)
A stock trading bot using sentiment analysis and reinforcement learning.

## What is this?
Sredictio is a stock trading bot that uses sentiment analysis and stock data to assist you in buying/selling stocks.

## What does Sredictio stand for?
Sredictio stands for ***S***tock P***redictio***n. 

## How did this get made?
Sredictio, at its core, is a A2C ([Advantage Actor Critic](https://sergioskar.github.io/Actor_critics/)) agent that has been trained against stock and sentiment data to come up with *actions* (buy, sell or hold) to maximise profit.

## How did you obtain the data?
The stock data was obtained from [Yahoo Finance](https://finance.yahoo.com/)'s historical data section.

The sentiment data was obtained by using NLTK's VADER sentiment analysis tool (for what it can do, go [here](https://medium.com/analytics-vidhya/simplifying-social-media-sentiment-analysis-using-vader-in-python-f9e6ec6fc52f)) against the Straits Times' articles on a particular company.

## What's with the spreadsheet?
`Sredictio Data Tracking.xlsx` is an excel spreadsheet used to document all the tests done on the data and on the A2C agent.


## Where's the model stored?
The model is saved as a `.zip` file in the main directory. It currently is named `Model_LBW-5_NOI-100000.zip`.

For more on the model, refer to [here](https://stable-baselines.readthedocs.io/en/master/guide/save_format.html) for more info.

## Credits
- Stock data taken from [Yahoo Finance](https://finance.yahoo.com/).
- Sentiment data scraped from [Straits Times](https://www.straitstimes.com/) articles.
- Cover image taken from [pensoft.co.ke](https://www.pensoft.co.ke/stocks-backgrounds-ultra-hd/).

## Acknowledgements
- Thanks to OpenAI and DeepMind for sharing these open-source Deep Learning resources to us!
