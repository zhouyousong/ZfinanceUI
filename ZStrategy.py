import ZBaseFunc,ZfinanceCfg
import yfinance as yf
import pandas as pd
import numpy as np
import talib


class UserVariables:
    def __init__(self):
        self.TradingStatus = ZfinanceCfg.TradingStatu.Watch
        self.Index = 0
        self.TrendDnCnt = 0
        self.SellByRSIFlag = False
        self.FlCAP = 0
        self.StopLossPrice = 0
        self.BuyPrice = 0
class UserParameters:
    def __init__(self,StrategyPara = dict()):


        self.RSITP = [
            StrategyPara['RSI']['RSI1']['Length'],
            StrategyPara['RSI']['RSI2']['Length'],
            StrategyPara['RSI']['RSI3']['Length']
        ]
        self.AEMATP = [

            StrategyPara['AEMATP']['Length1'],
            StrategyPara['AEMATP']['Length2'],
            StrategyPara['AEMATP']['Length3'],
            StrategyPara['AEMATP']['Length4'],
            StrategyPara['AEMATP']['Length5'],
            StrategyPara['AEMATP']['Length6']
        ]

        self.LastIndex  = StrategyPara['Trading']['LastIndex']
        self.TrendGate  = StrategyPara['Trading']['TrendGate']
        self.TrendDnRatioLen = StrategyPara['Trading']['TrendDnRatioLen']

        self.RaiseScaleInTrendUp = StrategyPara['Trading']['TrendUp']['RaiseScale']
        self.FallScaleInTrendUp  = StrategyPara['Trading']['TrendUp']['FallScale']
        self.ElimitInTrendup     = StrategyPara['Trading']['TrendUp']['Elimit']

        self.RaiseScaleInTrendNo = StrategyPara['Trading']['TrendNo']['RaiseScale']
        self.FallScaleInTrendNo  = StrategyPara['Trading']['TrendNo']['FallScale']
        self.ElimitInTrendNo     = StrategyPara['Trading']['TrendNo']['Elimit']

        self.RaiseScaleInTrendDn = StrategyPara['Trading']['TrendDn']['RaiseScale']
        self.FallScaleInTrendDn  = StrategyPara['Trading']['TrendDn']['FallScale']
        self.ElimitInTrendDn     = StrategyPara['Trading']['TrendDn']['Elimit']

        self.TrendDnRatio        = StrategyPara['Trading']['TrendDnRatio']
        self.ClosureRatio        = StrategyPara['Trading']['ClosureRatio']
        self.StopLossRate        = StrategyPara['Trading']['StopLossRate']
        self.RSISellLimit        = StrategyPara['Trading']['RSISellLimit']
        self.LockBuyLen          = StrategyPara['Trading']['LockBuyLen']
class SystemResult:
    def __init__(self):
        self.TradingStatus = ZfinanceCfg.TradingStatu.Watch
        self.Index = 0
        self.TrendDnCnt = 0
        self.SellByRSIFlag = False
        self.FlCAP = 0
        self.FlagStatusChanged= False
        self.ClosePrice = 0
