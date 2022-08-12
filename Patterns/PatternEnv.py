import sys
sys.path.insert(0, 'C:/Users/satya/Documents/Programming/HORUS-4.0')
from SetUp import *

from Data.DataHandler import DataHandler
from Plotter import Plotter

#Get RAW Data
tick = "GBPJPY"
dhOBJ = DataHandler()
zoneData = dhOBJ.getDF(f"StockData/ZONE/{tick}.csv").iloc[:5000]
print(zoneData)

#Build Class

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
        
class LeaveZone:
    """
    When Value leaves Zone
    """
    def __init__(self, zoneData, timePeriod, buyZoneTop, buyZoneBottom, sellZoneTop, sellZoneBottom, name = "leaveZone") -> None:
        
        tbz = zoneData[buyZoneTop]
        bbz = zoneData[buyZoneBottom]
        tsz = zoneData[sellZoneTop]
        bsz = zoneData[sellZoneBottom]

        selectData = self.getData(zoneData, timePeriod)

    def getData(self, rawData, timePeriod):
        period = str(timePeriod[1:])
        dataCSV = rawData[[period+'open', period+'high', period+'low', period+'close', period+'volume']].dropna()
        dataCSV.columns = ['o', 'h', 'l', 'c', 'v']
        return dataCSV
  
    def getLeaveZoneDF(self, selectData, tbz, bbz, tsz, bsz):
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

class inZone:
    """
    Enter top zone type and bottom zone type
                Top      Bottom
    flexible => hc|l    h|cl
    partial =>  h|cl    hc|l
    absolute => |hcl    hcl|

    """
    def __init__(self, zoneData, timePeriod,  buyZoneTopCol, buyZoneBottomCol, sellZoneTopCol, sellZoneBottomCol, **kwargs) -> None:
        
        buyZoneTopType = kwargs["buyZoneTopType"] if "buyZoneTopType" in kwargs else "partial"
        buyZoneBottomType = kwargs["buyZoneBottomType"] if "buyZoneBottomType" in kwargs else "absolute"
        sellZoneTopType = kwargs["sellZoneTopType"] if "sellZoneTopType" in kwargs else "absolute"
        sellZoneBottomType = kwargs["sellZoneBottomType"] if "sellZoneBottomType" in kwargs else "partial"

        selectData = self.getData(zoneData, timePeriod)
        
        inRangeArr = []

        for index, candleInfo in selectData.iterrows():
            barInfo = zoneData.loc[candleInfo.name]

            buyZoneTop = barInfo[buyZoneTopCol]
            buyZoneBottom = barInfo[buyZoneBottomCol]
            sellZoneTop = barInfo[sellZoneTopCol]
            sellZoneBottom = barInfo[sellZoneBottomCol]

            inBuyRange = self.inRange(candleInfo, buyZoneTop, buyZoneBottom, buyZoneTopType, buyZoneBottomType)
            inSellRange = self.inRange(candleInfo, sellZoneTop, sellZoneBottom, sellZoneTopType, sellZoneBottomType)

            inRangeArr.append([index, inBuyRange, inSellRange])

        df = pd.DataFrame(inRangeArr, columns=["index", "inBuyRange", "inSellRange"]).set_index("index")

        self.df = self.extendDF(zoneData, df)

    def inRange(self, barInfo, topZone, bottomZone, topZoneType, bottomZoneType):
        
        
        if topZoneType == "flexible":
            inTopZone = topZone > barInfo["l"]
        if topZoneType == "absolute":
            inTopZone = topZone > barInfo["h"]
        if topZoneType == "partial":
            inTopZone = topZone > barInfo["c"]

        if bottomZoneType == "flexible":
            inBottomZone = barInfo["h"] > bottomZone
        if bottomZoneType == "absolute":
            inBottomZone = barInfo["l"] > bottomZone
        if bottomZoneType == "partial":
            inBottomZone = barInfo["c"] > bottomZone
        
        return inTopZone and inBottomZone

    def getData(self, rawData, timePeriod):
        period = str(timePeriod[1:])
        dataCSV = rawData[[period+'open', period+'high', period+'low', period+'close', period+'volume']].dropna()
        dataCSV.columns = ['o', 'h', 'l', 'c', 'v']
        return dataCSV

    def extendDF(self, master, minor):
        minorCols = list(minor.columns.values)

        newMinor = pd.DataFrame(columns=minorCols, index=list(master.index.values))

        for index in range(1, len(minor.index.values)):
            lastMinor = minor.iloc[index-1]
            curMinor = minor.iloc[index]

            newMinor[(newMinor.index>=lastMinor.name) & (newMinor.index<curMinor.name)] = list(lastMinor.values) #EXTEND TO LAST DAY!!

        return newMinor


#----------Call Class

inZoneOBJ = inZone(zoneData, "1h", 'ematrTopBuy', 'ematrBottomBuy', 'ematrTopSell', 'ematrBottomSell')
print(inZoneOBJ.__doc__)

print(inZoneOBJ.df)

# patternOBJ = LeaveZone(zoneData, "1h", 'ematrTopBuy', 'ematrBottomBuy', 'ematrTopSell', 'ematrBottomSell')
# zoneDF = zoneOBJ.df
# print(zoneDF)


# print(zoneDF[["ematrTopBuy", "ematrBottomBuy"]])

# score, sampleSize, valDF = zoneOBJ.validate(indicatorData, "1h", indicatorData["atr_14"], atrDistance= 2)

# print(valDF)
# print(score, sampleSize)


#----------Test Class [Optimize as well]




#----------Plot Class

# pltOBJ = Plotter(zoneData, "1h")

# pltOBJ.plot()

# pltOBJ.shadeArea(zoneData[["ematrTopBuy", "ematrBottomBuy"]], 0.3, 'lime')
# pltOBJ.shadeArea(zoneData[["ematrTopSell", "ematrBottomSell"]], 0.3, 'pink')


# for index, trade in valDF.iterrows():
#     color = "green" if trade["success"] else "red"
#     pltOBJ.upArrow(trade["lastDate"], color = color) if trade["side"] == "long" else pltOBJ.downArrow(trade["lastDate"], color = color)
#     # pltOBJ.upArrow(trade["curDate"], color = color) if trade["side"] == "long" else pltOBJ.downArrow(trade["curDate"], color = color)

#     if trade["success"]:
#         pltOBJ.plotSingleLine(trade["lastDate"], trade["curDate"], startAnchor="close", endAnchor="high", color = color, ls="dotted") if trade["side"] == "long" else pltOBJ.plotSingleLine(trade["lastDate"], trade["curDate"], startAnchor="close", endAnchor="low", color = color, ls="dotted")
#     else:
#         pltOBJ.plotSingleLine(trade["lastDate"], trade["curDate"], startAnchor="close", endAnchor="low", color = color, ls="dotted") if trade["side"] == "long" else pltOBJ.plotSingleLine(trade["lastDate"], trade["curDate"], startAnchor="close", endAnchor="high", color = color, ls="dotted")
# pltOBJ.show()