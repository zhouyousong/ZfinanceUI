from enum import Enum
PROXYEN = None
EXTENDLEN = 100
DownloadDefualtCfg = {
    "PROXYEN": 'http://127.0.0.1:7890',
    'Intervial_1Day_x':True,
    'Intervial_1h_x':True,
    'Intervial_30min_x':True,
    'Intervial_15min_x':True,
    'Intervial_5min_x':True,
    'Intervial_1min_x':True,

    'FunAna_Info_x':True,
    'FunAna_Financials_x':True,
    'FunAna_Balancesheet_x':True,
    'FunAna_Cashflow_x':True,
    'FunAna_Dividends_x':True,
    'FunAna_Splits_x':True,

    'DownloadPeriod_x' : 10,
    'MulitThreadDL_x':5,
    'ReConnectCnt_x':2,
    'TimeOut_x':10,

    'SkipPeriod_x':0,
    'SkipNG_x':True,

    "EX_CN-SHZ_x": True,
    "EX_HK_x": True,
    "EX_US-ASE_x": True,
    "EX_US-NYQ_x": True,
    "EX_US-NMS_x": True,
    "EX_FAVOR_x": True
}

PeriodDict={
    'PeriodStr' : ["1 Day", "5 Days", '60 Days', '90 Days', '180 Days', '1 Years',
                 '2 Years', "5 Years", '10 Years' ,'MAX'],
    'PeriodStrPara' : ["1d", "5d", '60d', '3mo', '6mo', '1y',
                 '2y', "5y", '10y', 'max'],
    'Period2Days': [1, 4, 50, 80, 160, 340,
                      700, 1700, 3500,  -1]
}
PreviewPeriodList=[10,20,60,120,240,480,960,1200,2400,-1]
MulitThreadList_c = ['1','3','5','10','20','40','60','100']
SkipPeriodList_c = ['0','3','6','9','12','15','18','21']
ReConnectList_c = ['1','3','5','10','20']
TimeOutList_c = ['5','10','20','30','60']

class TradingStatu(Enum):
    Buy         = 0
    Hold        = 1
    LockSell    = 2
    Sell        = 3
    Watch       = 4
    LockBuy     = 5

class TrendMode(Enum):
    UP          = 0
    DN          = 1
    NO          = 2

BackTestTableColumeItem = ['Start', 'End', 'FlPL', 'StdPL', 'FixPL']
MonitorAndTradeTableColumeItem = ['Mark', 'Status', 'Trade On/Off']
BalanceTableColumeItem = ['P/L Day', 'P/L Open', 'Cost', 'Mark', 'P/L %', 'Net Liq']

DebugStatusStr = {
                    TradingStatu.Buy:['Buy','green'],
                    TradingStatu.Hold:['Hold','lightgreen'],
                    TradingStatu.LockSell:['LockSell','peru'],
                    TradingStatu.Sell:['Sell','red'],
                    TradingStatu.Watch:['Watch','blue'],
                    TradingStatu.LockBuy:['LockBuy','violet']
}

BackTestPara = {
                    "ProcessConfig": {
                        "ProcessorCnt": 4,
                    },
                    "BackTestDayCount": {
                        "Length": int(180),
                    },
                    "AEMATP":{
                        "Length1":int(8),
                        "Length2":int(21),
                        "Length3":int(50),
                        "Length4":int(144),
                        "Length5":int(200),
                        "Length6":int(350)
                    },
                    "RSI":{
                        "Enable":True,
                        "RSI1":{
                            "Length":int(21),
                            'OverBuy':int(80),
                            "OverSell":int(20),
                        },
                        "RSI2":{
                            "Enable":False,
                            "Length":int(21),
                        },
                        "RSI3": {
                            "Enable": True,
                            "Length": int(50),
                        }
                    },
                    "P/L":{
                        "FloatPL":{
                            "Enable":True
                        },
                        "StanderPL":{
                            "Enable":False
                        },
                        "FixedPL": {
                            "Enable": True
                        },
                        "Index": {
                            "Enable": True
                        }
                    },
                    "Trading":{
                        "Enable":False,
                        "TrendGate": 0.0008,
                        "ClosureRatio": 0.15,
                        "LastIndex":3,

                        "TrendDnRatio":63,
                        "TrendDnRatioLen":int(230),

                        "RSISellLimit":float(78),
                        'TrendUp':{
                            "RaiseScale":1.0,
                            'FallScale':0.98,
                            "Elimit": int(2)
                        },
                        'TrendDn':{
                            "RaiseScale": 1.0,
                            'FallScale': 0.98,
                            "Elimit": int(2),
                        },
                        'TrendNo':{
                        "RaiseScale": 1.0,
                        'FallScale': 0.98,
                        "Elimit": int(2),
                        },
                        "lastIndex":int(3),
                        "LockBuyLen":int(10),
                        "StopLossRate":95.8,


                        'RaiseScale':1.01,
                        'FallScale':0.98

                    },
                    "WebPage": {
                        "Save": False,
                        "AutoOpen": True
                    }





}

class TableColor(Enum):
    Green   = 1
    Yellow  = 2
    Red     = 3

ExchargeMarket = {
            "CN-SHH":["上海证券交易所","沪A"],
            "CN-SHZ":["深圳证券交易所","深A"],
            "HK":    ["港交所","9999"],
            "US-ASE":["美国股票交易所","105"],
            "US-NYQ":["纽约证券交易所","106"],
            "US-NMS":["纳斯达克股票交易所","107"],
            "FAVOR":["收藏清单","NA"]
          }