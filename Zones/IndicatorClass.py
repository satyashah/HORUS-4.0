import sys
sys.path.insert(0, 'C:/Programming/HORUS-4.0')
from SetUp import *

class atr:
    """
    --ohlcvType: data used for ema ['o', 'h', 'l', 'c', 'v']
    --timePeriod: period calculated for ['5m','1h','1d']
    """
    def __init__(self, rawData, timePeriod, length, extendDF = True) -> None:
        ohlcData = self.getData(rawData, timePeriod)

        self.df = self.atr(ohlcData, length).to_frame(name=f"atr_{length}")

        if extendDF:
            self.df = self.extendDF(rawData, self.df)

        self.optimizeDict = {
            "rawData": rawData,
            'timePeriod': ['1d', '1h'],
            "length": np.arange(5,200,5)
        }

    def atr(self, ohlcData, period):
        high_low = ohlcData['h'] - ohlcData['l']
        high_close = np.abs(ohlcData['h'] - ohlcData['c'].shift())
        low_close = np.abs(ohlcData['l'] - ohlcData['c'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(period).sum()/period

        # atr = atr.fillna(atr.iloc[period+1])

        return atr
    
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


class ema:
    """
    --ohlcvType: data used for ema ['o', 'h', 'l', 'c', 'v']
    --timePeriod: period calculated for ['5m','1h','1d']


    Plot Function:
        emaUpper = emaDF.iloc[:,0] + 1*atrDF.iloc[:,0]
        emaLower = emaDF.iloc[:,0] - 1*atrDF.iloc[:,0]

        pltOBJ.plotLine(emaDF)
        pltOBJ.plotLine(emaUpper)
        pltOBJ.plotLine(emaLower)

        for index, trade in valDF.iterrows():
            color = "green" if trade["success"] else "red"
            pltOBJ.upArrow(trade["lastDate"], color = color) if trade["lastEvent"] == "touchLower" else pltOBJ.downArrow(trade["lastDate"], color = color)
            pltOBJ.upArrow(trade["curDate"], color = color) if trade["curEvent"] == "touchLower" else pltOBJ.downArrow(trade["curDate"], color = color)
    """
    def __init__(self, rawData, ohlcvType, timePeriod, length, extendDF = True) -> None:
        ohlcData = self.getSpecificData(rawData,  ohlcvType, timePeriod)
        self.df = ta.ema(ohlcData, length=length).to_frame()

        if extendDF:
            self.df = self.extendDF(rawData, self.df)

        self.optionsDict = {
            'ohlcvType': ['o', 'h', 'l', 'c', 'v'],
            'timePeriod': ['1d', '1h'],
            "length": list(np.arange(5,200,5))
        }

    def getSpecificData(self, rawData, ohlcvType, timePeriod):
        period = str(timePeriod[1:])
        dataCSV = rawData[[period+'open', period+'high', period+'low', period+'close', period+'volume']].dropna()
        dataCSV.columns = ['o', 'h', 'l', 'c', 'v']

        return dataCSV[ohlcvType]

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

    def validate(self, rawData, testPeriod, atrDF, atrDistance = 1):
        
        ema = (self.df)
        ema.columns = ["ema"]

        emaUpper = (self.df.iloc[:,0] + atrDistance * atrDF.iloc[:,0]).to_frame(name="emaUpper")
        emaLower = (self.df.iloc[:,0] - atrDistance * atrDF.iloc[:,0]).to_frame(name="emaLower")

        dataDF = self.getData(rawData, testPeriod)
        dataDF = pd.concat([dataDF, ema, emaUpper, emaLower], axis = 1)

        dataDF["touchUpper"] = (dataDF["h"]>dataDF["emaUpper"]) & (dataDF["l"]<dataDF["emaUpper"])
        dataDF["touchLower"] = (dataDF["h"]>dataDF["emaLower"]) & (dataDF["l"]<dataDF["emaLower"])

        crossOvers = dataDF[(dataDF["touchUpper"]==True) | (dataDF["touchLower"]==True)]
        crossOvers.to_csv("check.csv")

        valScoreArr = []

        for crossIndex in range(1, len(crossOvers)):
            lastDay = crossOvers.iloc[crossIndex-1]
            curDay = crossOvers.iloc[crossIndex]

            if curDay["touchUpper"] == True and curDay["touchLower"] == True:
                valScoreArr.append([False, curDay.name, "touchLower", curDay.name, "touchUpper"] if curDay["o"]< curDay["c"] else [False, curDay.name, "touchUpper", curDay.name, "touchLower"])
            elif lastDay["touchUpper"] == True and lastDay["touchLower"] == True:
                pass
            elif curDay["touchUpper"] == True:
                if lastDay["touchLower"] == True:
                    valScoreArr.append([False, lastDay.name, "touchLower", curDay.name, "touchUpper"])
                if lastDay["touchUpper"] == True:
                    moveDF = dataDF.loc[lastDay.name:curDay.name]

                    allHighsAboveEma = not any(moveDF["h"]<moveDF["ema"])
                    allLowsBelowEmaUpper = not any(moveDF["l"]>moveDF["emaUpper"])
                    atLeastOneLowBelowEma = any(moveDF["l"]<moveDF["ema"])

                    if allHighsAboveEma and atLeastOneLowBelowEma and allLowsBelowEmaUpper:
                        if len(moveDF) == 2:
                            if moveDF.iloc[0]["c"] < moveDF.iloc[0]["o"] and moveDF.iloc[1]["c"] > moveDF.iloc[1]["o"]:
                                valScoreArr.append([True, lastDay.name, "touchUpper", curDay.name, "touchUpper"])
                        else:
                            valScoreArr.append([True, lastDay.name, "touchUpper", curDay.name, "touchUpper"])
                    
                    if not allHighsAboveEma and atLeastOneLowBelowEma and allLowsBelowEmaUpper:
                        valScoreArr.append([False, lastDay.name, "touchUpper", curDay.name, "touchUpper"])
            
            elif curDay["touchLower"] == True:
                if lastDay["touchUpper"] == True:
                    valScoreArr.append([False, lastDay.name, "touchUpper", curDay.name, "touchLower"])
                if lastDay["touchLower"] == True:
                    moveDF = dataDF.loc[lastDay.name:curDay.name]

                    allLowsBelowEma = not any(moveDF["l"]>moveDF["ema"])
                    allHighsAboveEmaLower = not any(moveDF["h"]<moveDF["emaLower"])
                    atLeastOneHighAboveEma = any(moveDF["h"]>moveDF["ema"])
                    

                    if allLowsBelowEma and atLeastOneHighAboveEma and allHighsAboveEmaLower:
                        if len(moveDF) == 2:
                            if moveDF.iloc[0]["c"] > moveDF.iloc[0]["o"] and moveDF.iloc[1]["c"] < moveDF.iloc[1]["o"]:
                                valScoreArr.append([True, lastDay.name, "touchLower", curDay.name, "touchLower"])
                        else:
                            valScoreArr.append([True, lastDay.name, "touchLower", curDay.name, "touchLower"])

                    if not allLowsBelowEma  and atLeastOneHighAboveEma and allHighsAboveEmaLower:
                        valScoreArr.append([False, lastDay.name, "touchLower", curDay.name, "touchLower"])

        valDF = pd.DataFrame(valScoreArr, columns=['success', 'lastDate', "lastEvent", "curDate", "curEvent"])
        score = sum(valDF["success"].values)/len(valDF["success"].values) if len(valDF["success"].values)>0 else 0
        return score, 1-score, len(valDF["success"].values), valDF

