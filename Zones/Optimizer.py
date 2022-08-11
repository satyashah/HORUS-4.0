from random import sample
import sys
sys.path.insert(0, 'C:/Programming/HORUS-4.0')
from SetUp import *

from Data.DataHandler import DataHandler
from Indicators.IndicatorClass import *
from Plotter import Plotter

print("=============================Optimizing EMA=============================")
#Get Data

ticks = ["GBPJPY", "EURUSD"]
dhOBJ = DataHandler()

for tick in ticks:
    testingData = dhOBJ.getRawData(tick, filter5m = False)
    dhOBJ.saveDF(testingData, f"StockData/Raw/{tick}.csv")
    rawData = dhOBJ.getDF(f"StockData/Raw/{tick}.csv")
    print(rawData)

#Input Arrays
ohlcvTypeArr = ['c', 'h', 'l']
timePeriodArr = ['1d', '1h']
lengthArr = [20, 30, 50, 100, 150, 200]

allInputArrays = [ohlcvTypeArr, timePeriodArr, lengthArr]

allCombos = list(itertools.product(*allInputArrays))

print(len(allCombos))


# Cycle through each Combo and add info to array
start = time.time()
print(start)

optArr = []

#   Helpers


for combo in allCombos[:]:
    print(combo)
    score, sampleSize = 0, 0

    for tick in ticks:
        rawData = dhOBJ.getDF(f"StockData/Raw/{tick}.csv")
        atrOBJ = atr(rawData, "1h", 14)
        emaOBJ = ema(rawData, combo[0], combo[1], combo[2])
        tickScore, error, tickSampleSize, valDF = emaOBJ.validate(rawData, "1h", atrOBJ.df)
        score += tickScore
        sampleSize += tickSampleSize

        print(tick, score, sampleSize, tickScore, tickSampleSize)

    optArr.append([score, sampleSize, combo[0], combo[1], combo[2]])

    end = time.time()
    print(round(end - start,0), "seconds")


optDF = pd.DataFrame(optArr, columns=["score", "sampleSize", "ohlcData", "timePeriod", "length"])
optDF.to_csv("ema_optimized2.csv")

end = time.time()
print(round(end - start,0), "seconds")