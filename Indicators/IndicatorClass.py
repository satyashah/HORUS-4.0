import sys
sys.path.insert(0, 'C:/Programming/HORUS-4.0')
from SetUp import *

class atr:
    """
    --ohlcvType: data used for ema ['o', 'h', 'l', 'c', 'v']
    --timePeriod: period calculated for ['5m','1h','1d']
    """
    def __init__(self, rawData, timePeriod, length, extendDF = True, name = "atr") -> None:
        ohlcData = self.getData(rawData, timePeriod)

        self.df = self.atr(ohlcData, length).to_frame(name=f"atr_{length}")

        if extendDF:
            self.df = self.extendDF(rawData, self.df)

        self.df.columns = [name]

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
    def __init__(self, rawData, ohlcvType, timePeriod, length, extendDF = True, name = "ema") -> None:
        ohlcData = self.getSpecificData(rawData,  ohlcvType, timePeriod)
        self.df = ta.ema(ohlcData, length=length).to_frame()

        if extendDF:
            self.df = self.extendDF(rawData, self.df)

        self.df.columns = [name]
        
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

class pivots:
    """
        for index, anchors in pivotsDF.iterrows():
            pltOBJ.upArrow(index, color = "#5EB1BF") if anchors["type"] == "low" else pltOBJ.downArrow(index, color = "#EF7B45")
    """
    def __init__(self, rawData, timePeriod, swingLen, extendDF = True):
        dataCSV = self.getData(rawData, timePeriod)
        self.df = self.getPivotHL(dataCSV, swingLen)

        if extendDF:
            self.df = self.extendDF(rawData, self.df)

    def getData(self, masterData, calcPeriod):
        period = str(calcPeriod[1:])
        dataCSV = masterData[[period+'open', period+'high', period+'low', period+'close', period+'volume']].dropna()
        dataCSV.columns = ['open', 'high', 'low', 'close', 'volume']
        return dataCSV

    def getPivotHL(self, data, swingLen):
        max_idx = argrelextrema(data['high'].values, np.greater, order=swingLen)[0]
        min_idx = argrelextrema(data['low'].values, np.less, order=swingLen)[0]

        highVals = [[list(data.index.values)[idx], data['high'].values[idx], "high"] for idx in max_idx]
        lowVals = [[list(data.index.values)[idx], data['low'].values[idx], "low"] for idx in min_idx]

        allPeaks = highVals + lowVals

        allPeaks.sort(key=lambda x:x[0])
        
        for index in range(len(allPeaks)-2, 0, -1):
            if allPeaks[index][2] == allPeaks[index+1][2]:
                if allPeaks[index][2] == "high":
                    allPeaks.pop(index if allPeaks[index][1]<allPeaks[index+1][1] else index+1)
                else:
                    allPeaks.pop(index if allPeaks[index][1]>allPeaks[index+1][1] else index+1)

        # plt.plot(data['close'])
        # [plt.scatter(i[0], i[1], c="green" if i[2] == "high" else "red") for i in allPeaks]
        # plt.show()
        peaksDF = pd.DataFrame(allPeaks, columns = ["index", "peak", "type"]).set_index("index")
        return peaksDF
    
    def extendDF(self, master, minor):
        minorCols = list(minor.columns.values)

        newMinor = pd.DataFrame(columns=minorCols, index=list(master.index.values))

        for index in range(1, len(minor.index.values)):
            lastMinor = minor.iloc[index-1]
            curMinor = minor.iloc[index]

            newMinor[(newMinor.index>=lastMinor.name) & (newMinor.index<curMinor.name)] = list(lastMinor.values) #EXTEND TO LAST DAY!!

        return newMinor

