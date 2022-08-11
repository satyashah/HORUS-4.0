from DataHandler import DataHandler


dataHandlerObj = DataHandler()

tickers = ["GBPJPY", "EURUSD"]
for tick in tickers:
    print(DataHandler.__doc__)
    rawTickDF = dataHandlerObj.getRawData(tick)
    print(rawTickDF)
    dataHandlerObj.saveDF(rawTickDF, f"StockData/RAW/{tick}.csv")