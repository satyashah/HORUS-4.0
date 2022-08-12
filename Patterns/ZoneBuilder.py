import sys
sys.path.insert(0, 'C:/Users/satya/Documents/Programming/HORUS-4.0')
from SetUp import *
from Data.DataHandler import DataHandler
from ZoneClass import *

ticks = ["GBPJPY", "EURUSD"]
dhOBJ = DataHandler()

for tick in ticks:

    # testingData = dhOBJ.getRawData(tick, filter5m = True) # If not already built correctly
    # dhOBJ.saveDF(testingData, f"StockData/Raw/{tick}.csv") # If not already built correctly

    indicatorData = dhOBJ.getDF(f"StockData/INDICATOR/{tick}.csv")
    print(indicatorData)

    zoneOBJ = EmaAtrZone(indicatorData["ema_20_1h_c"], indicatorData["atr_14_1h"])

    print(zoneOBJ.df)

    indicatorDF = pd.concat([indicatorData, zoneOBJ.df], axis = 1)

    print(indicatorDF)

    dhOBJ.saveDF(indicatorDF, "StockData/Zone/{}.csv".format(tick))