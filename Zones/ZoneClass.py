import sys
sys.path.insert(0, 'C:/Programming/HORUS-4.0')
from SetUp import *


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
