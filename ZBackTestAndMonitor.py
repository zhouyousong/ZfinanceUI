from PySide2.QtWidgets import QApplication, QMessageBox,QFileDialog
from PySide2.QtUiTools import QUiLoader

import ZFavorEditor
import ZBaseFunc
import ZfinanceCfg
import pandas as pd
import ZFunAna
import ZBackTestAndMonitor
import json,os
from PySide2.QtGui import QFont
from PySide2.QtWidgets import *
import PySide2.QtWidgets ,PySide2.QtWidgets ,PySide2.QtGui
import talib
import Zplot
import numpy as np
from PySide2.QtCore import *
from PySide2.QtGui import QCursor


BMTableColumeItem = ['Start','End','FPL','最大回撤','收益率','静态收益率','最低/最高',"当前/最低","指数/收益"]

class BackTestAndMonitorProc:
    def __init__(self,GlobalUI,APP):

        self.GlobalAPP = APP
        self.GlobalMainUI = GlobalUI

        self.GlobalMainUI.SetBackTestPara.clicked.connect(self.HandleSetBackTestPara)
        self.GlobalMainUI.StartBackTesting.clicked.connect(self.HandleStartBackTesting)

        self.GlobalMainUI.BackTestandMonitorTable.clear()
        self.GlobalMainUI.BackTestandMonitorTable.setRowCount(0)
        self.GlobalMainUI.BackTestandMonitorTable.setColumnCount(len(BMTableColumeItem) + 1)


        self.GlobalMainUI.BackTestandMonitorTable.verticalHeader().setVisible(False)
        self.GlobalMainUI.BackTestandMonitorTable.horizontalHeader().setDefaultAlignment(PySide2.QtCore.Qt.AlignLeft)
        self.GlobalMainUI.BackTestandMonitorTable.setFont(QFont('song', 6))
        self.GlobalMainUI.BackTestandMonitorTable.horizontalHeader().setFont(QFont('song', 8))
        self.GlobalMainUI.BackTestandMonitorTable.verticalScrollBar().setValue(0)


        self.BackTestCfgUI = QUiLoader().load('UIDesign\BackTestingParaEditor.ui')

        self.BackTestCfgUI.SaveBackTestPara.clicked.connect(self.HandleSaveBackTestPara)
        self.BackTestCfgUI.LoadBackTestPara.clicked.connect(self.HandleLoadBackTestPara)
        self.BackTestCfgUI.CancelBackTestPara.clicked.connect(self.HandleCancelBackTestPara)

        self.BackTestCfgUI.BackTestSymbolList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.BackTestCfgUI.BackTestSymbolList.customContextMenuRequested[QPoint].connect(self.FavorListChechboxSelectMenu)
        self.BackTestCfgUI.ImportSymbolsToBackTest.clicked.connect(self.HandleImportSymbolsToBackTest)

 #       self.HandleStartBackTesting()
 #       self.HandleSetBackTestPara()

    def HandleImportSymbolsToBackTest(self):
        cursor = QTreeWidgetItemIterator(self.BackTestCfgUI.BackTestSymbolList)
        ChildCnt = cursor.value().childCount()
        self.BMList = []
        while cursor.value():
            Temp = cursor.value()
            ChildCnt = Temp.childCount()
            if(ChildCnt == 0):
                if(Temp.checkState(0)):
                    self.BMList.append(Temp.text(0))
                    print('add-' + Temp.text(0))
            elif Temp.text(0) =='BLACKLIST':
                for i in range(ChildCnt):
                    cursor = cursor.__iadd__(1)
                    Temp = cursor.value()
                    print('Delete-' + Temp.text(0))
                    try:
                        self.BMList.remove(Temp.text(0))
                    except:
                        pass
            cursor = cursor.__iadd__(1)
        ############################去重复
        temp_list = []
        for one in self.BMList:
            if one not in temp_list:
                temp_list.append(one)
        self.BMList = temp_list
        ############################
        self.GlobalMainUI.BackTestandMonitorTable.clear()
        self.GlobalMainUI.BackTestandMonitorTable.setRowCount(len(self.BMList))
        self.GlobalMainUI.BackTestandMonitorTable.setColumnCount(len(BMTableColumeItem) + 1)


        self.GlobalMainUI.BackTestandMonitorTable.verticalHeader().setVisible(False)
        self.GlobalMainUI.BackTestandMonitorTable.horizontalHeader().setDefaultAlignment(PySide2.QtCore.Qt.AlignLeft)
        self.GlobalMainUI.BackTestandMonitorTable.setFont(QFont('song', 6))
        self.GlobalMainUI.BackTestandMonitorTable.horizontalHeader().setFont(QFont('song', 8))
        self.GlobalMainUI.BackTestandMonitorTable.verticalScrollBar().setValue(0)
        Row = 0
        for i in self.BMList:
            SymbolsInTable = PySide2.QtWidgets.QTableWidgetItem(i)
            self.GlobalMainUI.BackTestandMonitorTable.setRowHeight(Row, 5)
            self.GlobalMainUI.BackTestandMonitorTable.setItem(Row, 0, SymbolsInTable)
            Row = Row + 1

        self.GlobalMainUI.BackTestandMonitorTable.setColumnWidth(0, 40)

        Col = 1
        for i in range(len(BMTableColumeItem)):
            self.GlobalMainUI.BackTestandMonitorTable.setColumnWidth(Col, 60)
            Col = Col + 1
        Temp = ['SYM']
        for i in BMTableColumeItem:
            Temp.append(i)
        self.GlobalMainUI.BackTestandMonitorTable.setHorizontalHeaderLabels(Temp)

    def CancelAllChildrenInFavorList(self):
        self.BackTestCfgUI.BackTestSymbolList.currentItem().setCheckState(0, PySide2.QtCore.Qt.CheckState.Unchecked)
        cursor = QTreeWidgetItemIterator(self.BackTestCfgUI.BackTestSymbolList.currentItem())
        ChildCnt = cursor.value().childCount()
        cursor = cursor.__iadd__(1)

        for i in range(ChildCnt):
            cursor.value().setCheckState(0, PySide2.QtCore.Qt.CheckState.Unchecked)
            cursor = cursor.__iadd__(1)

    def SelectAllChildrenInFavorList(self):
        self.BackTestCfgUI.BackTestSymbolList.currentItem().setCheckState(0, PySide2.QtCore.Qt.CheckState.Checked)
        cursor = QTreeWidgetItemIterator(self.BackTestCfgUI.BackTestSymbolList.currentItem())
        ChildCnt = cursor.value().childCount()
        cursor = cursor.__iadd__(1)

        for i in range(ChildCnt):
            cursor.value().setCheckState(0, PySide2.QtCore.Qt.CheckState.Checked)
            cursor = cursor.__iadd__(1)

    def FavorListChechboxSelectMenu(self):
        popMenu = QMenu()
        if self.BackTestCfgUI.BackTestSymbolList.currentItem().parent() == None:
            CancelAll  = popMenu.addAction("取消全选")
            SelectAll  = popMenu.addAction('全选')

            CancelAll.triggered.connect(self.CancelAllChildrenInFavorList)
            SelectAll.triggered.connect(self.SelectAllChildrenInFavorList)
        popMenu.exec_(QCursor.pos())
        return

    def HandleSetBackTestPara(self):
        self.BackTestCfgUI.show()
        ZFavorEditor.LoadFavorListCfg(self.BackTestCfgUI.BackTestSymbolList, CheckBox=True)
        BackTestParaFilePathName = os.getcwd() + '\\Data\\00_Config\\DefaultBackTestPara.ZFbt'
        try:
            with open(BackTestParaFilePathName, 'r') as load_f:
                BackTestDict = json.load(load_f)
            print('Load Default FavorList Config success!!')
        except:
            print('Load Default FavorList Config Fail!!')
            BackTestDict = ZfinanceCfg.BackTestPara
        pass
        self.BackTestCfgUI.BackTestPara.setColumnCount(3)
        self.BackTestCfgUI.BackTestPara.setHeaderLabels(('Key', 'Value','Comment'))
        self.BackTestCfgUI.BackTestPara.clear()
        for Lv1Key,Lv1Val in BackTestDict.items():
            Lv1Child = QTreeWidgetItem(self.BackTestCfgUI.BackTestPara)
            Lv1Child.setText(0, Lv1Key)
            Lv1Child.setExpanded(True)
            if isinstance(Lv1Val,dict):
                for Lv2Key,Lv2Val in Lv1Val.items():
                    if Lv2Key == 'Enable':
                        Lv1Child.setText(2, 'CheckBox')
                        if Lv2Val == True:
                            Lv1Child.setCheckState(0, Qt.Checked)
                        else:
                            Lv1Child.setCheckState(0, Qt.Unchecked)
                    else:
                        Lv2Child = QTreeWidgetItem(Lv1Child)
                        Lv2Child.setExpanded(True)
                        if isinstance(Lv2Val,dict):
                            Lv2Child.setText(0, Lv2Key)
                            for Lv3Key, Lv3Val in Lv2Val.items():
                                if Lv3Key == 'Enable':
                                    Lv2Child.setText(2, 'CheckBox')
                                    if Lv3Val == True:
                                        Lv2Child.setCheckState(0, Qt.Checked)
                                    else:
                                        Lv2Child.setCheckState(0, Qt.Unchecked)
                                else:
                                    Lv3Child = QTreeWidgetItem(Lv2Child)
                                    Lv3Child.setExpanded(True)
                                    Lv3Child.setText(0, Lv3Key)
                                    if(isinstance(Lv3Val,bool)):
                                        Lv3Child.setText(2, "CheckBox-")
                                        if Lv3Val:
                                            Lv3Child.setCheckState(1, Qt.Checked)
                                        else:
                                            Lv3Child.setCheckState(1, Qt.Unchecked)
                                    else:
                                        Lv3Child.setText(1, str(Lv3Val))
                                    Lv3Child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
                        else:
                            Lv2Child.setText(0, Lv2Key)
                            if (isinstance(Lv2Val, bool)):
                                Lv2Child.setText(2, "CheckBox-")
                                if Lv2Val:
                                    Lv2Child.setCheckState(1, Qt.Checked)
                                else:
                                    Lv2Child.setCheckState(1, Qt.Unchecked)
                            else:
                                Lv2Child.setText(1, str(Lv2Val))
                            Lv2Child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
            else:
                Lv1Child.setText(1, Lv1Val)

    def HandleSaveBackTestPara(self):
        BackTestDict = dict()
        cursor = QTreeWidgetItemIterator(self.BackTestCfgUI.BackTestPara)

        for i in range(self.BackTestCfgUI.BackTestPara.topLevelItemCount()):
            if cursor.value().childCount() != 0:
                Lv1Key = cursor.value().text(0)
                Lv2ChCnt = cursor.value().childCount()
                BackTestDict.setdefault(Lv1Key, {})
                if cursor.value().text(2) == 'CheckBox':
                    if (cursor.value().checkState(0)):
                        BackTestDict[Lv1Key]['Enable'] = True
                    else:
                        BackTestDict[Lv1Key]['Enable'] = False
                cursor = cursor.__iadd__(1)
                for j in range(Lv2ChCnt):
                    if cursor.value().childCount() != 0:
                        Lv2Key = cursor.value().text(0)
                        Lv3ChCnt = cursor.value().childCount()
                        BackTestDict[Lv1Key].setdefault(Lv2Key, {})
                        if cursor.value().text(2) == 'CheckBox':
                            if (cursor.value().checkState(0)):
                                BackTestDict[Lv1Key][Lv2Key]['Enable'] = True
                            else:
                                BackTestDict[Lv1Key][Lv2Key]['Enable'] = False
                        cursor = cursor.__iadd__(1)
                        for k in range(Lv3ChCnt):
                            if cursor.value().text(2) == 'CheckBox-':
                                if (cursor.value().checkState(1)):
                                    BackTestDict[Lv1Key][Lv2Key][cursor.value().text(0)] = True
                                else:
                                    BackTestDict[Lv1Key][Lv2Key][cursor.value().text(0)] = False
                            else:
                                BackTestDict[Lv1Key][Lv2Key][cursor.value().text(0)] = float(cursor.value().text(1))
                            cursor = cursor.__iadd__(1)
                    else:
                        if cursor.value().text(2) == 'CheckBox':
                            Lv2Key = cursor.value().text(0)
                            BackTestDict[Lv1Key].setdefault(Lv2Key, {})
                            if (cursor.value().checkState(0)):
                                BackTestDict[Lv1Key][Lv2Key]['Enable'] = True
                            else:
                                BackTestDict[Lv1Key][Lv2Key]['Enable'] = False
                        elif cursor.value().text(2) == 'CheckBox-':
                            if (cursor.value().checkState(1)):
                                BackTestDict[Lv1Key][cursor.value().text(0)] = True
                            else:
                                BackTestDict[Lv1Key][cursor.value().text(0)] = False
                        if cursor.value().text(1) != '':
                            BackTestDict[Lv1Key][cursor.value().text(0)] = float(cursor.value().text(1))
                        cursor = cursor.__iadd__(1)
            else:
                BackTestDict[Lv1Key[cursor.value().text(0)]] = float(cursor.value().text(1))
                cursor = cursor.__iadd__(1)

        BackTestParaFilePathName = os.getcwd() + '\\Data\\00_Config\\DefaultBackTestPara.ZFbt'
        with open(BackTestParaFilePathName, "w") as f:
            json.dump(BackTestDict, f)

    def HandleLoadBackTestPara(self):
        pass

    def HandleCancelBackTestPara(self):
        self.BackTestCfgUI.close()
        pass

    def HandleStartBackTesting(self):


        for Symbol in self.BMList:
            ZBaseFunc.Log2LogBox("Start "+Symbol+" Backtest")
            FileName = ZBaseFunc.GetCompleteFileName('Data/01_TickerDatabase/' + Symbol + '/' + Symbol + '_5m')
            if FileName == None:
                continue
            else:
                Tempdf = pd.read_csv('Data/01_TickerDatabase/' + Symbol + '/' + FileName, sep=',', index_col='DateTime')

            StartDate = Tempdf.index[0]
            EndDate = Tempdf.index[-1]
            KAMA = list()
            RSI = list()

            rsi = talib.RSI(Tempdf["Close"], timeperiod=ZfinanceCfg.RSITP[0])
            highLowLength = 10
            Tempdf['LowPriceMin'] = Tempdf["Low"].rolling(highLowLength).min()
            Tempdf['HighPriceMax'] = Tempdf["High"].rolling(highLowLength).max()
            for i in range(6):
                length = ZfinanceCfg.KAMATP[i]
                multiplier1 = 2/(length+1)


                Tempdf.dropna(inplace=True)
                Tempdf['multiplier2'] = abs((Tempdf["Close"] - Tempdf['LowPriceMin']) -
                                            (Tempdf['HighPriceMax'] - Tempdf["Close"])) / \
                                        (Tempdf['HighPriceMax'] - Tempdf['LowPriceMin'])
                Tempdf['alpha'] = multiplier1 * (1+Tempdf['multiplier2'])
                result = sum(Tempdf["Close"].tolist()[0:length-1])/length

                AMA = [np.nan for i in range(length)]
                for i in range(length,len(Tempdf)):
                    result = result+ Tempdf.iat[i,-1]*(Tempdf.iat[i,3]-result)
                    AMA.append(result)

                KAMA.append(AMA)

            for i in range(3):
                TP = ZfinanceCfg.RSITP[i]
                RSI.append(talib.RSI(Tempdf["Close"], timeperiod=TP))

            for i in range(6):
                Tempdf['KAMA_[' + str(ZfinanceCfg.KAMATP[i]) + ']'] = KAMA[i]
            for i in range(3):
                Tempdf['RSI_[' + str(ZfinanceCfg.RSITP[i]) + ']'] = RSI[i]

            Tempdf.dropna(inplace=True)

            Tempdf['TrendVal'] = Tempdf['KAMA_[' + str(ZfinanceCfg.KAMATP[5]) + ']'].diff()

            currentprice = 1
            buyprice = 0

            ReachRelease = 10
            lockbuylen = 10
            Currentprice = 10
            StopLossPrice = 0
            SellByRSI = 0

            ThisTradingStatus = ZfinanceCfg.TradingStatu.Watch
            buycondition  = False
            sellcondition = False

            TrendRatioLen = 100
            TrendRatio    = 60

            FPL = 0
            ZFPL = 0
            FlCAP  = 0
            FlPOS  = 0
            FlPLList  = list()
            StdPLList = list()
            FixPLList = list()

            ActionList = list()

            Tempdf=Tempdf.iloc[-1000:-1]
            StopLossPrice = 0
            SellByRSIFlag = False
            ProcessCntSum = len(Tempdf)
            TrendDnCnt = 0

            DebugStatus  = ['Watch']
            ActionList.append({
                'TimeStamp':Tempdf.index.values[0],
                'Value':Tempdf.iloc[0]['High'],
                'Action':ZfinanceCfg.DebugStatusStr[ZfinanceCfg.TradingStatu.Watch][0],
                'Color':ZfinanceCfg.DebugStatusStr[ZfinanceCfg.TradingStatu.Watch][1]
            })
            RSI = [0,0,0]
            StartPrice = Tempdf.iloc[0]['Open']
            StartFun = StartPrice*100

            StdFund = StartFun
            FlSharesQt = 0
            StdSharesQt = 0
            for i in range(1, ProcessCntSum):
                ClosePrice = Tempdf.iloc[i]['Close']
                OpenPrice  = Tempdf.iloc[i]['Open']
                TimeStamp = Tempdf.index[i]
                KAMA[0] = Tempdf.iloc[i]['KAMA_[' + str(ZfinanceCfg.KAMATP[0]) + ']']
                KAMA[1] = Tempdf.iloc[i]['KAMA_[' + str(ZfinanceCfg.KAMATP[1]) + ']']
                KAMA[2] = Tempdf.iloc[i]['KAMA_[' + str(ZfinanceCfg.KAMATP[2]) + ']']
                KAMA[3] = Tempdf.iloc[i]['KAMA_[' + str(ZfinanceCfg.KAMATP[3]) + ']']
                KAMA[4] = Tempdf.iloc[i]['KAMA_[' + str(ZfinanceCfg.KAMATP[4]) + ']']
                KAMA[5] = Tempdf.iloc[i]['KAMA_[' + str(ZfinanceCfg.KAMATP[5]) + ']']
                RSI[0] = Tempdf.iloc[i]['RSI_[' + str(ZfinanceCfg.RSITP[0]) + ']']
                RSI[1] = Tempdf.iloc[i]['RSI_[' + str(ZfinanceCfg.RSITP[1]) + ']']
                RSI[2] = Tempdf.iloc[i]['RSI_[' + str(ZfinanceCfg.RSITP[2]) + ']']

                # ---------------------------------------------BUYCONDITION------------------------------------------------#
                 #AMA8 > 所有
                if KAMA[0] < KAMA[1] and\
                   KAMA[0] < KAMA[2] and\
                   KAMA[0] < KAMA[3] and\
                   KAMA[0] < KAMA[4] and\
                   KAMA[0] < KAMA[5] :
                    Buycondition_AMA0UpAll = True
                else:
                    Buycondition_AMA0UpAll = False

                # 整体趋势处于下降

                if Tempdf.iloc[i]['TrendVal'] <= 0:
                    TrendDnCnt += 1
                try:
                    if Tempdf.iloc[i-ZfinanceCfg.TrendDnRatioLen]['TrendVal'] <= 0:
                        TrendDnCnt -= 1
                except:
                    pass

                if TrendDnCnt/ZfinanceCfg.TrendDnRatioLen *100 > ZfinanceCfg.TrendDnRatio:
                    Buycondition_TrendDnRatio = True
                else:
                    Buycondition_TrendDnRatio = False

                # 三条线接近
                if abs(KAMA[3] - KAMA[4])+abs(KAMA[3] - KAMA[5]) +abs(KAMA[4] - KAMA[5]) <ZfinanceCfg.ClosureRatio*KAMA[5] :
                    Buycondition_ClosureRatio = True
                else:
                    Buycondition_ClosureRatio = False

                if Buycondition_AMA0UpAll and Buycondition_TrendDnRatio and Buycondition_ClosureRatio:
                    Buycondition = True
                else:
                    Buycondition = False
                #---------------------------------------------^BUYCONDITION^------------------------------------------------#

                #---------------------------------------------SELLCONDITION------------------------------------------------#
                AMALowerCnt = 0
                for j in range(1, 5):  # AMA8 > 所有
                    if KAMA[0] < KAMA[j] :
                        AMALowerCnt += 1
                if AMALowerCnt >=ZfinanceCfg.Elimit:
                    SellCondition_AMALowerCnt = True
                else:
                    SellCondition_AMALowerCnt = False

                if RSI[0] > ZfinanceCfg.RSISellLimit:
                    SellCondition_RSI = True
                else:
                    SellCondition_RSI = False

                if SellCondition_AMALowerCnt or SellCondition_RSI:
                    SellCondition = True
                else:
                    SellCondition = False
                #---------------------------------------------^SELLCONDITION^------------------------------------------------#

                if (ThisTradingStatus is ZfinanceCfg.TradingStatu.Buy):
                    FlSharesQt = 100
                    FlCAP = FlCAP - FlSharesQt * OpenPrice


                    StdSharesQt = round(StdFund/OpenPrice)
                    StdFund = StdFund-StdSharesQt*OpenPrice

                    BuyPrice = OpenPrice
                    StopLossPrice = OpenPrice * ZfinanceCfg.StopLossRate / 100
                    ZBaseFunc.Log2LogBox(TimeStamp+'|Buy:'+str(OpenPrice))
                if (ThisTradingStatus is ZfinanceCfg.TradingStatu.Sell):
                    FlCAP = FlCAP + 100 * OpenPrice
                    FlSharesQt = 0

                    StdFund =StdFund + StdSharesQt*OpenPrice
                    StdSharesQt = 0

                    ZBaseFunc.Log2LogBox(TimeStamp+'|Sell:'+str(OpenPrice))


                FlagStatusChanged = 1
                #---------------------------------------------状态机跳转------------------------------------------------#
                if ((ThisTradingStatus is ZfinanceCfg.TradingStatu.Watch) and (Buycondition is True)):                  # 观望且符合买入条件
                    ThisTradingStatus =  ZfinanceCfg.TradingStatu.Buy                                                   # 观望转购买
                    ZBaseFunc.Log2LogBox(TimeStamp+'|Watch -> Buy')
                elif ((ThisTradingStatus is ZfinanceCfg.TradingStatu.Hold) and (ClosePrice < BuyPrice)):              # 持仓，但价格跌破买入价
                    ThisTradingStatus =  ZfinanceCfg.TradingStatu.LockSell                                              # 持仓转锁售
                    ZBaseFunc.Log2LogBox(TimeStamp+'|Hold -> LockSell')
                elif ((ThisTradingStatus is ZfinanceCfg.TradingStatu.Hold) and (SellCondition is True)):                # 持仓，符合卖出条件（AMA穿过，RSI很高）
                    ThisTradingStatus =  ZfinanceCfg.TradingStatu.Sell                                                  # 持仓转清仓
                    ZBaseFunc.Log2LogBox(TimeStamp+'|Hold -> Sell')
                    if SellCondition_RSI :                                                                              # 如果RSI过高
                        SellByRSIFlag = True                                                                            # 设置RSIFlag
                elif ((ThisTradingStatus is ZfinanceCfg.TradingStatu.Sell) and (SellByRSIFlag is True)):                 # 卖出，且是以为RSI卖出的
                    ThisTradingStatus =  ZfinanceCfg.TradingStatu.LockBuy                                               # 卖出转锁买
                    ZBaseFunc.Log2LogBox(TimeStamp+'|Sell -> LockBuy')
                    SellByRSIFlag = False
                elif (ThisTradingStatus is   ZfinanceCfg.TradingStatu.Sell):                                            # 卖出
                    ThisTradingStatus =  ZfinanceCfg.TradingStatu.Watch                                                 # 清仓转观望
                    ZBaseFunc.Log2LogBox(TimeStamp+'|Sell -> Watch')
                elif (ThisTradingStatus is  ZfinanceCfg.TradingStatu.Buy):                                              # 买入
                    ThisTradingStatus =  ZfinanceCfg.TradingStatu.Hold                                                  # 买入转持仓
                    ZBaseFunc.Log2LogBox(TimeStamp+'|Buy -> Hold')
                elif ((ThisTradingStatus is  ZfinanceCfg.TradingStatu.LockBuy) and (ReachRelease > lockbuylen)):        # 锁买期过期
                    ThisTradingStatus  =  ZfinanceCfg.TradingStatu.Watch                                                # 锁买转观望
                    ZBaseFunc.Log2LogBox(TimeStamp+'|LockBuy -> Watch')
                elif ((ThisTradingStatus is  ZfinanceCfg.TradingStatu.LockSell) and (ClosePrice < StopLossPrice)):    # 锁售，但跌破止损价格
                    ThisTradingStatus   =  ZfinanceCfg.TradingStatu.Sell                                                # 锁售转卖出
                    ZBaseFunc.Log2LogBox(TimeStamp+'|LockSell -> Sell')
                elif ((ThisTradingStatus is  ZfinanceCfg.TradingStatu.LockSell) and (ClosePrice > BuyPrice)):         # 锁售，当前价格突破买入价
                    ThisTradingStatus  =  ZfinanceCfg.TradingStatu.Hold                                                 # 锁售转持仓
                    ZBaseFunc.Log2LogBox(TimeStamp+'|LockSell -> Hold')
                else:
                    FlagStatusChanged = 0
                    pass
                if FlagStatusChanged == 1:
                    ActionList.append({
                        'TimeStamp': Tempdf.index.values[i],
                        'Value': Tempdf.iloc[i]['High'],
                        'Action': ZfinanceCfg.DebugStatusStr[ThisTradingStatus][0],
                        'Color': ZfinanceCfg.DebugStatusStr[ThisTradingStatus][1]
                    })
                #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#

                self.GlobalMainUI.FunAnaGroupProgressBar.setValue(i / (ProcessCntSum-1) * 100)
                self.GlobalAPP.processEvents()
                DebugStatus.append(ZfinanceCfg.DebugStatusStr[ThisTradingStatus][0])
                FlPL = FlCAP + FlSharesQt*ClosePrice
                StdFundPL = StdFund + StdSharesQt*ClosePrice

                FlPLList.append(FlPL)
                StdPLList.append((StdFundPL/StartFun-1)*100)
                FixPLList.append((ClosePrice/StartPrice-1)*100)

            ZBaseFunc.Log2LogBox("Stop Backtest")
            Tempdf['Status'] = DebugStatus


            StdPL   = (Tempdf['Volume']* 0.01).tolist()

            SP500PL = (Tempdf['Volume']* 0.01).tolist()

            Zplot.DrawCharts(
                Symbol,
                Tempdf.index.values.tolist(),
                np.array(Tempdf.loc[:,['Open','Close','Low','High']]).tolist(),
                Tempdf['Volume'].tolist(),
                Tempdf.loc[:,  ['KAMA_[' + str(ZfinanceCfg.KAMATP[0]) + ']',
                                'KAMA_[' + str(ZfinanceCfg.KAMATP[1]) + ']',
                                'KAMA_[' + str(ZfinanceCfg.KAMATP[2]) + ']',
                                'KAMA_[' + str(ZfinanceCfg.KAMATP[3]) + ']',
                                'KAMA_[' + str(ZfinanceCfg.KAMATP[4]) + ']',
                                'KAMA_[' + str(ZfinanceCfg.KAMATP[5]) + ']']],
                Tempdf['TrendVal'].tolist(),
                Tempdf.loc[:, ['RSI_[' + str(ZfinanceCfg.RSITP[0]) + ']',
                               'RSI_[' + str(ZfinanceCfg.RSITP[1]) + ']',
                               'RSI_[' + str(ZfinanceCfg.RSITP[2]) + ']']],
                ActionList,
                FlPLList, StdPLList,FixPLList,FixPLList
            )

            #def DrawCharts(Symbol, TimeStamp, KlineData, KAMAData, RSIData, Action, FPL, Postion):
            print(FPL)

        pass

