from matplotlib.pyplot import tight_layout
from pandas import DatetimeIndex
from SetUp import *

class Plotter:
    """
    --calcPeriod: period calculated for ['5m','1h','1d']
    """

    def __init__(self, rawData, timePeriod) -> None:

        plt.rcParams['axes.facecolor'] = 'black'
        plt.rcParams['axes.edgecolor'] = 'black'
        plt.figure(figsize=(18, 10), tight_layout = True, dpi=80)

        self.timePeriod = timePeriod
        self.rawData = rawData

        self.selectData = self.getSpecificData()
        self.plotIndex = list(self.selectData.index)
        self.selectData.index = [parser.parse(date) for date in self.selectData.index]

        self.averageRange = (self.selectData["high"] - self.selectData["low"]).mean()

    def plot(self):
        prices = self.getSpecificData()

        dateIndex = [parser.parse(date) for date in prices.index]
        prices.index = dateIndex

        minDistance = divmod((dateIndex[2]-dateIndex[1]).total_seconds(), 60)[0]
        

        width = minDistance/24/60
        width2 = minDistance/24/60/8

        #define up and down prices
        up = prices[prices.close>=prices.open]
        down = prices[prices.close<prices.open]

        #define colors to use
        col1 = 'green'
        col2 = 'red'

        #plot up prices
        plt.bar(up.index,up.close-up.open,width,bottom=up.open,color=col1)
        plt.bar(up.index,up.high-up.close,width2,bottom=up.close,color=col1)
        plt.bar(up.index,up.low-up.open,width2,bottom=up.open,color=col1)

        #plot down prices
        plt.bar(down.index,down.close-down.open,width,bottom=down.open,color=col2)
        plt.bar(down.index,down.high-down.open,width2,bottom=down.open,color=col2)
        plt.bar(down.index,down.low-down.close,width2,bottom=down.close,color=col2)

        #rotate x-axis tick labels
        plt.xticks(rotation=45, ha='right')

    def getSpecificData(self):
        period = str(self.timePeriod[1:])
        dataCSV = self.rawData[[period+'open', period+'high', period+'low', period+'close', period+'volume']].dropna()
        dataCSV.columns = ['open', 'high', 'low', 'close', 'volume']
        return dataCSV

    def plotLine(self, line, color = "b"):
        lineDF = line.loc[self.plotIndex]

        dateIndex = [parser.parse(date) for date in lineDF.index]

        plt.plot(dateIndex, lineDF.values, c = color)

    def upArrow(self, date, y = None, color = "m"):
        date = parser.parse(date)

        if y is None:
            y = self.selectData.loc[date]["low"] - self.averageRange

        plt.scatter(date, y, c=color, marker="^")
    
    def downArrow(self, date, y = None, color = "c"):
        date = parser.parse(date)

        if y is None:
            y = self.selectData.loc[date]["high"] + self.averageRange

        plt.scatter(date, y, c=color, marker="v")

    def shadeArea(self, rangeDF, opacity, color):

        topArr = list(rangeDF.iloc[:, 0].values)
        bottomArr = list(rangeDF.iloc[:, 1].values)

        dateIndex = [parser.parse(date) for date in rangeDF.index]

        plt.fill_between(dateIndex, topArr, bottomArr, color=color, alpha=opacity)

    def show(self):
        plt.show()


"""
    def plot(self, openDF, highDF, lowDF, closeDF):
        prices = pd.concat([openDF.to_frame(), highDF.to_frame(), lowDF.to_frame(), closeDF.to_frame()], axis = 1)

        dateIndex = [parser.parse(date) for date in prices.index]
        prices.index = dateIndex
        prices.columns = ["open", "high", "low", "close"]

        minDistance = divmod((dateIndex[2]-dateIndex[1]).total_seconds(), 60)[0]
        

        width = minDistance/24/60
        width2 = minDistance/24/60/8

        #define up and down prices
        up = prices[prices.close>=prices.open]
        down = prices[prices.close<prices.open]

        #define colors to use
        col1 = 'green'
        col2 = 'red'

        #plot up prices
        plt.bar(up.index,up.close-up.open,width,bottom=up.open,color=col1)
        plt.bar(up.index,up.high-up.close,width2,bottom=up.close,color=col1)
        plt.bar(up.index,up.low-up.open,width2,bottom=up.open,color=col1)

        #plot down prices
        plt.bar(down.index,down.close-down.open,width,bottom=down.open,color=col2)
        plt.bar(down.index,down.high-down.open,width2,bottom=down.open,color=col2)
        plt.bar(down.index,down.low-down.close,width2,bottom=down.close,color=col2)

        #rotate x-axis tick labels
        plt.xticks(rotation=45, ha='right')
"""