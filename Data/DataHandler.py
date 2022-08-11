import sys
sys.path.insert(0, 'C:/Programming/HORUS-4.0')
from SetUp import *

class DataHandler():

    def __init__(self) -> None:
        pass

    def getRawData(self, tick, **kwargs):

        def perdelta(start, end, delta):
            curr = start
            while curr < end:
                yield curr
                curr += delta

        timeArr = perdelta(datetime(2015, 12, 1),datetime(2022, 7, 16), timedelta(minutes=5))
        timeArr = list(timeArr)

        # print(kwargs)
        filter5m = kwargs["filter5m"] if "filter5m" in kwargs else True

        testingData = pd.DataFrame(columns=['mopen', 'mhigh', 'mlow', 'mclose', 'mvolume', 'hopen', 'hhigh', 'hlow', 'hclose', 'hvolume', 'dopen', 'dhigh', 'dlow', 'dclose', 'dvolume'])
        
        tickData = pd.DataFrame(index=timeArr)

        mData = pd.read_csv("StockData/{}/5m.csv".format(tick), index_col=0).drop_duplicates()#.drop(columns=["trade_count", "vwap"])
        mData.columns = ["mopen", "mhigh", "mlow", "mclose", "mvolume"]
        mData.index = [parser.parse(dateVal[:19]) for dateVal in mData.index.values]

        hData = pd.read_csv("StockData/{}/1h.csv".format(tick), index_col=0)#.drop(columns=["trade_count", "vwap"])
        hData.columns = ["hopen", "hhigh", "hlow", "hclose", "hvolume"]
        hData.index = [parser.parse(dateVal[:19]) for dateVal in hData.index.values]

        dData = pd.read_csv("StockData/{}/1d.csv".format(tick), index_col=0)#.drop(columns=["trade_count", "vwap"])
        dData.columns = ["dopen", "dhigh", "dlow", "dclose", "dvolume"]
        dData.index = [parser.parse(dateVal[:19]) for dateVal in dData.index.values]
        
        tickData = pd.concat([tickData, mData, hData, dData], axis = 1)
        testingData = pd.concat([testingData, tickData])

        testingData = testingData.dropna(subset=['mopen', 'mhigh', 'mlow', 'mclose', 'mvolume', 'hopen', 'hhigh', 'hlow', 'hclose', 'hvolume', 'dopen', 'dhigh', 'dlow', 'dclose', 'dvolume'], how='all')
        testingData = testingData.loc[mData.iloc[0].name:] if filter5m else testingData
        return testingData

    def saveDF(self, df, path):
        df.to_csv(path)
    
    def getDF(self, path, **kwargs):
        indexPresent = True
        if "indexPresent" in kwargs:
            indexPresent = kwargs["indexPresent"]

        if indexPresent:
            return pd.read_csv(path, index_col=0)
        else:
            return pd.read_csv(path)

DataHandler.__doc__ = \
"""
Data Handler:

    getRawData(tick, **kwargs):
        Returns raw stock Data

        Kwargs:
            filter5m -> Whether the data will be truncated to first instance of 5m Data (Default == True)

    saveDF(df, path):
        Saves DF... duh

    getDF(path, **kwargs):
        Gets DF :)

        Kwargs:
            indexPresent -> Returns Data with first column as index (Default == True)

"""