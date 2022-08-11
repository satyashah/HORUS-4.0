import sys
sys.path.insert(0, 'C:/Programming/HORUS-4.0')
from SetUp import *

from Data.DataHandler import DataHandler
from Plotter import Plotter

#Get RAW Data
tick = "GBPJPY"
dhOBJ = DataHandler()
indicatorData = dhOBJ.getDF(f"StockData/INDICATOR/{tick}.csv").iloc[:5000]
print(indicatorData)

#Build Class

class EmaAtrZone:
    """
    Enter an ema and atr, the zone is the area between
    zoneType -- "flexible" [only a high or low have to be in the zone], "partial" [the open/close must be in the candle], "absolute" [the entire candle must be in the zone], "topFlex"/"bottomFlex" [Can have high/low leave from the area that is flexible]
    """
    def __init__(self, emaDF, atrDF, name = "ematr") -> None:
        self.name = name
        self.df = self.buildZone(emaDF, atrDF)

    def buildZone(self, emaDF, atrDF):
        zoneArr = []
        for date in emaDF.index.values:
            curEma = emaDF.loc[date]
            curAtr = atrDF.loc[date]

            #Top, Bottom
            sellRange = [curEma, curEma-curAtr]
            buyRange = [curEma+curAtr, curEma]
            

            zoneArr.append([date, sellRange[0], sellRange[1], buyRange[0], buyRange[1]])

        zoneDF = pd.DataFrame(zoneArr, columns=["date", f"{self.name}TopBuy", f"{self.name}BottomBuy", f"{self.name}TopSell", f"{self.name}BottomSell"]).set_index("date")
        return zoneDF

        

    
        
        



#----------Call Class

zoneOBJ = EmaAtrZone(indicatorData["EMA_20"], indicatorData["atr_14"])
zoneDF = zoneOBJ.df
print(zoneDF)


print(zoneDF[["ematrTopBuy", "ematrBottomBuy"]])




#----------Test Class [Optimize as well]




#----------Plot Class

pltOBJ = Plotter(indicatorData, "1h")

pltOBJ.plot()

# pltOBJ.plotLine(indicatorData["EMA_20"], color="yellow")
# pltOBJ.plotLine(indicatorData["EMA_20"]+indicatorData["atr_14"], color="lime")
# pltOBJ.plotLine(indicatorData["EMA_20"]-indicatorData["atr_14"], color="pink")

pltOBJ.shadeArea(zoneDF[["ematrTopBuy", "ematrBottomBuy"]], 0.3, 'lime')
pltOBJ.shadeArea(zoneDF[["ematrTopSell", "ematrBottomSell"]], 0.3, 'pink')
# plt.fill_between(x, y1, y2, where=(y1 > y2), color='C0', alpha=0.3)


# for index, trade in valDF.iterrows():
#     color = "green" if trade["success"] else "red"
#     pltOBJ.upArrow(trade["lastDate"], color = color) if trade["lastEvent"] == "touchLower" else pltOBJ.downArrow(trade["lastDate"], color = color)
#     pltOBJ.upArrow(trade["curDate"], color = color) if trade["curEvent"] == "touchLower" else pltOBJ.downArrow(trade["curDate"], color = color)


pltOBJ.show()