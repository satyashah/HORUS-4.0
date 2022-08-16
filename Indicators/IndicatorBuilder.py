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

    rawData = dhOBJ.getDF(f"StockData/Raw/{tick}.csv").iloc[:]
    print(rawData)

    pivotsOBJ = pivots(rawData, "1h", 15, extendDF=False)
    pivotsDF = pivotsOBJ.df


    atrOBJ = atr(rawData, "1h", 14)
    atrDF = atrOBJ.df


    emaOBJ = ema(rawData, "c", "1h", 20)
    emaOBJ.df

    vpOBJ = vp(rawData, pivotsDF["peak"], "1h", "5m", 15, 4, fastRefresh = False)
    vpDF = vpOBJ.df

    vwapOBJ = vwap(rawData, pivotsDF["peak"], "1h", 15, 4, "hlc3", keep="all")
    vwapDF = vwapOBJ.df
    

    indicatorDF = pd.concat([rawData,  atrOBJ.df, emaOBJ.df, vpOBJ.df, vwapOBJ.df], axis = 1)

    print(indicatorDF)

    dhOBJ.saveDF(indicatorDF, "StockData/Indicator/{}.csv".format(tick))

