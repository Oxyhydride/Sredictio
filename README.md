![SredictioImage](https://user-images.githubusercontent.com/25820201/69715400-246fa900-1143-11ea-91e1-7f9107c652a0.jpg)
A stock trading bot using sentiment analysis and reinforcement learning.

## What is this?
Sredictio is a stock trading bot that uses sentiment analysis and stock data to assist you in buying/selling stocks.

## What does Sredictio stand for?
Sredictio stands for ***S***tock P***redictio***n. 

## How did this get made?
Sredictio, at its core, is a A2C (a.k.a. [Advantage Actor Critic](https://sergioskar.github.io/Actor_critics/)) agent that has been trained against stock and sentiment data to come up with *actions* (buy, sell or hold) to maximise profit.

## How was the data obtained?
The stock data was obtained from [Yahoo Finance](https://finance.yahoo.com/)'s historical data section.

The sentiment data was obtained by using NLTK's VADER sentiment analysis tool (for what it can do, go [here](https://medium.com/analytics-vidhya/simplifying-social-media-sentiment-analysis-using-vader-in-python-f9e6ec6fc52f)) against the Straits Times' articles on a particular company.

## What's under `Extra Resources`?
The `Extra Resources` folder currently contains three spreadsheets. 

- `Sredictio Data Tracking.xlsx` is used to document all the tests done on the data and on the A2C agent. The spreadsheet currently contains 4 previous tests on the data and on the model.
- `Sredictio Field Tests.xlsx` documents the previous field tests. In the last field test, four stocks, Facebook (`FB`), Google/Alphabet Inc. (`GOOGL`), Boeing (`BA`) and ST Engineering (`S63.SI`), were used as benchmarks for the A2C agent.
- `Sredictio Update Plans.xlsx` is like a roadmap for Sredictio. It contains all past and future update plans for this Sredictio.

## Where's the model stored?
The latest model (and previous models) can be found under the `Models` directory.

The model is a `.zip` file, containing the parameters of the model.

For more on the model and its format, refer to [here](https://stable-baselines.readthedocs.io/en/master/guide/save_format.html) for more info.

## Update Log
- 2019-12-10: **Version 0.1.0: The Initial Update** was released.
- 2019-12-10: **Version 0.1.1** was released. It was an update to "[tidy] up the files in the repository".
- 2019-12-11: **Version 0.1.2** was released. It was "a hotfix for the update to `yahoo-fin`, which... [broke] the stock obtaining mechanism of Sredictio."
- 2019-12-20: **Version 0.2.0: The Quality of Life Update** was released.

## Credits
- Sredictio's Stock data taken from [Yahoo Finance](https://finance.yahoo.com/).
- Sredictio's Sentiment data scraped from [Straits Times](https://www.straitstimes.com/) articles.
- The cover image was taken from [pensoft.co.ke](https://www.pensoft.co.ke/stocks-backgrounds-ultra-hd/).

## Acknowledgements
We would like to thank OpenAI and DeepMind for sharing these open-source Deep Learning resources to us. Without them, AI research could be way behind our time.