class OpenStrategysPlatform:
    def __init__(self, StrategyDataframe=pd.DataFrame(), StrategyPara = dict()):
        self.Result = SystemResult()                    #初始化系统需要的结果输出，用户需要在策略完成时把self.Result里的内容填满
        self.Z_UsrPara = UserParameters(StrategyPara)   #初始化用户参数
        self.Z_UseVar  = UserVariables()                #初始化用户变量

        self.StrategyDataframe = StrategyDataframe


    def CalcInitIndicators(self):               #用户编写
        Result = dict()
        highLowLength = 10
        RSILenLabel = []
        AEMALenLabel = []

        self.StrategyDataframe['LowPriceMin'] = self.StrategyDataframe ["Low"].rolling(highLowLength).min()
        self.StrategyDataframe['HighPriceMax'] = self.StrategyDataframe ["High"].rolling(highLowLength).max()
        self.StrategyDataframe.dropna(inplace=True)


        for RSILen in self.Z_UsrPara.RSITP:
            ColumeIndex = 'RSI_[' + str(RSILen) + ']'
            self.StrategyDataframe[ColumeIndex] = talib.RSI(self.StrategyDataframe["Close"], timeperiod=RSILen)
            RSILenLabel.append(ColumeIndex)

        for AEMALen in self.Z_UsrPara.AEMATP:
            ColumeIndex = 'AEMA_[' + str(AEMALen) + ']'
            AEMALenLabel.append(ColumeIndex)

            multiplier1 = 2 / (AEMALen + 1)
            self.StrategyDataframe['multiplier2'] = abs((self.StrategyDataframe["Close"] - self.StrategyDataframe['LowPriceMin']) -
                                        (self.StrategyDataframe['HighPriceMax'] - self.StrategyDataframe["Close"])) / \
                                    (self.StrategyDataframe['HighPriceMax'] - self.StrategyDataframe['LowPriceMin'])
            self.StrategyDataframe['alpha'] = multiplier1 * (1 + self.StrategyDataframe['multiplier2']).fillna(0)
            alpha = self.StrategyDataframe.columns.get_loc('alpha')
            Close = self.StrategyDataframe.columns.get_loc('Close')
            result = sum(self.StrategyDataframe["Close"].tolist()[0:AEMALen - 1]) / AEMALen
            AEMA_x = [np.nan for j in range(AEMALen)]
            for k in range(AEMALen, len(self.StrategyDataframe)):
                result = result + self.StrategyDataframe.iat[k, alpha] * (self.StrategyDataframe.iat[k, Close] - result)
                AEMA_x.append(result)
            self.StrategyDataframe[ColumeIndex] = AEMA_x


        self.StrategyDataframe['TrendVal'] = self.StrategyDataframe['AEMA_[' + str(AEMALen) + ']'].diff()
        self.StrategyDataframe.dropna(inplace=True)

        Result["IndictorInKlineDraw"]   = AEMALenLabel
        Result["RSIInDraw"]             = RSILenLabel

        Result["StartPrice"]            = self.StrategyDataframe.iloc[0]['Open']
        Result["HighPrice"]            = self.StrategyDataframe.iloc[0]['High']
        Result["StartTime"]             = self.StrategyDataframe.index[0]

        Result["ClosePrice"]              = self.StrategyDataframe.iloc[-1]['Close']
        Result["EndTime"]               = self.StrategyDataframe.index[-1]

        Result["Length"]                = len(self.StrategyDataframe)
        Result["SkipLength"]            = self.Z_UsrPara.LastIndex

        self.Z_UseVar.TradingStatus = ZfinanceCfg.TradingStatu.Watch


        #用于iat取值的优化，可以大大提高计算速度
        self.LocClose = self.StrategyDataframe.columns.get_loc('Close')
        self.LocAEMA0 = self.StrategyDataframe.columns.get_loc('AEMA_[' + str(self.Z_UsrPara.AEMATP[0]) + ']')
        self.LocAEMA1 = self.StrategyDataframe.columns.get_loc('AEMA_[' + str(self.Z_UsrPara.AEMATP[1]) + ']')
        self.LocAEMA2 = self.StrategyDataframe.columns.get_loc('AEMA_[' + str(self.Z_UsrPara.AEMATP[2]) + ']')
        self.LocAEMA3 = self.StrategyDataframe.columns.get_loc('AEMA_[' + str(self.Z_UsrPara.AEMATP[3]) + ']')
        self.LocAEMA4 = self.StrategyDataframe.columns.get_loc('AEMA_[' + str(self.Z_UsrPara.AEMATP[4]) + ']')
        self.LocAEMA5 = self.StrategyDataframe.columns.get_loc('AEMA_[' + str(self.Z_UsrPara.AEMATP[5]) + ']')

        self.LocRSI0 = self.StrategyDataframe.columns.get_loc('RSI_[' + str(self.Z_UsrPara.RSITP[0]) + ']')
        self.LocRSI1 = self.StrategyDataframe.columns.get_loc('RSI_[' + str(self.Z_UsrPara.RSITP[1]) + ']')
        self.LocRSI2 = self.StrategyDataframe.columns.get_loc('RSI_[' + str(self.Z_UsrPara.RSITP[2]) + ']')

        self.LocTrendVal = self.StrategyDataframe.columns.get_loc('TrendVal')
        self.LocHigh     = self.StrategyDataframe.columns.get_loc('High')


        return Result

    def LoopStrategys(self,TailerPointer):                    #用户编写
        AEMA =  [0] * 6
        RSI =  [0] * 3

        ClosePrice = self.StrategyDataframe.iat[TailerPointer,self.LocClose]

        AEMA[0] = self.StrategyDataframe.iat[TailerPointer,self.LocAEMA0]
        AEMA[1] = self.StrategyDataframe.iat[TailerPointer,self.LocAEMA1]
        AEMA[2] = self.StrategyDataframe.iat[TailerPointer,self.LocAEMA2]
        AEMA[3] = self.StrategyDataframe.iat[TailerPointer,self.LocAEMA3]
        AEMA[4] = self.StrategyDataframe.iat[TailerPointer,self.LocAEMA4]
        AEMA[5] = self.StrategyDataframe.iat[TailerPointer,self.LocAEMA5]

        AEMA_LastOne   = self.StrategyDataframe.iat[TailerPointer - 1,                       self.LocAEMA5]
        AEMA_LastIndex = self.StrategyDataframe.iat[TailerPointer - self.Z_UsrPara.LastIndex,self.LocAEMA5]

        RSI[0] = self.StrategyDataframe.iat[TailerPointer,self.LocRSI0]
        RSI[1] = self.StrategyDataframe.iat[TailerPointer,self.LocRSI1]
        RSI[2] = self.StrategyDataframe.iat[TailerPointer,self.LocRSI2]

        Temp = ((AEMA[5] - AEMA_LastOne) / AEMA_LastOne)
        if Temp > self.Z_UsrPara.TrendGate:
            TrendMode = ZfinanceCfg.TrendMode.UP
        elif Temp  < -self.Z_UsrPara.TrendGate:
            TrendMode = ZfinanceCfg.TrendMode.DN
        else:
            Temp = ((AEMA[5] - AEMA_LastIndex) / AEMA_LastIndex)
            if Temp > self.Z_UsrPara.TrendGate:
                TrendMode = ZfinanceCfg.TrendMode.UP
            elif Temp < -self.Z_UsrPara.TrendGate:
                TrendMode = ZfinanceCfg.TrendMode.DN
            else:
                TrendMode = ZfinanceCfg.TrendMode.NO

        if TrendMode == ZfinanceCfg.TrendMode.UP:
            RaiseScale  =   self.Z_UsrPara.RaiseScaleInTrendUp
            FallScale   =   self.Z_UsrPara.FallScaleInTrendUp
            Elimit      =   self.Z_UsrPara.ElimitInTrendup
        elif TrendMode == ZfinanceCfg.TrendMode.DN:
            RaiseScale  =   self.Z_UsrPara.RaiseScaleInTrendDn
            FallScale   =   self.Z_UsrPara.FallScaleInTrendDn
            Elimit      =   self.Z_UsrPara.ElimitInTrendDn
        else:
            RaiseScale  =   self.Z_UsrPara.RaiseScaleInTrendNo
            FallScale   =   self.Z_UsrPara.FallScaleInTrendNo
            Elimit      =   self.Z_UsrPara.ElimitInTrendNo



        # ---------------------------------------------BUYCONDITION------------------------------------------------#
         #AMA8 > 所有
        if AEMA[0] > AEMA[1]*RaiseScale and\
           AEMA[0] > AEMA[2]*RaiseScale and\
           AEMA[0] > AEMA[3]*RaiseScale and\
           AEMA[0] > AEMA[4]*RaiseScale and\
           AEMA[0] > AEMA[5]*RaiseScale :
            Buycondition_AEMA0UpAll = True
        else:
            Buycondition_AEMA0UpAll = False

        # 整体趋势处于下降

        if self.StrategyDataframe.iat[TailerPointer,self.LocTrendVal] < 0:
            self.Z_UseVar.TrendDnCnt += 1
        if TailerPointer >= self.Z_UsrPara.TrendDnRatioLen+self.Z_UsrPara.LastIndex:
            if self.StrategyDataframe.iat[TailerPointer-self.Z_UsrPara.TrendDnRatioLen,self.LocTrendVal] < 0:
                self.Z_UseVar.TrendDnCnt -= 1
        #print("TDC = "+str(TrendDnCnt)+" |i = "+str(i)+"|TrendVal = "+str(Tempdf.iloc[i]['TrendVal']))

        if self.Z_UseVar.TrendDnCnt <0:
            print("Error TrendDnCnt i=",TailerPointer)
        if self.Z_UseVar.TrendDnCnt/self.Z_UsrPara.TrendDnRatioLen *100 > self.Z_UsrPara.TrendDnRatio:
            Buycondition_TrendDnRatio = True
        else:
            Buycondition_TrendDnRatio = False

        # 三条线接近
        if abs(AEMA[3] - AEMA[4])+abs(AEMA[3] - AEMA[5]) +abs(AEMA[4] - AEMA[5]) <self.Z_UsrPara.ClosureRatio*(AEMA[3]+AEMA[4]+AEMA[5]) :
            Buycondition_ClosureRatio = True
        else:
            Buycondition_ClosureRatio = False

        if Buycondition_AEMA0UpAll and Buycondition_TrendDnRatio and Buycondition_ClosureRatio:
            Buycondition = True
        else:
            Buycondition = False
        #---------------------------------------------^BUYCONDITION^------------------------------------------------#

        #---------------------------------------------SELLCONDITION------------------------------------------------#
        AEMALowerCnt = 0
        for j in range(1, 5):  # AMA8 > 所有
            if AEMA[0] < AEMA[j] * FallScale:
                AEMALowerCnt += 1
        if AEMALowerCnt >=Elimit:
            SellCondition_AMALowerCnt = True
        else:
            SellCondition_AMALowerCnt = False

        if RSI[0] > self.Z_UsrPara.RSISellLimit:
            SellCondition_RSI = True
        else:
            SellCondition_RSI = False

        if SellCondition_AMALowerCnt or SellCondition_RSI:
            SellCondition = True
        else:
            SellCondition = False
        #---------------------------------------------^SELLCONDITION^------------------------------------------------#

        #---------------------------------------------状态机跳转------------------------------------------------#
        if (self.Z_UseVar.TradingStatus is ZfinanceCfg.TradingStatu.LockBuy):
            self.Z_UseVar.ReachRelease += 1
        FlagStatusChanged = True
        #---------------------------------------------状态机跳转------------------------------------------------#
        if ((self.Z_UseVar.TradingStatus is ZfinanceCfg.TradingStatu.Watch) and (Buycondition is True)):                  # 观望且符合买入条件
            self.Z_UseVar.TradingStatus =  ZfinanceCfg.TradingStatu.Buy                                                   # 观望转购买

        elif ((self.Z_UseVar.TradingStatus is ZfinanceCfg.TradingStatu.Hold) and (ClosePrice < self.Z_UseVar.BuyPrice)):              # 持仓，但价格跌破买入价
            self.Z_UseVar.TradingStatus =  ZfinanceCfg.TradingStatu.LockSell                                              # 持仓转锁售

        elif ((self.Z_UseVar.TradingStatus is ZfinanceCfg.TradingStatu.Hold) and (SellCondition is True)):                # 持仓，符合卖出条件（AMA穿过，RSI很高）
            self.Z_UseVar.TradingStatus =  ZfinanceCfg.TradingStatu.Sell                                                  # 持仓转清仓

            if SellCondition_RSI :                                                                              # 如果RSI过高
                self.Z_UseVar.SellByRSIFlag = True                                                                            # 设置RSIFlag
                self.Z_UseVar.ReachRelease = 0
        elif ((self.Z_UseVar.TradingStatus is ZfinanceCfg.TradingStatu.Sell) and (self.Z_UseVar.SellByRSIFlag is True)):                 # 卖出，且是以为RSI卖出的
            self.Z_UseVar.TradingStatus =  ZfinanceCfg.TradingStatu.LockBuy                                               # 卖出转锁买

            self.Z_UseVar.SellByRSIFlag = False
        elif (self.Z_UseVar.TradingStatus is   ZfinanceCfg.TradingStatu.Sell):                                            # 卖出
            self.Z_UseVar.TradingStatus =  ZfinanceCfg.TradingStatu.Watch                                                 # 清仓转观望

        elif (self.Z_UseVar.TradingStatus is  ZfinanceCfg.TradingStatu.Buy):                                              # 买入
            self.Z_UseVar.TradingStatus =  ZfinanceCfg.TradingStatu.Hold                                                  # 买入转持仓

        elif ((self.Z_UseVar.TradingStatus is  ZfinanceCfg.TradingStatu.LockBuy) and (self.Z_UseVar.ReachRelease > self.Z_UsrPara.LockBuyLen)):        # 锁买期过期
            self.Z_UseVar.TradingStatus  =  ZfinanceCfg.TradingStatu.Watch                                                # 锁买转观望

        elif ((self.Z_UseVar.TradingStatus is  ZfinanceCfg.TradingStatu.LockSell) and (ClosePrice < self.Z_UseVar.StopLossPrice)):    # 锁售，但跌破止损价格
            self.Z_UseVar.TradingStatus   =  ZfinanceCfg.TradingStatu.Sell                                                # 锁售转卖出

        elif ((self.Z_UseVar.TradingStatus is  ZfinanceCfg.TradingStatu.LockSell) and (ClosePrice > self.Z_UseVar.BuyPrice)):         # 锁售，当前价格突破买入价
            self.Z_UseVar.TradingStatus  =  ZfinanceCfg.TradingStatu.Hold                                                 # 锁售转持仓
        else:
            FlagStatusChanged = False
            pass

        if FlagStatusChanged == True:

            if (self.Z_UseVar.TradingStatus is ZfinanceCfg.TradingStatu.Buy):
                self.Z_UseVar.BuyPrice      = ClosePrice
                self.Z_UseVar.StopLossPrice = self.Z_UseVar.BuyPrice * self.Z_UsrPara.StopLossRate / 100


        self.Result.TradingStatus       = self.Z_UseVar.TradingStatus
        self.Result.FlagStatusChanged   = FlagStatusChanged
        self.Result.ClosePrice          = ClosePrice

        self.Result.TimeStamp = self.StrategyDataframe.index[TailerPointer]
        self.Result.HighPrice = self.StrategyDataframe.iat[TailerPointer,self.LocHigh]

        return self.Result

    def CalcNewIndicators(self,NewOHLCV):       #用户编写
        self.StrategyDataframe.append(NewOHLCV)

        highLowLength = 10
        self.StrategyDataframe['LowPriceMin'] = self.StrategyDataframe ["Low"].rolling(highLowLength).min()
        self.StrategyDataframe['HighPriceMax'] = self.StrategyDataframe ["High"].rolling(highLowLength).max()


        for RSILen in self.Z_UsrPara.RSITP:
            self.StrategyDataframe['RSI_[' + str(self.StrategyDataframe[RSILen]) + ']'] = talib.RSI(self.StrategyDataframe["Close"], timeperiod=RSILen)

        for AEMALen in self.Z_UsrPara.AEMATP:

            multiplier1 = 2 / (AEMALen + 1)
            self.StrategyDataframe['multiplier2'] = abs((self.StrategyDataframe["Close"] - self.StrategyDataframe['LowPriceMin']) -
                                        (self.StrategyDataframe['HighPriceMax'] - self.StrategyDataframe["Close"])) / \
                                    (self.StrategyDataframe['HighPriceMax'] - self.StrategyDataframe['LowPriceMin'])
            self.StrategyDataframe['alpha'] = multiplier1 * (1 + self.StrategyDataframe['multiplier2']).fillna(0)
            result = sum(self.StrategyDataframe["Close"].tolist()[0:AEMALen - 1]) / AEMALen
            AEMA_x = [np.nan for j in range(AEMALen)]
            for k in range(AEMALen, len(self.StrategyDataframe)):
                result = result + self.StrategyDataframe.iat[k, -1] * (self.StrategyDataframe.iat[k, 3] - result)
                AEMA_x.append(result)
            self.StrategyDataframe['AEMA_[' + str(AEMALen) + ']'] = AEMA_x


        self.StrategyDataframe['TrendVal'] = self.StrategyDataframe['AEMA_[' + str(AEMALen) + ']'].diff()
        self.StrategyDataframe.dropna(inplace=True)
        pass
