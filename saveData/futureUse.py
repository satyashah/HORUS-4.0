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