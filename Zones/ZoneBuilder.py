import sys
sys.path.insert(0, 'C:/Programming/HORUS-4.0')
from SetUp import *
from Data.DataHandler import DataHandler
from IndicatorClass import *

ticks = ["GBPJPY", "EURUSD"]
dhOBJ = DataHandler()

for tick in ticks:

    # testingData = dhOBJ.getRawData(tick, filter5m = True) # If not already built correctly
    # dhOBJ.saveDF(testingData, f"StockData/Raw/{tick}.csv") # If not already built correctly

    rawData = dhOBJ.getDF(f"StockData/Raw/{tick}.csv")
    print(rawData)

    emaOBJ = ema(rawData, "c", "1d", 20)

    atrOBJ = atr(rawData, "1h", 14)

    print(emaOBJ.df)
    print(atrOBJ.df)

    indicatorDF = pd.concat([rawData, emaOBJ.df, atrOBJ.df], axis = 1)

    print(indicatorDF)

    dhOBJ.saveDF(indicatorDF, "StockData/Indicator/{}.csv".format(tick))