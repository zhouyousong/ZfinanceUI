import copy
# import matplotlib.pyplot as plt
# from matplotlib.font_manager import FontProperties
import talib
import yfinance as yf
import pandas as pd
import numpy as np
import pathlib
from ZfinanceCfg import PROXYEN
from ZfinanceCfg import EXTENDLEN
import os
import math
import csv
import time,datetime
from enum import Enum

class Indicator(Enum):
    NULL = 1
    CHG = 2
    RVI = 3
    RSI = 4
    MACD = 5
    KDJ = 6
class Comp(Enum):
    GTT  = 1
    GTTE = 2
    SMT  = 3
    SMTE = 4
    EQ   = 5

# MarketQuotationsData
#     |-01_Ticker&ETFList
#     |-02_IndexData
#     |-03_EFTData
#     |-04_SingleStockData
#     |-05_ExchangeData
#         |-01_NYSE_Exchange
#         |-02_NASDAQ_Exchange
#         |-03_AMEX_Exchange
#     |-06_Analyzer

# MarketQuotations
#     |----GetYesterdayData
#     |----GetCurrentData
#     |-SingleStockQuotations
#       |--DownloadHistoryData
#     |-ETFQuotations
#       |--GetConstituentStockList
#       |--DownloadHistoryData
#     |-IndexQuotations
#       |--DownloadHistoryData
# StockExchangeQuotations
#     |--DownloadHistoryData
#     |--DownloadCurrentData

# Analyzer
#     |----PickupColums
#     |----ListColumItems
#     |----PickupConditionColums
#     |----SortItems

# TickerAnalyzer
#     |----DailyRnF


def ChangeRatio(Start, End):
    return (End - Start)/Start*100
#------------------个股分析----------------------------
def get_EMA(df,N):
    df['EMA'] = 0
    for i in range(len(df)):
        if i==0:
            df.iloc[i,df.columns.get_loc('EMA')]=df.iloc[i,df.columns.get_loc('Close')]
        if i>0:
            df.iloc[i,df.columns.get_loc('EMA')]=(2*df.iloc[i,df.columns.get_loc('Close')]+(N-1)*df.iloc[i-1,df.columns.get_loc('EMA')])/(N+1)
    ema=list(df['EMA'])
    return ema
def get_MACD(df,short=12,long=26,M=9):
    a=get_EMA(df,short)
    b=get_EMA(df,long)
    df['diff']=(pd.Series(a)-pd.Series(b)).tolist()
    df['dea'] = 0
    #print(df['diff'])
    for i in range(len(df)):
        if i==0:
            df.iloc[i,df.columns.get_loc('dea')]=df.iloc[i,df.columns.get_loc('diff')]
        if i>0:
            df.iloc[i,df.columns.get_loc('dea')]=(2*df.iloc[i,df.columns.get_loc('diff')]+(M-1)*df.iloc[i-1,df.columns.get_loc('dea')])/(M+1)
    df['macd']=(df['diff']-df['dea'])
    return df

def CHGfunc(DailyHistoryData,TempIndicatorParams,i):
    PopNum = TempIndicatorParams['Duration']
    LastCloseNewOpen = DailyHistoryData['Close'].tolist()
    Temp = LastCloseNewOpen[0 :PopNum]
    del LastCloseNewOpen[-(PopNum + 0):]
    Temp.extend(LastCloseNewOpen)
    LastCloseNewOpen = Temp
    NewColStr = str(PopNum)+'DaysAgoClose_['+str(i)+']'
    DailyHistoryData[NewColStr] = LastCloseNewOpen
    DailyHistoryData[str(PopNum)+'DaysChangeRate_['+str(i)+'*]'] = DailyHistoryData.apply(lambda col: ChangeRatio(col[NewColStr], col['Close']), axis=1)
    return DailyHistoryData
