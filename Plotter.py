from matplotlib.pyplot import tight_layout
from pandas import DatetimeIndex
from SetUp import *

class Plotter:
    """
    --calcPeriod: period calculated for ['5m','1h','1d']
    """

    def __init__(self, rawData, timePeriod, volPlot  = True) -> None:
        
        self.volPlot = volPlot
        
        plt.rcParams['axes.facecolor'] = 'black'
        plt.rcParams['axes.edgecolor'] = 'black'
        if volPlot:
            self.fig, axes = plt.subplots(2, 1, gridspec_kw={'height_ratios': [5, 1]}, sharex=True)
            self.price_plot = axes[0]
            self.plot_vol = axes[1]
        else:
            self.fig, axes = plt.subplots(1, 1, sharex=True)
            self.price_plot = axes
        
        self.fig.set_size_inches(18, 10)
        self.fig.tight_layout()
        self.fig.subplots_adjust(hspace=0)
        
        

        self.timePeriod = timePeriod
        self.rawData = rawData

        self.selectData = self.getSpecificData()
        self.plotIndex = list(self.selectData.index)
        self.selectData.index = [parser.parse(date) for date in self.selectData.index]

        self.averageRange = (self.selectData["high"] - self.selectData["low"]).mean()

    def plot(self):
        if not self.volPlot:
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
            self.price_plot.bar(up.index,up.close-up.open,width,bottom=up.open,color=col1)
            self.price_plot.bar(up.index,up.high-up.close,width2,bottom=up.close,color=col1)
            self.price_plot.bar(up.index,up.low-up.open,width2,bottom=up.open,color=col1)

            #plot down prices
            self.price_plot.bar(down.index,down.close-down.open,width,bottom=down.open,color=col2)
            self.price_plot.bar(down.index,down.high-down.open,width2,bottom=down.open,color=col2)
            self.price_plot.bar(down.index,down.low-down.close,width2,bottom=down.close,color=col2)

        if self.volPlot:
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
            self.price_plot.bar(up.index,up.close-up.open,width,bottom=up.open,color=col1)
            self.price_plot.bar(up.index,up.high-up.close,width2,bottom=up.close,color=col1)
            self.price_plot.bar(up.index,up.low-up.open,width2,bottom=up.open,color=col1)

            #plot down prices
            self.price_plot.bar(down.index,down.close-down.open,width,bottom=down.open,color=col2)
            self.price_plot.bar(down.index,down.high-down.open,width2,bottom=down.open,color=col2)
            self.price_plot.bar(down.index,down.low-down.close,width2,bottom=down.close,color=col2)

            self.plot_vol.bar(prices.index, prices.volume, width, color = "purple", alpha = .5)
            self.plot_vol.get_yaxis().set_visible(False)

    def getSpecificData(self):
        period = str(self.timePeriod[1:])
        dataCSV = self.rawData[[period+'open', period+'high', period+'low', period+'close', period+'volume']].dropna()
        dataCSV.columns = ['open', 'high', 'low', 'close', 'volume']
        return dataCSV

    def plotLine(self, line, color = "b"):
        lineDF = line.loc[self.plotIndex]

        dateIndex = [parser.parse(date) for date in lineDF.index]

        self.price_plot.plot(dateIndex, lineDF.values, c = color)

    def plotSingleLine(self, startDate, endDate, startAnchor = "close", endAnchor = "close", color = "cyan", ls = "solid"):
        startDate = parser.parse(startDate)
        endDate = parser.parse(endDate)
        
        y1 = self.selectData.loc[startDate][startAnchor]
        y2 = self.selectData.loc[endDate][endAnchor]

        self.price_plot.plot([startDate, endDate], [y1, y2], c=color, ls=ls)


    def upArrow(self, date, y = None, color = "m"):
        date = parser.parse(date)

        if y is None:
            y = self.selectData.loc[date]["low"] - self.averageRange

        self.price_plot.scatter(date, y, c=color, marker="^")
    
    def downArrow(self, date, y = None, color = "c"):
        date = parser.parse(date)

        if y is None:
            y = self.selectData.loc[date]["high"] + self.averageRange

        self.price_plot.scatter(date, y, c=color, marker="v")

    def shadeArea(self, rangeDF, opacity, color):

        topArr = list(rangeDF.iloc[:, 0].values)
        bottomArr = list(rangeDF.iloc[:, 1].values)

        dateIndex = [parser.parse(date) for date in rangeDF.index]

        self.price_plot.fill_between(dateIndex, topArr, bottomArr, color=color, alpha=opacity)

    def show(self):
        plt.show()


"""
    class Plotter:

    def __init__(self, rawData, timePeriod, volPlot  = True) -> None:

        plt.rcParams['axes.facecolor'] = 'black'
        plt.rcParams['axes.edgecolor'] = 'black'
        plt.figure(figsize=(18, 10), tight_layout = True, dpi=80)

        self.timePeriod = timePeriod
        self.rawData = rawData

        self.selectData = self.getSpecificData()
        self.plotIndex = list(self.selectData.index)
        self.selectData.index = [parser.parse(date) for date in self.selectData.index]

        self.averageRange = (self.selectData["high"] - self.selectData["low"]).mean()

    def plot(self, volume = True):
        if volume:
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
        if volume:
            fig, axes = plt.subplots(2, 1, gridspec_kw={'height_ratios': [4, 1]}, sharex=True)
            fig.set_size_inches(18, 10)
            fig.tight_layout()
            fig.subplots_adjust(hspace=0)
            
            
            
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

            plot_price = axes[0]
            #plot up prices
            plot_price.bar(up.index,up.close-up.open,width,bottom=up.open,color=col1)
            plot_price.bar(up.index,up.high-up.close,width2,bottom=up.close,color=col1)
            plot_price.bar(up.index,up.low-up.open,width2,bottom=up.open,color=col1)

            #plot down prices
            plot_price.bar(down.index,down.close-down.open,width,bottom=down.open,color=col2)
            plot_price.bar(down.index,down.high-down.open,width2,bottom=down.open,color=col2)
            plot_price.bar(down.index,down.low-down.close,width2,bottom=down.close,color=col2)

            plot_vol = axes[1]
            plot_vol.bar(prices.index, prices.volume, width, color = "purple", alpha = .5)
            axes[1].get_yaxis().set_visible(False)

    def plotVolume(self, prices, minDistance):

        avgClose = prices.close.mean()
        print(avgClose)

        perChart = .2

        maxRange = avgClose * perChart
        maxVolume = max(prices.volume)

        plt.bar(prices.index, maxRange * prices.volume/maxVolume, width, color = "purple", alpha = .5)


    def getSpecificData(self):
        period = str(self.timePeriod[1:])
        dataCSV = self.rawData[[period+'open', period+'high', period+'low', period+'close', period+'volume']].dropna()
        dataCSV.columns = ['open', 'high', 'low', 'close', 'volume']
        return dataCSV

    def plotLine(self, line, color = "b"):
        lineDF = line.loc[self.plotIndex]

        dateIndex = [parser.parse(date) for date in lineDF.index]

        plt.plot(dateIndex, lineDF.values, c = color)

    def plotSingleLine(self, startDate, endDate, startAnchor = "close", endAnchor = "close", color = "cyan", ls = "solid"):
        startDate = parser.parse(startDate)
        endDate = parser.parse(endDate)
        
        y1 = self.selectData.loc[startDate][startAnchor]
        y2 = self.selectData.loc[endDate][endAnchor]

        plt.plot([startDate, endDate], [y1, y2], c=color, ls=ls)


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