class vp:
    """
    --dataTimePeriod: data period which the vp is built off of  ['5m','1h','1d']

    Runner:

        pivotsOBJ = pivots(rawData, "1h", 15, extendDF=False)
        pivotsDF = pivotsOBJ.df
        print(pivotsDF)


        atrOBJ = atr(rawData, "1h", 14)
        atrDF = atrOBJ.df


        vpOBJ = vp(rawData, pivotsDF["peak"], "1h", "5m", 15, 4, fastRefresh = False)
        vpDF = vpOBJ.df

        score, sampleSize, valDF = vpOBJ.validate(rawData, "1h", atrDF, atrDistance = 1)
        print(round(score*100,3),"% \nSample Size:",sampleSize)

        
    Plot:
        pltOBJ.plotLine(vpDF["poc"], color = "#CDEDF6")
        pltOBJ.plotLine(vpDF["poc"]+atrDF["atr"], color = "#5EB1BF")
        pltOBJ.plotLine(vpDF["poc"]-atrDF["atr"], color = "#EF7B45")

        for index, trade in valDF.iterrows():
            color = "green" if trade["success"] else "red"
            pltOBJ.upArrow(trade["lastDate"], color = color) if trade["side"] == "long" else pltOBJ.downArrow(trade["lastDate"], color = color)

            if trade["success"]:
                pltOBJ.plotSingleLine(trade["lastDate"], trade["curDate"], startAnchor="close", endAnchor="high", color = color, ls="dotted") if trade["side"] == "long" else pltOBJ.plotSingleLine(trade["lastDate"], trade["curDate"], startAnchor="close", endAnchor="low", color = color, ls="dotted")
            else:
                pltOBJ.plotSingleLine(trade["lastDate"], trade["curDate"], startAnchor="close", endAnchor="low", color = color, ls="dotted") if trade["side"] == "long" else pltOBJ.plotSingleLine(trade["lastDate"], trade["curDate"], startAnchor="close", endAnchor="high", color = color, ls="dotted")

    """

    def __init__(self, masterData, anchorDF, timePeriod, dataTimePeriod, swingLookBack, vpPastSwings, extendDF = True, name = "poc", vpBins = 20, fastRefresh = True) -> None:
        
        self.fastRefresh = fastRefresh
        self.vpBins = vpBins
        
        dailyCSV = self.getData(masterData, timePeriod)
        minuteCSV = self.getData(masterData, dataTimePeriod)

        anchorDF.name = "anchor"
        dailyCSV = pd.concat([dailyCSV,anchorDF], axis=1)
        dailyCSV = self.buildVPSupports(dailyCSV, minuteCSV, swingLookBack, vpPastSwings)
        # formatCSV = self.format(formatCSV)

        dailyCSV.columns = [name]
        self.df = dailyCSV

        if extendDF:
            self.df = self.extendDF(masterData, self.df)
    
    def getData(self, masterData, calcPeriod):
        period = str(calcPeriod[1:])
        dataCSV = masterData[[period+'open', period+'high', period+'low', period+'close', period+'volume']].dropna()
        dataCSV.columns = ['open', 'high', 'low', 'close', 'volume']
        return dataCSV

    def buildVPSupports(self, dailyCSV, minuteCSV, swingLen, vpPastSwings):
        dailyCSV = dailyCSV.reset_index()
        filteredPeaks = dailyCSV.dropna(subset="anchor")
        fourthFP = filteredPeaks.iloc[vpPastSwings-1].name+swingLen+1
        poc = np.nan
        
        vpArr = [np.nan] * fourthFP
        for index in range(fourthFP, len(dailyCSV.index.values)):
            lastPeaks = filteredPeaks[filteredPeaks.index+swingLen<index]

            curPeak, lastPeak = lastPeaks.iloc[-1].name, lastPeaks.iloc[-vpPastSwings].name

            refreshCondition = index%10 == 0
            if not self.fastRefresh:
                refreshCondition = (index == curPeak + swingLen + 1)

            if refreshCondition:
                minDF = minuteCSV[(minuteCSV.index >= dailyCSV.iloc[lastPeak]["index"]) & (minuteCSV.index < dailyCSV.iloc[index]["index"])]
                vpDF, poc = self.getVP(minDF)
            
            vpArr.append(poc)

        dailyCSV["poc"] = vpArr
        dailyCSV = dailyCSV.set_index("index")
        return dailyCSV[["poc"]]

    def getVP(self,dataCSV):
        vpDF = ta.vp(dataCSV["close"], dataCSV["volume"],width=self.vpBins, sort_close=True)
        return vpDF, vpDF.loc[vpDF["total_volume"].idxmax()]["mean_close"]

    def extendDF(self, master, minor):
        minorCols = list(minor.columns.values)

        newMinor = pd.DataFrame(columns=minorCols, index=list(master.index.values))

        for index in range(1, len(minor.index.values)):
            lastMinor = minor.iloc[index-1]
            curMinor = minor.iloc[index]

            newMinor[(newMinor.index>=lastMinor.name) & (newMinor.index<curMinor.name)] = list(lastMinor.values) #EXTEND TO LAST DAY!!

        return newMinor

    def validate(self, rawData, testPeriod, atrDF, atrDistance = 1):
        dataDF = self.getData(rawData, testPeriod)

        crossArr = []

        for barIndex in range(1, len(dataDF)):
            
            lastCandle = dataDF.iloc[barIndex-1]
            curCandle = dataDF.iloc[barIndex]

            lastVal = self.df.loc[lastCandle.name][self.df.columns[0]]
            curVal = self.df.loc[curCandle.name][self.df.columns[0]]

            curAtr = atrDF.loc[curCandle.name][atrDF.columns[0]]

            if not pd.isna(lastVal):

                longSignal = lastCandle["low"] < lastVal and curCandle["low"] > curVal
                shortSignal = lastCandle["high"] > lastVal and curCandle["high"] < curVal
                
                longSL = curVal
                shortSL = curVal

                longTP = curVal + atrDistance*curAtr
                shortTP = curVal - atrDistance*curAtr
                crossArr.append([curCandle.name, longSignal, shortSignal, longSL, shortSL, longTP, shortTP])
            
            else:
                crossArr.append([np.nan]*6)

        crossDF = pd.DataFrame(crossArr, columns=['date', 'longSignal', 'shortSignal', 'longSL', 'shortSL', 'longTP', 'shortTP']).set_index("date")

        crossDF.to_csv("check.csv")
        valScoreArr = []

        buysDF = crossDF[crossDF["longSignal"]==True]

        for index, buyInfo in buysDF.iterrows():
            
            testDF = dataDF.loc[index:].iloc[1:]
            tpIndex = testDF[testDF["high"]>buyInfo["longTP"]].index
            slIndex = testDF[testDF["high"]<buyInfo["longSL"]].index

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
            tpIndex = testDF[testDF["low"]<sellInfo["shortTP"]].index
            slIndex = testDF[testDF["low"]>sellInfo["shortSL"]].index

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