class EquityPlatform:
    def __init__(self, ShareVol,StartPrice):
        self.Std_PLEquity_Start = self.Std_PLEquity = StartPrice * ShareVol                     # 标准固定资产算法，假设一开始有100股的金额
        self.StartPrice = StartPrice
        self.Float_PLEquity = 0                                                                 # floatprofit 算法下的剩余资产，起始为0，每次买卖都是100股
        self.Std_SharesVol = self.Float_SharesVol = 0                                                        # 初始状态持仓为0
        self.ShareVol = ShareVol

    def CalcResidualEquity(self,TradeAction,OptPrice,ClosePrice):
        EquityResult = dict()
        if TradeAction is ZfinanceCfg.TradingStatu.Buy:  # 如果是买入操作
            self.Float_PLEquity = self.Float_PLEquity - self.ShareVol * OptPrice                # 计算floatprofit算法下的剩余资产 thinkorswim提供的算法
            self.Float_SharesVol = self.ShareVol                                                # 记floatprofitprofit算法下的持仓为100

            self.Std_SharesVol = round(self.Std_PLEquity / OptPrice)                            # 计算standardprofit算法下剩余资产能买入仓位数
            self.Std_PLEquity = self.Std_PLEquity - self.Std_SharesVol * OptPrice               # 计算standardprofit算法下的剩余资产
        elif TradeAction is ZfinanceCfg.TradingStatu.Sell:                                           # 如果是卖出操作
            self.Float_PLEquity = self.Float_PLEquity + self.ShareVol * OptPrice                # 计算floatprofit算法下的剩余资产 thinkorswim提供的算法
            self.Float_SharesVol = 0                                                            # 计算floatprofit算法下的持仓为0

            self.Std_PLEquity = self.Std_PLEquity + self.Std_SharesVol  * OptPrice              # 计算standardprofit算法下的剩余资产
            self.Std_SharesVol = 0                                                              # standardprofit算法仓位清空

        EquityResult['Float_PL']     = self.Float_PLEquity + self.ShareVol * ClosePrice
        EquityResult['Std_PL_Ratio'] = (self.Std_PLEquity + self.Std_SharesVol * ClosePrice)/self.Std_PLEquity_Start * 100
        EquityResult['Fix_PL_Ratio'] = ClosePrice / self.StartPrice *100

        return EquityResult

