import sys
sys.path.insert(0, 'C:/Programming/HORUS-4.0')
from SetUp import *


class EmaAtrZone:
    """
    Enter an ema and atr, the zone is the area between
    

    Plotter:
        pltOBJ.shadeArea(zoneDF[["ematrTopBuy", "ematrBottomBuy"]], 0.3, 'lime')
        pltOBJ.shadeArea(zoneDF[["ematrTopSell", "ematrBottomSell"]], 0.3, 'pink')

        for index, trade in valDF.iterrows():
            color = "green" if trade["success"] else "red"
            pltOBJ.upArrow(trade["lastDate"], color = color) if trade["side"] == "long" else pltOBJ.downArrow(trade["lastDate"], color = color)
            # pltOBJ.upArrow(trade["curDate"], color = color) if trade["side"] == "long" else pltOBJ.downArrow(trade["curDate"], color = color)

            if trade["success"]:
                pltOBJ.plotSingleLine(trade["lastDate"], trade["curDate"], startAnchor="close", endAnchor="high", color = color, ls="dotted") if trade["side"] == "long" else pltOBJ.plotSingleLine(trade["lastDate"], trade["curDate"], startAnchor="close", endAnchor="low", color = color, ls="dotted")
            else:
                pltOBJ.plotSingleLine(trade["lastDate"], trade["curDate"], startAnchor="close", endAnchor="low", color = color, ls="dotted") if trade["side"] == "long" else pltOBJ.plotSingleLine(trade["lastDate"], trade["curDate"], startAnchor="close", endAnchor="high", color = color, ls="dotted")
    
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

        
    def validate(self, indicatorData, testPeriod, atrDF, atrDistance = 1):
        dataDF = self.getData(indicatorData, testPeriod)

        crossArr = []

        for barIndex in range(1, len(dataDF)):
            
            lastCandle = dataDF.iloc[barIndex-1]
            curCandle = dataDF.iloc[barIndex]

            lastRange = self.df.loc[lastCandle.name]
            curRange = self.df.loc[curCandle.name]

            curAtr = atrDF.loc[curCandle.name]

            if not pd.isna(lastRange["ematrTopBuy"]):

                longSignal = lastCandle["c"] < lastRange["ematrTopBuy"] and curCandle["c"] > curRange["ematrTopBuy"]
                shortSignal = lastCandle["c"] > lastRange["ematrBottomSell"] and curCandle["c"] < curRange["ematrBottomSell"]
                
                longSL = curRange["ematrBottomBuy"]
                shortSL = curRange["ematrTopSell"]

                longTP = curRange["ematrTopBuy"] + atrDistance*curAtr
                shortTP = curRange["ematrBottomSell"] - atrDistance*curAtr
                crossArr.append([curCandle.name, longSignal, shortSignal, longSL, shortSL, longTP, shortTP])
            
            else:
                crossArr.append([np.nan]*6)

        crossDF = pd.DataFrame(crossArr, columns=['date', 'longSignal', 'shortSignal', 'longSL', 'shortSL', 'longTP', 'shortTP']).set_index("date")

        crossDF.to_csv("check.csv")
        valScoreArr = []

        buysDF = crossDF[crossDF["longSignal"]==True]

        for index, buyInfo in buysDF.iterrows():
            
            testDF = dataDF.loc[index:].iloc[1:]
            tpIndex = testDF[testDF["h"]>buyInfo["longTP"]].index
            slIndex = testDF[testDF["l"]<buyInfo["longSL"]].index

            if len(slIndex) == 0 and len(tpIndex) != 0:
                valScoreArr.append([True, "long", index, tpIndex[0]])
            if len(slIndex) != 0 and len(tpIndex) == 0:
                valScoreArr.append([False, "long", index, slIndex[0]])
            if len(tpIndex) != 0 and len(slIndex) != 0:
                if tpIndex[0] < slIndex[0]:
                    exitPrice = testDF.loc[tpIndex[0]]
                    valScoreArr.append([True, "long", index, tpIndex[0]])
                else:
                    exitPrice = testDF.loc[slIndex[0]]
                    valScoreArr.append([False, "long", index, slIndex[0]])
        

        sellsDF = crossDF[crossDF["shortSignal"]==True]

        for index, sellInfo in sellsDF.iterrows():
            
            testDF = dataDF.loc[index:].iloc[1:]
            tpIndex = testDF[testDF["l"]<sellInfo["shortTP"]].index
            slIndex = testDF[testDF["h"]>sellInfo["shortSL"]].index

            if len(slIndex) == 0 and len(tpIndex) != 0:
                valScoreArr.append([True, "short", index, tpIndex[0]])
            if len(slIndex) != 0 and len(tpIndex) == 0:
                valScoreArr.append([False, "short", index, slIndex[0]])
            if len(tpIndex) != 0 and len(slIndex) != 0:
                if tpIndex[0] < slIndex[0]:
                    valScoreArr.append([True, "short", index, tpIndex[0]])
                else:
                    valScoreArr.append([False, "short", index, slIndex[0]])

        valDF = pd.DataFrame(valScoreArr, columns=["success", "side", "lastDate", "curDate"])
        score = sum(valDF["success"].values)/len(valDF["success"].values) if len(valDF["success"].values)>0 else 0
            
        return score, len(valDF["success"].values), valDF

    def getData(self, rawData, timePeriod):
        period = str(timePeriod[1:])
        dataCSV = rawData[[period+'open', period+'high', period+'low', period+'close', period+'volume']].dropna()
        dataCSV.columns = ['o', 'h', 'l', 'c', 'v']
        return dataCSV