class vwap:
    """
    --dataTimePeriod: data period which the vp is built off of  ['5m','1h','1d']

    Runner:

        pivotsOBJ = pivots(rawData, "1h", 15, extendDF=False)
        pivotsDF = pivotsOBJ.df


        atrOBJ = atr(rawData, "1h", 14)
        atrDF = atrOBJ.df


        vwapOBJ = vwap(rawData, pivotsDF["peak"], "1h", 15, 4, "hlc3", keep="all")
        vwapDF = vwapOBJ.df
        print(vwapDF)

        score, sampleSize, valDF = vwapOBJ.validate(rawData, "1h", atrDF, atrDistance = 1)
        print(round(score*100,3),"% \nSample Size:",sampleSize)
        print(valDF)

        pltOBJ = Plotter(rawData, "1h", volPlot= True)

        

        
    Plot:
        pltOBJ.plot()

        pltOBJ.plotLine(vwapDF["+2SD"], color = "#EF476F")
        pltOBJ.plotLine(vwapDF["+SD"], color = "#FFD166")
        pltOBJ.plotLine(vwapDF["vwap"], color = "#06D6A0")
        pltOBJ.plotLine(vwapDF["-SD"], color = "#118AB2")
        pltOBJ.plotLine(vwapDF["-2SD"], color = "#0A5770")

        for index, anchors in pivotsDF.iterrows():
            pltOBJ.upArrow(index, color = "#5EB1BF") if anchors["type"] == "low" else pltOBJ.downArrow(index, color = "#EF7B45")

        for index, trade in valDF.iterrows():
            color = "green" if trade["success"] else "red"
            pltOBJ.upArrow(trade["lastDate"], color = color) if trade["lastEvent"] == "touchLower" else pltOBJ.downArrow(trade["lastDate"], color = color)
            pltOBJ.upArrow(trade["curDate"], color = color) if trade["curEvent"] == "touchLower" else pltOBJ.downArrow(trade["curDate"], color = color)

        pltOBJ.show()
    """

    def __init__(self, masterData, anchorPointsDF, calcPeriod, swingLookBack, vwapPastSwings, ohlcCalc, extendDF = True, name = ["-2SD","-SD","vwap","+SD","+2SD"], keep = "vwap"):
        self.name = name
        self.keep = keep
        
        dataCSV = self.getData(masterData, calcPeriod)

        anchorPointsDF.name = "anchors"
        dataCSV = pd.concat([dataCSV,anchorPointsDF], axis=1)
        dataCSV = self.buildVWAPSupports(dataCSV, swingLookBack, vwapPastSwings, ohlcCalc)

        self.df = dataCSV

        if extendDF:
            self.df = self.extendDF(masterData, self.df)
        
    def getData(self, masterData, calcPeriod):
        period = str(calcPeriod[1:])
        dataCSV = masterData[[period+'open', period+'high', period+'low', period+'close', period+'volume']].dropna()
        dataCSV.columns = ['open', 'high', 'low', 'close', 'volume']
        return dataCSV

    def buildVwap(self, dataCSV, ohlcCalc):

        prices = []
        cumulativeVolume = 0
        cumulativeTPV = 0

        DownTwoSD = []
        DownOneSD = []
        vwapArr = []
        UpOneSD = []
        UpTwoSD = []


        for rowIndex in range(0,len(dataCSV["close"].values)):

            c = dataCSV.iloc[[rowIndex]]["close"].values[0]
            h = dataCSV.iloc[[rowIndex]]["high"].values[0]
            l = dataCSV.iloc[[rowIndex]]["low"].values[0]
            v = dataCSV.iloc[[rowIndex]]["volume"].values[0]

            if ohlcCalc == "high":
                tpv = h
            elif ohlcCalc == "low":
                tpv = l
            elif ohlcCalc == "hlc3":
                tpv = (c+h+l)/3
            else:
                tpv = c
            


            cumulativeTPV += tpv * v
            cumulativeVolume += v
            
            prices.append(c)
            
            standardDeviation = statistics.stdev(prices) if len(prices)>1 else 0

            DownTwoSD.append(cumulativeTPV / cumulativeVolume - 2*standardDeviation)
            DownOneSD.append(cumulativeTPV / cumulativeVolume - standardDeviation)
            vwapArr.append(cumulativeTPV / cumulativeVolume)
            UpOneSD.append(cumulativeTPV / cumulativeVolume + standardDeviation)
            UpTwoSD.append(cumulativeTPV / cumulativeVolume + 2*standardDeviation)

        vwapDF = pd.DataFrame({"DownTwoSD": DownTwoSD, "DownOneSD":DownOneSD, "vwapArr":vwapArr, "UpOneSD":UpOneSD, "UpTwoSD":UpTwoSD}).set_index(dataCSV.index)
        return vwapDF

    def buildVWAPSupports(self, supResDF, swingLen, vwapPastSwings, ohlcCalc):
        supResDF = supResDF.reset_index()
        peaksDF = supResDF.dropna(subset=["anchors"])

        vwapDF = pd.DataFrame(columns=["DownTwoSD","DownOneSD","vwapArr","UpOneSD","UpTwoSD"])

        for peakIndex in range(int(vwapPastSwings/2),len(peaksDF.index.values)):
            curPeak, lastPeak, lastLastPeak = peaksDF.iloc[peakIndex].name, peaksDF.iloc[peakIndex-1].name, peaksDF.iloc[peakIndex-int(vwapPastSwings/2)].name
            cutOff = len(supResDF) if peakIndex == len(peaksDF.index.values)-1 else curPeak+swingLen
            vwapTempDF = self.buildVwap(supResDF.iloc[lastLastPeak:cutOff], ohlcCalc).loc[lastPeak+swingLen:]
            vwapDF = pd.concat([vwapDF,vwapTempDF])
    
        vwapDF.columns = self.name
        vwapDF = pd.concat([supResDF, vwapDF], axis=1).set_index("index")

        if self.keep == "vwap":
            vwapDF = vwapDF[[self.name[2]]]
        elif self.keep == "1SD":
            vwapDF = vwapDF[[self.name[1],self.name[2],self.name[3]]]
        else:
            vwapDF = vwapDF[[self.name[0],self.name[1],self.name[2],self.name[3],self.name[4]]]

        return vwapDF

    def validate(self, rawData, testPeriod, atrDF, atrDistance = 1):
        
        vwap = self.df[self.name[2]]

        vwapUpper = self.df[self.name[3]]
        vwapLower = self.df[self.name[1]]

        dataDF = self.getData(rawData, testPeriod)

        vwap.name, vwapUpper.name, vwapLower.name = "vwap", "vwapUpper", "vwapLower"
        dataDF = pd.concat([dataDF, vwap, vwapUpper, vwapLower], axis = 1)

        dataDF["touchUpper"] = (dataDF["high"]>dataDF["vwapUpper"]) & (dataDF["low"]<dataDF["vwapUpper"])
        dataDF["touchLower"] = (dataDF["high"]>dataDF["vwapLower"]) & (dataDF["low"]<dataDF["vwapLower"])

        crossOvers = dataDF[(dataDF["touchUpper"]==True) | (dataDF["touchLower"]==True)]
        crossOvers.to_csv("check.csv")

        valScoreArr = []

        for crossIndex in range(1, len(crossOvers)):
            lastDay = crossOvers.iloc[crossIndex-1]
            curDay = crossOvers.iloc[crossIndex]

            if curDay["touchUpper"] == True and curDay["touchLower"] == True:
                valScoreArr.append([False, curDay.name, "touchLower", curDay.name, "touchUpper", "short"] if curDay["open"]< curDay["close"] else [False, curDay.name, "touchUpper", curDay.name, "touchLower", "long"])
            elif lastDay["touchUpper"] == True and lastDay["touchLower"] == True:
                pass
            elif curDay["touchUpper"] == True:
                if lastDay["touchLower"] == True:
                    valScoreArr.append([False, lastDay.name, "touchLower", curDay.name, "touchUpper", "long"])
                if lastDay["touchUpper"] == True:
                    moveDF = dataDF.loc[lastDay.name:curDay.name]

                    allHighsAboveVwap = not any(moveDF["high"]<moveDF["vwap"])
                    allLowsBelowVwapUpper = not any(moveDF["low"]>moveDF["vwapUpper"])
                    atLeastOneLowBelowVwap = any(moveDF["low"]<moveDF["vwap"])

                    if allHighsAboveVwap and atLeastOneLowBelowVwap and allLowsBelowVwapUpper:
                        if len(moveDF) == 2:
                            if moveDF.iloc[0]["close"] < moveDF.iloc[0]["open"] and moveDF.iloc[1]["close"] > moveDF.iloc[1]["open"]:
                                valScoreArr.append([True, lastDay.name, "touchUpper", curDay.name, "touchUpper", "long"])
                        else:
                            valScoreArr.append([True, lastDay.name, "touchUpper", curDay.name, "touchUpper", "long"])
                    
                    if not allHighsAboveVwap and atLeastOneLowBelowVwap and allLowsBelowVwapUpper:
                        valScoreArr.append([False, lastDay.name, "touchUpper", curDay.name, "touchUpper", "long"])
            
            elif curDay["touchLower"] == True:
                if lastDay["touchUpper"] == True:
                    valScoreArr.append([False, lastDay.name, "touchUpper", curDay.name, "touchLower", "short"])
                if lastDay["touchLower"] == True:
                    moveDF = dataDF.loc[lastDay.name:curDay.name]

                    allLowsBelowVwap = not any(moveDF["low"]>moveDF["vwap"])
                    allHighsAboveVwapLower = not any(moveDF["high"]<moveDF["vwapLower"])
                    atLeastOneHighAboveVwap = any(moveDF["high"]>moveDF["vwap"])
                    

                    if allLowsBelowVwap and atLeastOneHighAboveVwap and allHighsAboveVwapLower:
                        if len(moveDF) == 2:
                            if moveDF.iloc[0]["close"] > moveDF.iloc[0]["open"] and moveDF.iloc[1]["close"] < moveDF.iloc[1]["open"]:
                                valScoreArr.append([True, lastDay.name, "touchLower", curDay.name, "touchLower", "short"])
                        else:
                            valScoreArr.append([True, lastDay.name, "touchLower", curDay.name, "touchLower", "short"])

                    if not allLowsBelowVwap  and atLeastOneHighAboveVwap and allHighsAboveVwapLower:
                        valScoreArr.append([False, lastDay.name, "touchLower", curDay.name, "touchLower", "short"])

        valDF = pd.DataFrame(valScoreArr, columns=['success', 'lastDate', "lastEvent", "curDate", "curEvent", "side"])
        score = sum(valDF["success"].values)/len(valDF["success"].values) if len(valDF["success"].values)>0 else 0
        return score, len(valDF["success"].values), valDF

    def extendDF(self, master, minor):
        minorCols = list(minor.columns.values)

        newMinor = pd.DataFrame(columns=minorCols, index=list(master.index.values))

        for index in range(1, len(minor.index.values)):
            lastMinor = minor.iloc[index-1]
            curMinor = minor.iloc[index]

            newMinor[(newMinor.index>=lastMinor.name) & (newMinor.index<curMinor.name)] = list(lastMinor.values) #EXTEND TO LAST DAY!!

        return newMinor


