from enum import Enum

EXTENDLEN = 100
PROXYEN   = '127.0.0.1:7890'
#PROXYEN = None
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
ReConnectList_c = ['1','3','5','10','20']
TimeOutList_c = ['5','10','20','30','60']
KAMATP = [8,21,50,144,200,350]
RSITP = [14,21,50]
ClosureRatio = 0.01
TrendGate = 0.0001
TrendDnRatio = 60
TrendDnRatioLen = 300
RSISellLimit = 75
Elimit = 2
StopLossRate = 95

class TradingStatu(Enum):
    Buy         = 0
    Hold        = 1
    LockSell    = 2
    Sell        = 3
    Watch       = 4
    LockBuy     = 5

DebugStatusStr = {
                    TradingStatu.Buy:['Buy','green'],
                    TradingStatu.Hold:['Hold','lightgreen'],
                    TradingStatu.LockSell:['LockSell','peru'],
                    TradingStatu.Sell:['Sell','red'],
                    TradingStatu.Watch:['Watch','blue'],
                    TradingStatu.LockBuy:['LockBuy','violet']
}

BackTestPara = {
                    "AEMA":{
                        "Length":180,
                        "haha":False
                    },
                    "RSI":{
                        "Enable":True,
                        "RSI1":{
                            "Length":21,
                            'OverBug':80,
                            "OverSell":20,
                            "hehe":False
                        },
                        "RSI2":{
                            "Enable":False,
                            "Length":21,
                        },
                        "RSI3": {
                            "Enable": True,
                            "Length": 50,
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
                        "TrendGate": 0.001,
                        "ClosureRatio": 0.01,
                        "StopLossRate":95
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
