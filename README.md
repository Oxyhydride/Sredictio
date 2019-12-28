![Sredictio Cover Image](https://user-images.githubusercontent.com/25820201/69715400-246fa900-1143-11ea-91e1-7f9107c652a0.jpg)
A stock trading bot using sentiment analysis and reinforcement learning.

## What is this?
Sredictio is a stock trading bot that uses sentiment analysis and stock data to assist you in stock trading.

## What does Sredictio stand for?
Sredictio stands for ***S***tock P***redictio***n. 

## How did this get made?
Sredictio, at its core, is a A2C (a.k.a. [Advantage Actor Critic](https://sergioskar.github.io/Actor_critics/)) agent that has been trained against stock and sentiment data to come up with *actions* (buy, sell or hold) to maximise profit.

## How was the data obtained?
The OHLCV (which stands for Open, High, Low, Close and Volume) data was obtained from [Yahoo Finance](https://finance.yahoo.com/).

The sentiment data was obtained by running NLTK's VADER sentiment analysis tool (for what it can do, go [here](https://medium.com/analytics-vidhya/simplifying-social-media-sentiment-analysis-using-vader-in-python-f9e6ec6fc52f)) on the Straits Times' articles. The articles were on the stock itself.

## What's under the `Extras` directory?
The `Extras` folder currently contains three spreadsheets. 

- `Sredictio Data Tracking.xlsx` is used to document all the tests done on the data and on the A2C agent. The spreadsheet currently contains 4 previous tests on the data and on the model.
- `Sredictio Field Tests.xlsx` documents the previous field tests. In the last field test, four stocks, Facebook (`FB`), Google/Alphabet Inc. (`GOOGL`), Boeing (`BA`) and ST Engineering (`S63.SI`), were used as benchmarks for the A2C agent.
- `Sredictio Update Plans.xlsx` Sredictio's roadmap. It outlines past and future plans to develop Sredictio.

## Where's the model stored?
The latest model (and previous models) can be found under the `Models` directory.

The model is a `.zip` file, containing the parameters of the model.

For more on the model and its format, refer to [here](https://stable-baselines.readthedocs.io/en/master/guide/save_format.html) for more info.

## How do I use Sredictio?
### Training
To train the model, run the following command, replacing the parameters in "<>" with your own strings:

```
python Train.py <TRAINING DATA DIRECTORY> <STOCK THAT THE MODEL WOULD BE TRAINED ON> <STOCK THAT THE MODEL WOULD BE TESTED ON>
```

For example,
```
python Train.py "Training Data" AMZN BA
```
where `AMZN` is the "Training Stock" and `BA` is the "Testing Stock".

### Testing with Historical Data
To test the model with historical data, run the following command, replacing the parameters in "<>" with your own strings:

```
python "Test Sredictio.py" <MODEL DIRECTORY> <START DATE> <END DATE>
```

For instance, the following are valid commands:
```
python "Test Sredictio.py" Models 2019-01-01 2019-12-12
```
and

```
python "Test Sredictio.py" Models 2019-06-01 2019-06-30
```
but not

```
python "Test Sredictio.py" Models 2019-02-01 2019-01-01
```
or
```
python "Test Sredictio.py" Models 2019-01-01 2018-01-01
```

### Updating Training Data
To update Sredictio's training data, run `Update Training Data.py` **with no arguments**.

For example,
```
python "Update Training Data.py"
```

### Updating Sredictio
To update Sredictio, run `Update Sredictio.py` using the following command:
```
python "Update Sredictio.py"
```

## What if I found a bug?
If you find a bug in Sredictio, head over to [Sredictio's Issue Page](https://github.com/Ryan-Kan/Sredictio/issues) to post your bug. **Make sure that your bug hasn't been reported by someone else, though.**

If you want to see all **confirmed** issues in Sredictio, the `Bugtracker.txt` file will contain the information you need.

## Sredictio Update Log
- 2019-12-10: **Version 0.1.0: The Initial Update** was released.
- 2019-12-10: **Version 0.1.1** was released. It was an update to "[tidy] up the files in the repository".
- 2019-12-11: **Version 0.1.2** was released. It was "a hotfix for the update to `yahoo-fin`, which... [broke] the stock obtaining mechanism of Sredictio."
- 2019-12-20: **Version 0.2.0: The Quality of Life Update** was released.

## Credits
- Sredictio's Stock data taken from [Yahoo Finance](https://finance.yahoo.com/).
- Sredictio's Sentiment data scraped from [Straits Times](https://www.straitstimes.com/) articles.
- Sredictio's cover image's background was taken from [pensoft.co.ke](https://www.pensoft.co.ke/stocks-backgrounds-ultra-hd/).

## Acknowledgements
We would like to thank OpenAI and DeepMind for sharing these open-source Deep Learning resources to us. Without them, AI research could be way behind our time.
