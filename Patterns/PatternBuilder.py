import sys
sys.path.insert(0, 'C:/Programming/HORUS-4.0')
from SetUp import *
from Data.DataHandler import DataHandler
from PatternClass import *

ticks = ["GBPJPY", "EURUSD"]
dhOBJ = DataHandler()

for tick in ticks:

    # testingData = dhOBJ.getRawData(tick, filter5m = True) # If not already built correctly
    # dhOBJ.saveDF(testingData, f"StockData/Raw/{tick}.csv") # If not already built correctly

    zoneData = dhOBJ.getDF(f"StockData/ZONE/{tick}.csv").iloc[:1000]
    print(zoneData)

    inZoneOBJ = inZone(zoneData, "1h", 'ematrTopBuy', 'ematrBottomBuy', 'ematrTopSell', 'ematrBottomSell', extendDF = True)
    print(inZoneOBJ.df)

    leaveZoneOBJ = LeaveZone(zoneData, "1h", inZoneOBJ.df, extendDF = True)
    print(leaveZoneOBJ.df)

    indicatorDF = pd.concat([zoneData, leaveZoneOBJ.df], axis = 1)

    print(indicatorDF)

    dhOBJ.saveDF(indicatorDF, "StockData/PATTERN/{}.csv".format(tick))