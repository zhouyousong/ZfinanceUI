from enum import Enum

EXTENDLEN = 100
PROXYEN   = 'http://127.0.0.1:7890'
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
SkipPeriodList_c = ['No','3','6','9','12','15','18','21']
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

BMTableColumeItem = ['Start', 'End', 'FlPL', 'StdPL', 'FixPL']

DebugStatusStr = {
                    TradingStatu.Buy:['Buy','green'],
                    TradingStatu.Hold:['Hold','lightgreen'],
                    TradingStatu.LockSell:['LockSell','peru'],
                    TradingStatu.Sell:['Sell','red'],
                    TradingStatu.Watch:['Watch','blue'],
                    TradingStatu.LockBuy:['LockBuy','violet']
}

BackTestPara = {
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
