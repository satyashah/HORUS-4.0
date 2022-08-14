import sys
sys.path.insert(0, 'C:/Programming/HORUS-4.0')
from SetUp import *

class LeaveZone:
    """
    When Value leaves Zone
    """
    def __init__(self, zoneData, timePeriod, inZoneDF, names = ["leaveBuyZone", "leaveSellZone"], extendDF = True) -> None:
        
        selectData = self.getData(zoneData, timePeriod)

        leaveZoneArr = []

        for barIndex in range(1, len(selectData.values)-1):
            lastZone = inZoneDF.iloc[barIndex-1]
            curZone = inZoneDF.iloc[barIndex]

            leaveBuyZone = not curZone["inBuyRange"] and lastZone["inBuyRange"] and curZone["buyRangeRelation"] == "above"
            leaveSellZone = not curZone["inSellRange"] and lastZone["inSellRange"] and curZone["sellRangeRelation"] == "below"

            leaveZoneArr.append([selectData.iloc[barIndex+1].name, leaveBuyZone, leaveSellZone])

        self.df = pd.DataFrame(leaveZoneArr, columns = ["index", names[0], names[1]]).set_index("index")

        if extendDF:
            self.df = self.extendDF(zoneData, self.df) 
        
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

            newMinor[(newMinor.index>=lastMinor.name) & (newMinor.index<curMinor.name)] = list(lastMinor.values)

        return newMinor
  
class inZone:
    """
    Enter top zone type and bottom zone type
                Top      Bottom
    flexible => hc|l    h|cl
    partial =>  h|cl    hc|l
    absolute => |hcl    hcl|


    To Plot: (Turn Extend Off)

    for index, bar in inZoneDF.iterrows():
        if bar["inBuyRange"] == True:
            pltOBJ.upArrow(index, color = "green")
        if bar["inSellRange"] == True:
            pltOBJ.downArrow(index, color = "red")

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

            inBuyRange, buyRangeRelation = self.inRange(candleInfo, buyZoneTop, buyZoneBottom, buyZoneTopType, buyZoneBottomType)
            inSellRange, sellRangeRelation = self.inRange(candleInfo, sellZoneTop, sellZoneBottom, sellZoneTopType, sellZoneBottomType)

            inRangeArr.append([index, inBuyRange, buyRangeRelation, inSellRange, sellRangeRelation])

        self.df = pd.DataFrame(inRangeArr, columns=["index", "inBuyRange", "buyRangeRelation", "inSellRange", "sellRangeRelation"]).set_index("index")

        extendDF = kwargs["extendDF"] if "extendDF" in kwargs else True
        
        if extendDF:
            self.df = self.extendDF(zoneData, self.df) 

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
        
        relation = np.nan
        if inTopZone and not inBottomZone:
            relation = "below"
        elif not inTopZone and inBottomZone:
            relation = "above"
        elif not inTopZone and not inBottomZone:
            if barInfo["c"] > barInfo["o"]:
                relation = "above"
            else:
                relation = "below"
        
        return inTopZone and inBottomZone, relation

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

            newMinor[(newMinor.index>=lastMinor.name) & (newMinor.index<curMinor.name)] = list(lastMinor.values)

        return newMinor