class regression:
    """
    --dataTimePeriod: data period which the vp is built off of  ['5m','1h','1d']

    Runner:

        pivotsOBJ = pivots(rawData, "1h", 15*24, extendDF=False)
        pivotsDF = pivotsOBJ.df


        # atrOBJ = atr(rawData, "1h", 14)
        # atrDF = atrOBJ.df

        regOBJ = regression(rawData, pivotsDF["peak"], "1h", 15*24, 1, continuousReg = False, constantRefresh = True)
        regDF = regOBJ.df
        print(regDF)



        #----------Test Class [Optimize as well]

        # score, sampleSize, valDF = vwapOBJ.validate(rawData, "1h", atrDF, atrDistance = 1)
        # print(round(score*100,3),"% \nSample Size:",sampleSize)
        # print(valDF)


        #----------Plot Class

        

        
    Plot:
        pltOBJ = Plotter(rawData, "1h", volPlot= True)
        pltOBJ.plot()

        pltOBJ.plotLine(regDF["+2SD"], color = "#EF476F")
        pltOBJ.plotLine(regDF["+SD"], color = "#FFD166")
        pltOBJ.plotLine(regDF["reg"], color = "#06D6A0")
        pltOBJ.plotLine(regDF["-SD"], color = "#118AB2")
        pltOBJ.plotLine(regDF["-2SD"], color = "#0A5770")

        for index, anchors in pivotsDF.iterrows():
            pltOBJ.upArrow(index, color = "#5EB1BF") if anchors["type"] == "low" else pltOBJ.downArrow(index, color = "#EF7B45")
    """

    def __init__(self, masterData, anchorDF, timePeriod, swingLookBack, regPastSwings, continuousReg = False, ohlcType = "close", extendDF = True, name = ["-2SD","-SD","reg","+SD","+2SD"], constantRefresh = True, keep = "all"):
        
        self.constantRefresh = constantRefresh
        self.ohlcType = ohlcType
        self.name = name
        
        dataCSV = self.getData(masterData, timePeriod)

        anchorDF.name = "anchor"
        dataCSV = pd.concat([dataCSV,anchorDF], axis=1)
        if continuousReg:
            dataCSV = self.buildRegSupportsContinuous(dataCSV, swingLookBack, regPastSwings)
        else:
            dataCSV = self.buildRegSupports(dataCSV, swingLookBack, regPastSwings)

        if keep == "reg":
            dataCSV = dataCSV[[name[2]]]
        if keep == "1SD":
            dataCSV = dataCSV[[name[1],name[2],name[3]]]

        self.df = dataCSV

        if extendDF:
            self.df = self.extendDF(masterData, self.df)
    
    def getData(self, masterData, calcPeriod):
        period = str(calcPeriod[1:])
        dataCSV = masterData[[period+'open', period+'high', period+'low', period+'close', period+'volume']].dropna()
        dataCSV.columns = ['open', 'high', 'low', 'close', 'volume']
        return dataCSV
    
    def buildRegSupportsContinuous(self, dailyCSV, swingLen, regPastSwings):
        dailyCSV = dailyCSV.reset_index()
        
        regArr = [[np.nan]*5] * swingLen

        for index in range(swingLen, len(dailyCSV.index.values)):

            refreshCondition = index%1 == 0 or index == swingLen

            if refreshCondition:
                dataDF =  dailyCSV.iloc[index-swingLen:index]
                reg, sd = self.getReg(dataDF)

            curValue = reg.predict(np.array([index]).reshape(1, -1))[0]
            regArr.append([curValue-(2*sd),curValue-sd,curValue,curValue+sd,curValue+(2*sd)])

        regDF = pd.DataFrame(regArr, columns=self.name)
        regDF = regDF.set_index(dailyCSV["index"].values, drop=True)
        return regDF


    def buildRegSupports(self, dailyCSV, swingLen, regPastSwings):
        dailyCSV = dailyCSV.reset_index()
        filteredPeaks = dailyCSV.dropna(subset="anchor")
        fourthFP = filteredPeaks.iloc[regPastSwings-1].name+swingLen+1
        
        regArr = [[np.nan]*5] * fourthFP

        for index in range(fourthFP, len(dailyCSV.index.values)):
            lastPeaks = filteredPeaks[filteredPeaks.index+swingLen<index]

            curPeak, lastPeak = lastPeaks.iloc[-1].name, lastPeaks.iloc[-regPastSwings].name

            refreshCondition = index%1 == 0 or index == fourthFP
            if not self.constantRefresh:
                refreshCondition = (index == curPeak + swingLen + 1)

            if refreshCondition:
                dataDF =  dailyCSV.iloc[lastPeak:index]
                reg, sd = self.getReg(dataDF)

            curValue = reg.predict(np.array([index]).reshape(1, -1))[0]
            regArr.append([curValue-(2*sd),curValue-sd,curValue,curValue+sd,curValue+(2*sd)])

        regDF = pd.DataFrame(regArr, columns=self.name)
        regDF = regDF.set_index(dailyCSV["index"].values, drop=True)
        print(regDF)
        return regDF

    def getReg(self,dataCSV):

        y = np.array(dataCSV[self.ohlcType].values)
        x = np.array(dataCSV.index.values).reshape((-1, 1))

        reg = LinearRegression().fit(x, y)

        y_reg = [reg.predict(np.array([index]).reshape(1, -1))[0] for index in x]

        distList = y-y_reg
        sd = sum(abs(distList))/ len(distList)

        return reg, sd

    def extendDF(self, master, minor):
        minorCols = list(minor.columns.values)

        newMinor = pd.DataFrame(columns=minorCols, index=list(master.index.values))

        for index in range(1, len(minor.index.values)):
            lastMinor = minor.iloc[index-1]
            curMinor = minor.iloc[index]

            newMinor[(newMinor.index>=lastMinor.name) & (newMinor.index<curMinor.name)] = list(lastMinor.values) #EXTEND TO LAST DAY!!

        return newMinor

    def validate(self, rawData, testPeriod, atrDF, atrDistance = 1):
        dataDF = self.getData(rawData, testPeriod)

        crossArr = []

        for barIndex in range(1, len(dataDF)):
            
            lastCandle = dataDF.iloc[barIndex-1]
            curCandle = dataDF.iloc[barIndex]

            lastVal = self.df.loc[lastCandle.name][self.df.columns[0]]
            curVal = self.df.loc[curCandle.name][self.df.columns[0]]

            curAtr = atrDF.loc[curCandle.name][atrDF.columns[0]]

            if not pd.isna(lastVal):

                longSignal = lastCandle["low"] < lastVal and curCandle["low"] > curVal
                shortSignal = lastCandle["high"] > lastVal and curCandle["high"] < curVal
                
                longSL = curVal
                shortSL = curVal

                longTP = curVal + atrDistance*curAtr
                shortTP = curVal - atrDistance*curAtr
                crossArr.append([curCandle.name, longSignal, shortSignal, longSL, shortSL, longTP, shortTP])
            
            else:
                crossArr.append([np.nan]*6)

        crossDF = pd.DataFrame(crossArr, columns=['date', 'longSignal', 'shortSignal', 'longSL', 'shortSL', 'longTP', 'shortTP']).set_index("date")

        crossDF.to_csv("check.csv")
        valScoreArr = []

        buysDF = crossDF[crossDF["longSignal"]==True]

        for index, buyInfo in buysDF.iterrows():
            
            testDF = dataDF.loc[index:].iloc[1:]
            tpIndex = testDF[testDF["high"]>buyInfo["longTP"]].index
            slIndex = testDF[testDF["high"]<buyInfo["longSL"]].index

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
            tpIndex = testDF[testDF["low"]<sellInfo["shortTP"]].index
            slIndex = testDF[testDF["low"]>sellInfo["shortSL"]].index

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














































