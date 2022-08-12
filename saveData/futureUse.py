def inZone(self, zoneType, zoneRange, curCandle):
    if zoneType == "flexible":
        return zoneRange[0] > curCandle["h"] > zoneRange[1] or zoneRange[0] > curCandle["l"] > zoneRange[1]
    if zoneType == "absolute":
        return zoneRange[0] > curCandle["h"] > curCandle["l"] > zoneRange[1]
    if zoneType == "partial":
        return zoneRange[0] > curCandle["o"] > zoneRange[1] and  zoneRange[0] > curCandle["c"] > zoneRange[1]


    if zoneType[0] == "flexible":
        inTopZone = zoneRange[0] > curCandle["l"] > zoneRange[1]
    if zoneType[0] == "absolute":
        inTopZone = zoneRange[0] > curCandle["h"] > zoneRange[1]
    if zoneType[0] == "partial":
        inTopZone = zoneRange[0] > max(curCandle["o"], curCandle["c"]) > zoneRange[1] 


    if zoneType[1] == "flexible":
        inBottomZone = zoneRange[0] > curCandle["h"] > zoneRange[1]
    if zoneType[1] == "absolute":
        inBottomZone = zoneRange[0] > curCandle["h"] > zoneRange[1]
    if zoneType[1] == "partial":
        inBottomZone = zoneRange[0] > max(curCandle["o"], curCandle["c"]) > zoneRange[1] 
        
    if zoneType == "topFlex":
        return zoneRange[0] > curCandle["l"] > zoneRange[1]
    if zoneType == "bottomFlex":
        return zoneRange[0] > curCandle["h"] > zoneRange[1]



def validate(self, indicatorData, testPeriod, atrDF, atrDistance = 1):
    dataDF = self.getData(indicatorData, testPeriod)
    print(dataDF)

    crossArr = []

    for barIndex in range(1, len(dataDF)):
        
        lastCandle = dataDF.iloc[barIndex-1]
        curCandle = dataDF.iloc[barIndex]

        lastRange = self.df.loc[lastCandle.name]
        curRange = self.df.loc[curCandle.name]

        curAtr = atrDF.loc[curCandle.name]

        if not pd.isna(lastRange["ematrTopBuy"]):

            buyUpperCross = lastCandle["c"] < lastRange["ematrTopBuy"] and curCandle["c"] > curRange["ematrTopBuy"]
            sellLowerCross = lastCandle["c"] > lastRange["ematrBottomSell"] and curCandle["c"] < curRange["ematrBottomSell"]
            
            buyLowerCross = lastCandle["l"] > lastRange["ematrBottomBuy"] and curCandle["l"] < curRange["ematrBottomBuy"]
            sellUpperCross = lastCandle["h"] < lastRange["ematrTopSell"] and curCandle["h"] > curRange["ematrTopSell"]

            buyPlusAtr = curRange["ematrTopBuy"] + atrDistance*curAtr > lastCandle["h"]  and curRange["ematrTopBuy"] + atrDistance*curAtr < curCandle["h"] 
            sellPlusAtr = curRange["ematrBottomSell"] - atrDistance*curAtr < lastCandle["l"] and curRange["ematrBottomSell"] - atrDistance*curAtr > curCandle["l"]

            crossArr.append([curCandle.name, buyUpperCross, sellLowerCross, buyLowerCross, sellUpperCross, buyPlusAtr, sellPlusAtr])
        
        else:
            crossArr.append([np.nan]*6)

    crossDF = pd.DataFrame(crossArr, columns=['date', 'buyUpperCross', 'sellLowerCross', 'buyLowerCross', 'sellUpperCross', 'buyPlusAtr', 'sellPlusAtr']).set_index("date")
    print(crossDF)

    crossDF.to_csv("check.csv")
    
    buysDF = crossDF[(crossDF["buyUpperCross"]) | (crossDF["buyLowerCross"]) | (crossDF["buyPlusAtr"])]
    print(buysDF)
    
    valScoreArr = []

    for buyIndex in range(1, len(buysDF)):
        tradeDay = buysDF.iloc[buyIndex-1]
        stop = buysDF.iloc[buyIndex]

        if tradeDay["buyUpperCross"] == True:
            if stop["buyLowerCross"]:
                valScoreArr.append([False, "long", tradeDay.name, stop.name])
            if stop["buyPlusAtr"]:
                valScoreArr.append([True, "long", tradeDay.name, stop.name])
    
    sellsDF = crossDF[(crossDF["sellUpperCross"]) | (crossDF["sellLowerCross"]) | (crossDF["sellPlusAtr"])]
    print(sellsDF)

    for sellIndex in range(1, len(sellsDF)):
        tradeDay = sellsDF.iloc[sellIndex-1]
        stop = sellsDF.iloc[sellIndex]

        if tradeDay["sellLowerCross"] == True:
            if stop["sellUpperCross"]:
                valScoreArr.append([False, "short", tradeDay.name, stop.name])
            if stop["sellPlusAtr"]:
                valScoreArr.append([True, "short", tradeDay.name, stop.name])

    valDF = pd.DataFrame(valScoreArr, columns=["success", "side", "lastDate", "curDate"])
    score = sum(valDF["success"].values)/len(valDF["success"].values) if len(valDF["success"].values)>0 else 0
        
    return score, len(valDF["success"].values), valDF