import yfinance
def GetSymbolInitOHLCV( Symbol,Period = None,Interval = '5m',OnlineMode=True):

    if OnlineMode:
        SYM = yfinance.Ticker(Symbol)
        StrategyDataframe = SYM.history(prepost=True, interval='5m', proxy='http://127.0.0.1:7890')

    if (len(StrategyDataframe) != 0):
        if (Interval == '1d'):
            StrategyDataframe.index = StrategyDataframe.index.strftime("%Y-%m-%d")
        else:
            StrategyDataframe.index = StrategyDataframe.index.strftime("%Y-%m-%d %H:%M")

    else:
        FileName = ZBaseFunc.GetCompleteFileName('Data/01_TickerDatabase/' + Symbol + '/' + Symbol + '_'+Interval)
        StrategyDataframe = pd.read_csv('Data/01_TickerDatabase/' + Symbol + '/' + FileName, sep=',', index_col='DateTime')

    try:
        Market = Symbol.split['.'][1]
        if Market == 'ss'or Market == 'sz':
            Market = 'CN'
        elif Market == 'hk':
            Market = 'HK'
    except:
        Market = 'US'

    if Period != None:
        cnt = Period *ZfinanceCfg.CntPreDayConfigTable[Market][Interval]
        if cnt <= len(StrategyDataframe):
            return StrategyDataframe.iloc[-cnt:-1]
    return StrategyDataframe