def MACDfunc(DailyHistoryData,TempIndicatorParams,i):
    #get_MACD(DailyHistoryData, 12, 26, 9)
    MACD_macd, MACD_macdsignal, MACD_macdhist = talib.MACD(DailyHistoryData["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
    DailyHistoryData['MACD_macd_['+str(i)+']']       =MACD_macd
    DailyHistoryData['MACD_macdsignal_['+str(i)+']'] =MACD_macdsignal
    DailyHistoryData['MACD_macdhist_['+str(i)+'*]']   =MACD_macdhist
    return DailyHistoryData
def RSIfunc(DailyHistoryData,TempIndicatorParams,i):
    rsi = talib.RSI(DailyHistoryData["Close"],timeperiod = 14)
    DailyHistoryData['RSI_['+str(i)+'*]'] = rsi
    return DailyHistoryData
class TickerAnalyzer:
    def DailyTradeCHG(Ticker = '',Interval = '1h'):  #日内涨跌

        TickerPath = 'MarketQuotationsData/04_SingleStockData/'+Ticker+'/'+Ticker+'_'+Interval+'.csv'
        HourHistoryData=pd.read_csv(TickerPath)
        HourHistoryData.drop(columns=['Dividends', 'Stock Splits'],inplace = True)
        HourHistoryData['Date'] = HourHistoryData['DateTime'].map(lambda x:x.split(' ')[0])
        HourHistoryData['TimeTemp'] = HourHistoryData['DateTime'].map(lambda x:x.split(' ')[1])
        HourHistoryData['Time'] = HourHistoryData['TimeTemp'].map(lambda x: x.split('-')[0])
        Date = HourHistoryData['Date']
        Time = HourHistoryData['Time']
        HourHistoryData.drop(['DateTime','TimeTemp','Date','Time'],axis=1,inplace=True)
        HourHistoryData.insert(0,'Time',Time)
        HourHistoryData.insert(0,'Date',Date)
        HourHistoryData['ChangeRate'] = 1
        #滤掉12:32:23这种偶尔出现的时间的数据
        Temp = HourHistoryData.value_counts('Time')
        for Index, Row in Temp.to_frame().iterrows():
            if Row.iloc[0] < 10:
                HourHistoryData.drop(index=(HourHistoryData.loc[(HourHistoryData['Time']==Index)].index),inplace= True)
        TempA = HourHistoryData.value_counts('Date',ascending= True).to_frame()
        TemplateDate = TempA.index.tolist()[-1]
        TempB = TempA.value_counts(ascending= False).to_frame()
        #滤掉某天中时间不完整的时间
        i = 0
        for Index, Row in TempB.iterrows():
            i = i+1
            if i > 2:
                TempC = TempA.loc[TempA.iloc[:,0].isin([Index[0]])]
                for IndexC, RowC in TempC.iterrows():
                    HourHistoryData.drop(index=(HourHistoryData.loc[(HourHistoryData['Date'] == IndexC)].index),
                                         inplace=True)
        Temp = HourHistoryData.loc[HourHistoryData['Date'].isin([TemplateDate])]

        flag = 1
        ColorDict = {}
        for Index, Row in Temp.iterrows():
            if flag == 1:
                if Row['Volume'] == 0:
                    ColorDict[Row['Time']] = 'red'
                else:
                    flag = 0
                    ColorDict[Row['Time']] = 'pink'
            else:
                if Row['Volume'] !=0:
                    ColorDict[Row['Time']] = 'pink'
                else:
                    ColorDict[Row['Time']] = 'green'
        HourHistoryData['ChangeRate']
        LastCloseNewOpen  = HourHistoryData['Close'].tolist()
        Temp = HourHistoryData.iloc[0,2]
        LastCloseNewOpen.pop(-1)
        LastCloseNewOpen.insert(0, Temp)
        HourHistoryData['NewOpen'] = LastCloseNewOpen
        HourHistoryData['ChangeRate'] = HourHistoryData.apply(lambda col: ChangeRatio(col['NewOpen'], col['Close']), axis=1)
        HourHistoryData.to_csv('MarketQuotationsData/04_SingleStockData/'+Ticker+'/'+Ticker+'_'+Interval+'_Processed .csv',index = False)
        Ticker = {
            'TickerName':Ticker,
            'Dataframe' :HourHistoryData,
            'StageColor': ColorDict,
            'CompVals':['ChangeRate']
        }
        return Ticker
    def CondFilter(Ticker = '',Condition =[],Period = 300):
        FuncSwitcher = {
            Indicator.CHG:  CHGfunc,
            Indicator.MACD: MACDfunc,
            Indicator.RSI:  RSIfunc
        }

        TickerPath = 'MarketQuotationsData/04_SingleStockData/'+Ticker+'/'+Ticker+'_1d.csv'
        DailyHistoryData=pd.read_csv(TickerPath)
        DailyHistoryData = DailyHistoryData.iloc[-(Period+EXTENDLEN):]       #多取100天历史周期
        j=0
        for iCondtion in Condition:
            j = j+1
            TempIndicator           = iCondtion['Indicator']
            TempIndicatorParams     = iCondtion['IndicatorParams']

            DailyHistoryData = FuncSwitcher[TempIndicator](DailyHistoryData,TempIndicatorParams,j)
        DailyHistoryData = DailyHistoryData[EXTENDLEN:]
        j = 0
        for iCondtion in Condition:
            j = j+1
            TempCompMethod          = iCondtion['CompMethod']
            TempCompVal             = iCondtion['CompVal']

            Sign = str(j)+'*'

            List = DailyHistoryData.iloc[0,].index.tolist()
            for i in List:
                if Sign in i:
                    IndStr = i
                    break
            if TempCompMethod == Comp.GTT:
                result = DailyHistoryData[DailyHistoryData[IndStr] >  TempCompVal]
            if TempCompMethod == Comp.GTTE:
                result = DailyHistoryData[DailyHistoryData[IndStr] >= TempCompVal]
            if TempCompMethod == Comp.SMT:
                result = DailyHistoryData[DailyHistoryData[IndStr] <  TempCompVal]
            if TempCompMethod == Comp.SMTE:
                result = DailyHistoryData[DailyHistoryData[IndStr] <= TempCompVal]
            if TempCompMethod == Comp.EQ:
                result = DailyHistoryData[DailyHistoryData[IndStr] == TempCompVal]

            result.loc[:,'['+Sign+']'] = True

            DailyHistoryData['['+Sign+']'] = result['['+Sign+']']
            Temp = DailyHistoryData['[' + Sign + ']'].fillna(False)
            DailyHistoryData['[' + Sign + ']'] = Temp

        j = 0
        for iCondtion in Condition:
            j = j+1
            TempOccurrence          = iCondtion['Occurrence']
            LenDn = min(TempOccurrence['OccurrenceDate'])
            OcLen = 1 - LenDn
            Oc_list = [False for i in range(OcLen)]
            for i in TempOccurrence['OccurrenceDate']:
                Oc_list[i - LenDn] = True

            Sign = '['+str(j) + '*]'
            CompList = DailyHistoryData[Sign].tolist()
            CompCycle = len(CompList) - OcLen + 1
            ResultList = [False for i in range(OcLen-1)]
            for i in range(0,CompCycle):
                subcomplist = CompList[i:i+OcLen]
                if subcomplist == Oc_list:
                    ResultList.append(True)
                else:
                    ResultList.append(False)
            Sign = '[*' + str(j) + '*]'
            DailyHistoryData[Sign] = ResultList

        result = DailyHistoryData
        j = 0
        for iCondtion in Condition:
            j = j+1
            Sign = '[*' + str(j) + '*]'
            result = result[result[Sign] == True]
        return DailyHistoryData,result

#------------------记录时间----------------------------
class Logtime:
    def __init__(self,str=''):
        self.StartTime = int(round(time.time()*1000))
        print("%s:%d"%(str,self.StartTime))

        timeArray = time.localtime(self.StartTime/1000)
        StartTimestring = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        print(StartTimestring)
        return
    def Dtime(self,str=''):
        TempTime = int(round(time.time()*1000))
        print("%s:%dms"%(str,(TempTime - self.StartTime)))
        self.StartTime = TempTime
        return
#------------------分析行情数据----------------------------
class Analyzer:

    def __init__(self, ExchangesList=[]):
        switcher= {
            'NYSE': "MarketQuotationsData/05_ExchangeData/NYSE.csv",
            'NASDAQ': "MarketQuotationsData/05_ExchangeData/NASDAQ.csv",
            'AMEX': "MarketQuotationsData/05_ExchangeData/AMEX.csv",
        }
        self.TickersDataFrame = pd.read_csv(switcher[ExchangesList[0]])
        self.TickersDataFrame.set_index(['symbol'], inplace=True)
        self.TickersDataFrame['EM'] = ExchangesList[0]
        for Exchange in ExchangesList[1:]:
            TempTable = pd.read_csv(switcher[Exchange])
            TempTable.set_index(['symbol'], inplace=True)
            TempTable['EM'] = Exchange
            self.TickersDataFrame = self.TickersDataFrame.append(TempTable)
        self.TickersDataFrame.replace({'&': 'and'}, regex=True,inplace= True)
        return
    # ------------------挑出感兴趣的行----------------------------
    def PickupColums(self,ColumnIndex=['marketCap','twoHundredDayAverage','sector','industry','state','EM','exchange'],inplace = False):
        Temp=self.TickersDataFrame[ColumnIndex]
        if inplace is True:
            self.TickersDataFrame = Temp
        return Temp
    # ------------------列出某几行的元素排列组合种类和个数----------------------------
    def ListColumItems(self,ColumnIndex=['state','Exchange']):
        Temp = self.TickersDataFrame[ColumnIndex].fillna('-',)
        Temp=Temp.value_counts(ColumnIndex)
        Tempdict = {'Indexs':ColumnIndex,'List': Temp}
        return Tempdict
    # ------------------过滤出单列满足某个条件的行----------------------------
    def PickupConditionColums(self,ColumnIndex='state',Condition = ['CA','LA'],inplace = False):
        Temp = self.TickersDataFrame.loc[self.TickersDataFrame[ColumnIndex].isin(Condition)]
        if inplace is True:
            self.TickersDataFrame = Temp
        return Temp
    # ------------------对某列进行排序top----------------------------
    def SortItems(self,ColumnIndex=['marketCap'],Largest = True,Top = None,inplace = False):
        if Largest is True:
            if Top is None:
                Temp = self.TickersDataFrame.sort_values(ColumnIndex,ascending= False)
            else:
                Temp = self.TickersDataFrame.nlargest(Top,ColumnIndex)
        else:
            if Top is None:
                Temp = self.TickersDataFrame.sort_values(ColumnIndex,ascending= True)
            else:
                Temp = self.TickersDataFrame.nsmallest(Top,ColumnIndex)

        if inplace is True:
            self.TickersDataFrame = Temp
        return Temp
    # ------------------对某列进行排序top----------------------------
    def CalcBySorts(self,S ={},CalcIndex=['marketCap'],inplace = False):
        P = S['Indexs']
        Q = S['List']
        R = Q.to_frame()
        R.columns=['count']
        R[('Sum of '+CalcIndex[0])]=0
        for i in CalcIndex:
            R[('Sum of ' + i)] = 0
            R[('Avg of ' + i)] = 0
            R[('Cov of ' + i)] = 0
        for i,v in Q.items():
            Temp = self.TickersDataFrame[P[0]].isin([i[0]])
            Count = 1
            for j in i[1:]:
                Temp = self.TickersDataFrame[P[Count]].isin([j])&Temp
                Count+=1
            Temp = self.TickersDataFrame.loc[Temp]
            for j in CalcIndex:
                TempSum = Temp[j].sum()
                TempAvg = Temp[j].mean()
                TempCov = Temp[j].var()
                R.loc[i, 'Sum of ' + j] = TempSum/1000000
                R.loc[i, 'Avg of ' + j] = TempAvg/1000000
                R.loc[i, 'Cov of ' + j] = TempCov/1000000

        if inplace is True:
            self.TickersDataFrame = R
        return R
# ------------------获取行情数据----------------------------
class MarketQuotations:
    def __init__(self,symbolstring = ''):
        self.symbolstr = symbolstring
        self.symbol = yf.Ticker(self.symbolstr).get_balancesheet()
        self.symbol.info

        return
    #-------------------获取数据'
    def FetchHistoryData(self,start = None,period=None,interval='15m',PROXY=None):
        return self.symbol.history(start = start,period=period, prepost=True, interval=interval, proxy=PROXY)
    # ------------------获取行情数据（获取指数昨天信息）----------------------------
    def GetYesterdayData(self,interval='15m'):
        YesterdayData = self.symbol.history(period='1d',prepost = True,interval=interval,proxy=PROXYEN)
        return YesterdayData
    # ------------------获取行情数据（获取指数当前信息）----------------------------
    def GetCurrentData(self):
        CurrentData = self.symbol.get_info(proxy=PROXYEN)
        return CurrentData
    # ------------------获取单个数据（获取历史数据）----------------------------
    def DownloadHistoryData(self):  # 下载指数历史走势数据

        DailyHistoryData = self.symbol.history(period = 'max',interval='1d',proxy=PROXYEN,prepost=True)

        StartTimestamp = time.time() - 729*24*60*60
        timeArray = time.localtime(StartTimestamp)
        StartTimestring = time.strftime("%Y-%m-%d", timeArray)
        HourHistoryData = self.symbol.history(interval='1h',start=StartTimestring,proxy=PROXYEN,prepost=True)

        StartTimestamp = time.time() - 59*24*60*60
        timeArray = time.localtime(StartTimestamp)
        StartTimestring = time.strftime("%Y-%m-%d", timeArray)
        Min15HistoryData = self.symbol.history(interval='15m',start=StartTimestring,proxy=PROXYEN,prepost=True)


        DailyHistoryData = round(DailyHistoryData, 5)
        HourHistoryData = round(HourHistoryData, 5)
        Min15HistoryData = round(Min15HistoryData, 5)

        dirpath = self.RootDir+self.symbolstr+'/'
        path = pathlib.Path(dirpath)
        if path.exists() is False:
            os.makedirs(path)
            DailyHistoryData.to_csv(dirpath + self.symbolstr + '_1d.csv', sep=',',index_label='DateTime')
            HourHistoryData.to_csv(dirpath + self.symbolstr + '_1h.csv', sep=',',index_label='DateTime')
            Min15HistoryData.to_csv(dirpath + self.symbolstr + '_15m.csv', sep=',',index_label='DateTime')
        else:
            ExistDailyHistoryData = pd.read_csv(dirpath + self.symbolstr + '_1d.csv')
            ExistHourHistoryData  = pd.read_csv(dirpath + self.symbolstr + '_1h.csv')
            ExistMin15HistoryData = pd.read_csv(dirpath + self.symbolstr + '_15m.csv')

            DailyHistoryData.to_csv(dirpath + self.symbolstr + '_1d.tmp.csv', sep=',',index_label='DateTime')
            HourHistoryData.to_csv(dirpath + self.symbolstr + '_1h.tmp.csv', sep=',',index_label='DateTime')
            Min15HistoryData.to_csv(dirpath + self.symbolstr + '_15m.tmp.csv', sep=',',index_label='DateTime')

            TempDailyHistoryData = pd.read_csv(dirpath + self.symbolstr + '_1d.tmp.csv')
            os.remove(dirpath + self.symbolstr + '_1d.tmp.csv')
            TempHourHistoryData  = pd.read_csv(dirpath + self.symbolstr + '_1h.tmp.csv')
            os.remove(dirpath + self.symbolstr + '_1h.tmp.csv')
            TempMin15HistoryData = pd.read_csv(dirpath + self.symbolstr + '_15m.tmp.csv')
            os.remove(dirpath + self.symbolstr + '_15m.tmp.csv')

            DailyHistoryData = ExistDailyHistoryData.append(TempDailyHistoryData)
            DailyHistoryData.drop_duplicates(subset='DateTime', keep='first', inplace=True)
            DailyHistoryData.set_index(['DateTime'], inplace=True)
            DailyHistoryData.to_csv(dirpath + self.symbolstr + '_1d.csv', sep=',')

            HourHistoryData = ExistHourHistoryData.append(TempHourHistoryData)
            HourHistoryData.drop_duplicates(subset='DateTime', keep='first', inplace=True)
            HourHistoryData.set_index(['DateTime'], inplace=True)
            HourHistoryData.to_csv(dirpath + self.symbolstr + '_1h.csv', sep=',')

            Min15HistoryData = ExistMin15HistoryData.append(TempMin15HistoryData)
            Min15HistoryData.drop_duplicates(subset='DateTime', keep='first', inplace=True)
            Min15HistoryData.set_index(['DateTime'], inplace=True)
            Min15HistoryData.to_csv(dirpath + self.symbolstr + '_15m.csv', sep=',')

        return
# ------------------获取个股数据----------------------------
class SingleStockQuotations(MarketQuotations):
    def __init__(self, symbolstring=''):
        self.RootDir = 'MarketQuotationsData/04_SingleStockData/'
        self.symbolstr = symbolstring
        self.symbol = yf.Ticker(self.symbolstr)
# ------------------获取ETF数据----------------------------
class ETFQuotations(MarketQuotations):
    def __init__(self, symbolstring=''):
        self.RootDir = 'MarketQuotationsData/03_EFTData/'
        self.symbolstr = symbolstring
        self.symbol = yf.Ticker(self.symbolstr)
    # ------------------获取行情数据（获取ETF成分股票）----------------------------
    def GetConstituentStockList(self):  # 获取成分股列表
        switcher = {
            'QQQ':["https://en.wikipedia.org/wiki/Nasdaq-100",3,'Ticker'],
            'SPY':["https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",0,'Symbol'],
        }
        table = pd.read_html(switcher[self.symbolstr][0])
        ConstituentStockList = table[switcher[self.symbolstr][1]][switcher[self.symbolstr][2]].tolist()
        return ConstituentStockList
    # ------------------获取行情数据（获取ETF历史数据）----------------------------
    # def DownloadHistoryData(self):  # 下载指数历史走势数据
    #     IndexHistoryData = self.symbol.history(period='max',proxy=PROXYEN)
    #     FileName = self.symbolstr.replace('^','') + '.csv'
    #     IndexHistoryData.to_csv('MarketQuotationsData/03_EFTData/'+FileName, sep=',')
    #     return
# ------------------获取Index数据----------------------------
class IndexQuotations(MarketQuotations):
    def __init__(self, symbolstring=''):
        self.RootDir = 'MarketQuotationsData/02_IndexData/'
        self.symbolstr = symbolstring
        self.symbol = yf.Ticker(self.symbolstr)
    # ------------------获取行情数据（获取Index历史数据）----------------------------
    # def DownloadHistoryData(self):  # 下载指数历史走势数据
    #     IndexHistoryData = self.symbol.history(period='max',proxy=PROXYEN)
    #     FileName = self.symbolstr + '.csv'
    #     IndexHistoryData.to_csv('MarketQuotationsData/02_IndexData/'+FileName, sep=',')
# ------------------获取交易所数据---------------------------
def GetExchangeSymbolList(Exchange = ''):
    switcher = {
        'NYSE': 'MarketQuotationsData/01_ETF&IndexTickerList/NYSE_TickerList.csv',
        'NASDAQ': 'MarketQuotationsData/01_ETF&IndexTickerList/NASDAQ_TickerList.csv',
        'AMEX': 'MarketQuotationsData/01_ETF&IndexTickerList/AMEX_TickerList.csv'
    }
    list = (pd.read_csv(switcher[Exchange]))
    delIndex = []
    for i in list.index:
        if '^' in list['Symbol'][i] or '/' in list['Symbol'][i]:
            delIndex.append(i)
    list.drop(index=delIndex, inplace=True)
    return list['Symbol'].tolist()

class StockExchange:
    def __init__(self, Exchange=''):
        switcher = {
            'NYSE':['MarketQuotationsData/01_ETF&IndexTickerList/NYSE_TickerList.csv','MarketQuotationsData/05_ExchangeData/01_NYSE_Exchange'],
            'NASDAQ':['MarketQuotationsData/01_ETF&IndexTickerList/NASDAQ_TickerList.csv','MarketQuotationsData/05_ExchangeData/02_NASDAQ_Exchange'],
            'AMEX':['MarketQuotationsData/01_ETF&IndexTickerList/AMEX_TickerList.csv', 'MarketQuotationsData/05_ExchangeData/03_AMEX_Exchange'],
        }
        self.Exchange = Exchange
        self.list = (pd.read_csv(switcher[Exchange][0]))
        delIndex = []
        for i in self.list.index:
            if '^' in self.list['Symbol'][i] or '/' in self.list['Symbol'][i]:
                delIndex.append(i)
            try:
                if '/' in self.list['Sector'][i]:
                    self.list['Sector'][i] = self.list['Sector'][i].replace('/', '&')
                if '/' in self.list['Industry'][i]:
                    self.list['Industry'][i] = self.list['Industry'][i].replace('/', '&')
            except:
                pass
        self.list.drop(index=delIndex, inplace=True)
        self.SymoblListOfExchange = self.list['Symbol'].tolist()
        self.FilePath = switcher[Exchange][1]
        return
    # ------------------交易所操作(获取该交易所所有股票历史数据)---------------------------
    def DownloadStockHistoryPrice(self):  # 获取历史数据

        RatioOfProcess = 0;
        for SymbolString in self.SymoblListOfExchange:
            RatioOfProcess = RatioOfProcess + 1

            StockDataFilename = self.FilePath + '/' + SymbolString + '.csv'
            path = pathlib.Path(StockDataFilename)
            StockHistoryPriceData = []
            if path.exists() is False:  # 如果文件存在，不重复下载
                try:
                    pathlib.Path(path).touch()
                    StockHistoryPriceData = yf.download(SymbolString, period='max',proxy=PROXYEN)
                except:
                    print("%s Download Failed!" %SymbolString)
                    os.remove(path)

                StockHistoryPriceData.to_csv(StockDataFilename, sep=',')
            print("Ratio = %d/%d SI :%s" % (
            RatioOfProcess, len(self.SymoblListOfExchange), StockDataFilename + " Download Finished !!"))

        return
    # ------------------交易所操作(获取该交易所所有股票当前数据放一个表中)---------------------------
    def DownloadStockCurrentPrice(self):  # 获取当前数据

        RatioOfProcess = 0;
        TickersCurrentInfo = []
        Flag = False
        FailNum = 0

        TempFilePath = 'MarketQuotationsData/05_ExchangeData/' + self.Exchange + '.csv'
        path = pathlib.Path(TempFilePath)
        if path.exists():
            TickersDataFrame = pd.read_csv(TempFilePath)
            TickersDataFrame.set_index(['symbol'], inplace=True)
            ExistedSymbol = TickersDataFrame.index.tolist()
            Flag = True
        else:
            ExistedSymbol = []

        for SymbolString in self.SymoblListOfExchange:
            RatioOfProcess = RatioOfProcess + 1

            if SymbolString in ExistedSymbol:
                print("Ratio = %d/%d Ticker:%s" % (RatioOfProcess, len(self.SymoblListOfExchange), SymbolString + " Already Existed !!"))
            else:
                Ticker = yf.Ticker(SymbolString)
                try:
                    Ticker.info
                    TickerCurrentInfo = Ticker.get_info()
                    if Flag is False:
                        TickersDataFrame = pd.DataFrame(TickerCurrentInfo)
                        TickersDataFrame.set_index(['symbol'], inplace=True)
                        Flag = True

                    TempTickersDataFrame = pd.DataFrame([TickerCurrentInfo])
                    TempTickersDataFrame.set_index(['symbol'], inplace=True)

                    TickersDataFrame = TickersDataFrame.append(TempTickersDataFrame)
                    print("Ratio = %d/%d Ticker:%s" % (RatioOfProcess, len(self.SymoblListOfExchange), SymbolString + " Get info Finished !!"))
                    if RatioOfProcess%5 == 0:
                        print("Save for Once")
                        TickersDataFrame.to_csv('MarketQuotationsData/05_ExchangeData/' + self.Exchange + '.csv',sep=',')
                except:
                    print("Ratio = %d/%d Ticker:%s  Get info Failed !! FailNum = %d" % (RatioOfProcess, len(self.SymoblListOfExchange), SymbolString ,FailNum ))
                    FailNum =FailNum+1
                    if FailNum >= 50:
                        print("Download Failed cause network,please restart the program")
                        break


        TickersDataFrame.to_csv('MarketQuotationsData/05_ExchangeData/'+self.Exchange+'.csv', sep=',')
