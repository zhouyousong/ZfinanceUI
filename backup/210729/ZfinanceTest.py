import Zfinance as zf
import Zplot as zp
import seaborn as sns

# MarketQuotations
#     |----GetYesterdayData
#     |----GetCurrentData
#     |-SingleStockQuotations
#       |--DownloadHistoryData*(要支持到分钟下载和断点)
#     |-ETFQuotations
#       |--GetConstituentStockList
#       |--DownloadHistoryData*(要支持到分钟下载和断点)
#     |-IndexQuotations
#       |--DownloadHistoryData*(要支持到分钟下载和断点)

# StockExchangeQuotations
#     |--DownloadHistoryData
#     |--DownloadCurrentData

# Analyzer
#     |----PickupColums
#     |----ListColumItems
#     |----PickupConditionColums
#     |----SortItems
#     |----CalcBySorts*


Ztimelog = zf.Logtime("Start")
AAPLDATA = zf.TickerAnalyzer.DailyTradeCHG('AAPL', Interval='15m')
BABADATA = zf.TickerAnalyzer.DailyTradeCHG('BABA', Interval='15m')
BABACondition = [
    {'Indicator': zf.Indicator.CHG, 'IndicatorParams':  {'Duration': 10},'CompMethod': zf.Comp.GTT,
     'CompVal': 10, 'Occurrence': {'andTorF': True, 'OccurrenceDate': [-2, -1,0]}},
    {'Indicator': zf.Indicator.MACD, 'IndicatorParams': {'Duration': 10}, 'CompMethod': zf.Comp.SMT,
     'CompVal': 1,  'Occurrence': {'andTorF': True, 'OccurrenceDate': [-1, 0]}},
    {'Indicator': zf.Indicator.RSI, 'IndicatorParams':  {'Duration': 10}, 'CompMethod': zf.Comp.GTT,
     'CompVal': 60,  'Occurrence': {'andTorF': True, 'OccurrenceDate': [0]}},
]


Ztimelog.Dtime("QQQA")
BABADATA = zf.TickerAnalyzer.CondFilter('BABA', Condition=BABACondition, Period=300)
Ztimelog.Dtime("QQQB")
# zp.ZBar.OnDFBarPlot(AAPLDATA,TitleName = 'TRY')
Ztimelog.Dtime("YY")
zp.ZBar.OnDFsBarPlot([AAPLDATA, BABADATA], TitleName='TRY')
IXIC = zf.IndexQuotations('^IXIC')
IXIC.DownloadHistoryData()
Ztimelog.Dtime("IXIC")
QQQ = zf.ETFQuotations('QQQ')
QQQ.DownloadHistoryData()
Ztimelog.Dtime("QQQ")
AAPL = zf.SingleStockQuotations('AAPL')
AAPL.DownloadHistoryData()
Ztimelog.Dtime("AAPL")
# AMEX=zf.StockExchange('AMEX')
# AMEX.DownloadStockHistoryPrice()
# AMEX.DownloadStockCurrentPrice()
#
# NASDAQ=zf.StockExchange('NASDAQ')
# NASDAQ.DownloadStockHistoryPrice()
# NASDAQ.DownloadStockCurrentPrice()
#
# NYSE=zf.StockExchange('NYSE')
# NYSE.DownloadStockHistoryPrice()
# NYSE.DownloadStockCurrentPrice()

# QQQ= zf.ETFQuotations('QQQ')
# A=QQQ.GetYesterdayData()
# B=QQQ.GetCurrentData()
# QQQ.DownloadHistoryData()
# QQQlist = QQQ.GetConstituentStockList()

# GSPC = zf.IndexQuotations('^GSPC')
# GSPC.DownloadHistoryData()
# IXIC = zf.IndexQuotations('^IXIC')
# IXIC.DownloadHistoryData()
# DJI = zf.IndexQuotations('^DJI')
# DJI.DownloadHistoryData()
#
# Ztimelog =zf.Logtime("Start")
# Exchanges = ['NYSE','NASDAQ','AMEX']
# Ztimelog.Dtime("A")
#
# USAMarket = zf.Analyzer(Exchanges)
# Ztimelog.Dtime("Exchanges")
# x = USAMarket.PickupColums(['marketCap','volume','sector','industry','country','state','exchange'],inplace=True)
# Ztimelog.Dtime("PickupColums")
# SI = USAMarket.ListColumItems(['sector','industry'])
# Ztimelog.Dtime("ListColumItems")
# txtx=USAMarket.CalcBySorts(SI,CalcIndex = ['marketCap','volume'],inplace=True)
# Ztimelog.Dtime("CalcBySorts")
# A =USAMarket.SortItems(ColumnIndex=['Sum of marketCap'],Largest= True,Top=20)
# B =USAMarket.SortItems(ColumnIndex=['Avg of marketCap'],Largest= True,Top=20)
# Ztimelog.Dtime("SortItems")
# Country = USAMarket.ListColumItems('country')
# Ztimelog.Dtime("country")
# Country = USAMarket.PickupConditionColums(ColumnIndex ='country',Condition=['China','Taiwan'],inplace=True)
# Ztimelog.Dtime("E")
# a =USAMarket.SortItems(ColumnIndex=['marketCap'],Largest= True,Top=20)
# Ztimelog.Dtime("F")
# print(x)
