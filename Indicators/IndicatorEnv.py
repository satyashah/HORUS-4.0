import sys
sys.path.insert(0, 'C:/Programming/HORUS-4.0')
from SetUp import *

from Data.DataHandler import DataHandler
from Plotter import Plotter
from IndicatorClass import *

#Get RAW Data
tick = "GBPJPY"
dhOBJ = DataHandler()
rawData = dhOBJ.getDF(f"StockData/Raw/{tick}.csv").iloc[30000:50000]
# print(rawData)

#Build Class




#----------Call Class
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

#----------Test Class [Optimize as well]

# score, sampleSize, valDF = vwapOBJ.validate(rawData, "1h", atrDF, atrDistance = 1)
# print(round(score*100,3),"% \nSample Size:",sampleSize)
# print(valDF)


#----------Plot Class

pltOBJ = Plotter(rawData, "1h", volPlot= True)
pltOBJ.plot()

pltOBJ.plotLine(vpDF["poc"], color = "#CDEDF6")
pltOBJ.plotLine(vpDF["poc"]+atrDF["atr"], color = "#5EB1BF")
pltOBJ.plotLine(vpDF["poc"]-atrDF["atr"], color = "#EF7B45")

pltOBJ.plotLine(vwapDF["+2SD"], color = "#EF476F")
pltOBJ.plotLine(vwapDF["+SD"], color = "#FFD166")
pltOBJ.plotLine(vwapDF["vwap"], color = "#06D6A0")
pltOBJ.plotLine(vwapDF["-SD"], color = "#118AB2")
pltOBJ.plotLine(vwapDF["-2SD"], color = "#0A5770")

for index, anchors in pivotsDF.iterrows():
    pltOBJ.upArrow(index, color = "#5EB1BF") if anchors["type"] == "low" else pltOBJ.downArrow(index, color = "#EF7B45")


pltOBJ.show()


