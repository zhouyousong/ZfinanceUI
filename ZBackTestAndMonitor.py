import copy

from PySide2.QtWidgets import QApplication, QMessageBox,QFileDialog
from PySide2.QtUiTools import QUiLoader
import ctypes
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
import time,datetime,copy

class BackTestAndMonitorProc:
    def __init__(self,GlobalUI,APP):

        self.GlobalAPP = APP
        self.GlobalMainUI = GlobalUI

        self.GlobalMainUI.SetBackTestPara.clicked.connect(self.HandleSetBackTestPara)
        self.GlobalMainUI.StartBackTesting.clicked.connect(self.HandleStartBackTesting)
        self.GlobalMainUI.OpenGroupBackTestParas.clicked.connect(self.HandleOpenGroupBackTestParas)
        self.GlobalMainUI.StartGroupBackTestings.clicked.connect(self.HandleStartGroupBackTestings)

        self.GlobalMainUI.BackTestandMonitorTable.clear()
        self.GlobalMainUI.BackTestandMonitorTable.setRowCount(0)
        self.GlobalMainUI.BackTestandMonitorTable.setColumnCount(len(ZfinanceCfg.BMTableColumeItem) + 1)


        self.GlobalMainUI.BackTestandMonitorTable.verticalHeader().setVisible(False)
        self.GlobalMainUI.BackTestandMonitorTable.horizontalHeader().setDefaultAlignment(PySide2.QtCore.Qt.AlignLeft)
        self.GlobalMainUI.BackTestandMonitorTable.setFont(QFont('song', 8))
        self.GlobalMainUI.BackTestandMonitorTable.horizontalHeader().setFont(QFont('song', 8))
        self.GlobalMainUI.BackTestandMonitorTable.verticalScrollBar().setValue(0)


        self.BackTestCfgUI = QUiLoader().load('UIDesign\BackTestingParaEditor.ui')

        self.BackTestCfgUI.SaveBackTestPara.clicked.connect(self.HandleSaveBackTestPara)
        self.BackTestCfgUI.GenBackTestParaFiles.clicked.connect(self.HandleGenBackTestParaFiles)
        self.BackTestCfgUI.LoadBackTestPara.clicked.connect(self.HandleLoadBackTestPara)
        self.BackTestCfgUI.CancelBackTestPara.clicked.connect(self.HandleCancelBackTestPara)


        self.BackTestCfgUI.BackTestSymbolList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.BackTestCfgUI.BackTestSymbolList.customContextMenuRequested[QPoint].connect(self.FavorListChechboxSelectMenu)
        self.BackTestCfgUI.ImportSymbolsToBackTest.clicked.connect(self.HandleImportSymbolsToBackTest)

        self.StopFlag = True
 #       self.HandleStartBackTesting()
 #       self.HandleSetBackTestPara()

    def HandleOpenGroupBackTestParas(self):
        self.BackTestParaGroups, ok = QFileDialog.getOpenFileNames(None, "选择配置文件", 'Data/00_Config/BackTestParaGroup', '(*.ZFbt)')


    def HandleImportSymbolsToBackTest(self):
        cursor = QTreeWidgetItemIterator(self.BackTestCfgUI.BackTestSymbolList)
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
        self.CleanTable()
        ############################
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

            SelectAll  = popMenu.addAction('全选')
            CancelAll  = popMenu.addAction("取消全选")

            CancelAll.triggered.connect(self.CancelAllChildrenInFavorList)
            SelectAll.triggered.connect(self.SelectAllChildrenInFavorList)
        popMenu.exec_(QCursor.pos())
        return

    def HandleSetBackTestPara(self):
        self.BackTestCfgUI.show()
        ZFavorEditor.LoadFavorListCfg(self.BackTestCfgUI.BackTestSymbolList, CheckBox=False)
        BackTestParaFilePathName = os.getcwd() + '\\Data\\00_Config\\DefaultBackTestPara.ZFbt'
        try:
            with open(BackTestParaFilePathName, 'r') as load_f:
                self.BackTestDict = json.load(load_f)
            print('Load Default FavorList Config success!!')
        except:
            print('Load Default FavorList Config Fail!!')
            self.BackTestDict = ZfinanceCfg.BackTestPara

        pass
        self.BackTestCfgUI.BackTestPara.setColumnCount(3)
        self.BackTestCfgUI.BackTestPara.setHeaderLabels(('Key', 'Value','Comment'))
        self.BackTestCfgUI.BackTestPara.clear()
        #self.BackTestCfgUI.BackTestPara.setColumnHidden(2,True)
        for Lv1Key,Lv1Val in self.BackTestDict.items():
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
        cursor = QTreeWidgetItemIterator(self.BackTestCfgUI.BackTestPara)

        for i in range(self.BackTestCfgUI.BackTestPara.topLevelItemCount()):
            if cursor.value().childCount() != 0:
                Lv1Key = cursor.value().text(0)
                Lv2ChCnt = cursor.value().childCount()
                self.BackTestDict.setdefault(Lv1Key, {})
                if cursor.value().text(2) == 'CheckBox':
                    if (cursor.value().checkState(0)):
                        self.BackTestDict[Lv1Key]['Enable'] = True
                    else:
                        self.BackTestDict[Lv1Key]['Enable'] = False
                cursor = cursor.__iadd__(1)
                for j in range(Lv2ChCnt):
                    if cursor.value().childCount() != 0:
                        Lv2Key = cursor.value().text(0)
                        Lv3ChCnt = cursor.value().childCount()
                        self.BackTestDict[Lv1Key].setdefault(Lv2Key, {})
                        if cursor.value().text(2) == 'CheckBox':
                            if (cursor.value().checkState(0)):
                                self.BackTestDict[Lv1Key][Lv2Key]['Enable'] = True
                            else:
                                self.BackTestDict[Lv1Key][Lv2Key]['Enable'] = False
                        cursor = cursor.__iadd__(1)
                        for k in range(Lv3ChCnt):
                            if cursor.value().text(2) == 'CheckBox-':
                                if (cursor.value().checkState(1)):
                                    self.BackTestDict[Lv1Key][Lv2Key][cursor.value().text(0)] = True
                                else:
                                    self.BackTestDict[Lv1Key][Lv2Key][cursor.value().text(0)] = False
                            else:
                                if type(self.BackTestDict[Lv1Key][Lv2Key][cursor.value().text(0)]) == float:
                                    self.BackTestDict[Lv1Key][Lv2Key][cursor.value().text(0)] = float(cursor.value().text(1))
                                else:
                                    self.BackTestDict[Lv1Key][Lv2Key][cursor.value().text(0)] = int(cursor.value().text(1))
                            cursor = cursor.__iadd__(1)
                    else:
                        if cursor.value().text(2) == 'CheckBox':
                            Lv2Key = cursor.value().text(0)
                            self.BackTestDict[Lv1Key].setdefault(Lv2Key, {})
                            if (cursor.value().checkState(0)):
                                self.BackTestDict[Lv1Key][Lv2Key]['Enable'] = True
                            else:
                                self.BackTestDict[Lv1Key][Lv2Key]['Enable'] = False
                        elif cursor.value().text(2) == 'CheckBox-':
                            if (cursor.value().checkState(1)):
                                self.BackTestDict[Lv1Key][cursor.value().text(0)] = True
                            else:
                                self.BackTestDict[Lv1Key][cursor.value().text(0)] = False
                        if cursor.value().text(1) != '':
                            if type(self.BackTestDict[Lv1Key][cursor.value().text(0)]) == float :
                                self.BackTestDict[Lv1Key][cursor.value().text(0)] = float(cursor.value().text(1))
                            else:
                                self.BackTestDict[Lv1Key][cursor.value().text(0)] = int(cursor.value().text(1))
                        cursor = cursor.__iadd__(1)
            else:
                if type(self.BackTestDict[Lv1Key[cursor.value().text(0)]]) == float:
                    self.BackTestDict[Lv1Key[cursor.value().text(0)]] = float(cursor.value().text(1))
                else:
                    self.BackTestDict[Lv1Key][cursor.value().text(0)] = int(cursor.value().text(1))
                cursor = cursor.__iadd__(1)

        BackTestParaFilePathName = os.getcwd() + '\\Data\\00_Config\\DefaultBackTestPara.ZFbt'
        with open(BackTestParaFilePathName, "w") as f:
            json.dump(self.BackTestDict, f)
        self.BackTestDictGenPara = self.BackTestDict

    def HandleGenBackTestParaFiles(self):

        self.HandleSaveBackTestPara()
        BackTestDict = self.BackTestDictGenPara

        cursor = QTreeWidgetItemIterator(self.BackTestCfgUI.BackTestPara)


        TempDictIndexList = []
        while cursor.value():
            Temp = cursor.value()
            TempDictIndex = []
            if Temp.text(2).split(':')[0] != Temp.text(2):
                StepX = Temp.text(2)
                TempDictIndex.insert(0, Temp.text(0))
                while Temp.parent() != None:
                    Temp = Temp.parent()
                    TempDictIndex.insert(0,Temp.text(0))
                TempDictIndexList.insert(0,{"TempDictIndex":TempDictIndex,"StepX":StepX})

            cursor = cursor.__iadd__(1)

        TempFolderPath = os.getcwd() + "\\Data\\00_Config\\BackTestParaGroup"
        try:
            os.mkdir(TempFolderPath)
        except:
            pass
        DateTimeStr = time.strftime("%Y-%m-%d %H_%M_%S", time.localtime())
        TempFolderPath = TempFolderPath+'\\'+DateTimeStr
        os.mkdir(TempFolderPath)
        j=0
        self.GenZFbtFileSum = 1
        for iTempDictIndexList in TempDictIndexList:
            StepX = iTempDictIndexList["StepX"]
            TempDictIndex = iTempDictIndexList["TempDictIndex"]
            if len(TempDictIndex) == 3:
                TempDictIndexStr = "BackTestDict['"+TempDictIndex[0]+"']['"+TempDictIndex[1]+"']['"+TempDictIndex[2]+"']"
            elif len(TempDictIndex) == 2:
                TempDictIndexStr = "BackTestDict['"+TempDictIndex[0]+"']['"+TempDictIndex[1]+"']"
            elif len(TempDictIndex) == 1:
                TempDictIndexStr = "BackTestDict['"+TempDictIndex[0]+"']"
            else:
                print(TempDictIndex)

            if type(eval(TempDictIndexStr)) == float:
                StartNum = float(StepX.split(':')[0])
                EndNum = float(StepX.split(':')[1])
                StepNum = float(StepX.split(':')[2])
            else:
                StartNum = int(StepX.split(':')[0])
                EndNum = int(StepX.split(':')[1])
                StepNum = int(StepX.split(':')[2])
            StepXList = np.arange(StartNum, EndNum, StepNum).tolist()
            TempDictIndexList[j]["TempDictIndexStr"] = TempDictIndexStr
            TempDictIndexList[j]["StepXList"] = StepXList
            j+=1
            self.GenZFbtFileSum = self.GenZFbtFileSum * len(StepXList)

        self.GenZFbtFileCnt = 0
        self.funx(TempDictIndexList,BackTestDict,TempFolderPath)
        ZBaseFunc.Log2LogBox("Generate %d ZFbt files"%(self.GenZFbtFileSum))
        return


    def funx(self,TempDictIndexList=[],BackTestDict = dict(),TempFolderPath=''):
        TempDictIndexDict = TempDictIndexList.pop()
        if (len(TempDictIndexList) == 0):
            for iPara in TempDictIndexDict['StepXList']:
                ExceStr = TempDictIndexDict['TempDictIndexStr']+'= iPara'
                exec(ExceStr)
                BackTestParaFilePathName = TempFolderPath + '\\BackTestPara_' + datetime.datetime.now().strftime(
                    '%Y-%m-%d %H_%M_%S.%f') + '.ZFbt'
                with open(BackTestParaFilePathName, "w") as f:
                     json.dump(BackTestDict, f, indent=1)
                self.GenZFbtFileCnt +=1
                self.GlobalMainUI.FunAnaGroupProgressBar.setValue(self.GenZFbtFileCnt/self.GenZFbtFileSum * 100)

            return
        else:
            for iPara in TempDictIndexDict['StepXList']:
                ExceStr = TempDictIndexDict['TempDictIndexStr']+'= iPara'
                exec(ExceStr)
                tishen = copy.deepcopy(TempDictIndexList)
                self.funx(tishen,BackTestDict,TempFolderPath)


    def HandleLoadBackTestPara(self):
        pass

    def HandleCancelBackTestPara(self):
        self.BackTestCfgUI.close()
        pass

    def HandleStartGroupBackTestings(self):

        if self.StopFlag == True:
            self.StopFlag = False

            TempFolderPath = os.getcwd() + '\\Data\\05_BackTestResult\\'
            DateTimeStr = time.strftime("%Y-%m-%d %H_%M_%S", time.localtime())
            TempFolderPath = TempFolderPath + DateTimeStr
            os.mkdir(TempFolderPath)
            self.GlobalMainUI.StartBackTesting.setDisabled(True)
            self.GlobalMainUI.StartGroupBackTestings.setText("停止测试")
            time.sleep(1.5)

            GroupProcessSum = len(self.BackTestParaGroups)
            i = 0
            for BackTestParaFilePathName in self.BackTestParaGroups:
                i+=1
                with open(BackTestParaFilePathName, 'r') as load_f:
                    BackTestDict = json.load(load_f)
                self.StartBackTesting(BackTestDict, TempFolderPath)
                self.GlobalMainUI.FunAnaGroupProgressBar.setValue(i/GroupProcessSum * 100)
                os.remove(BackTestParaFilePathName)
                if self.StopFlag == True:
                    break

            self.GlobalMainUI.StartBackTesting.setDisabled(False)
            self.GlobalMainUI.StartGroupBackTestings.setDisabled(False)
            self.GlobalMainUI.StartGroupBackTestings.setText("开始组测试")
        else:
            self.StopFlag = True
            self.GlobalMainUI.StartGroupBackTestings.setDisabled(True)
            self.GlobalMainUI.StartGroupBackTestings.setText("停止测试中")

    def HandleStartBackTesting(self):

        if self.StopFlag == True:
            self.StopFlag = False
            self.GlobalMainUI.StartGroupBackTestings.setDisabled(True)
            self.GlobalMainUI.StartBackTesting.setText("停止测试")
            self.StartBackTesting()
            self.GlobalMainUI.StartGroupBackTestings.setDisabled(False)
            self.GlobalMainUI.StartBackTesting.setDisabled(False)
            self.GlobalMainUI.StartBackTesting.setText("开始单测试")
        else:
            self.StopFlag = True
            self.GlobalMainUI.StartBackTesting.setDisabled(True)
            self.GlobalMainUI.StartBackTesting.setText("停止测试中")

    def StartBackTesting(self,BTPara=None,GroupFolderPath=None):

        self.CleanTable()
        #读取参数


        if BTPara == None:
            BackTestParaFilePathName = os.getcwd() + '\\Data\\00_Config\\DefaultBackTestPara.ZFbt'
            try:
                with open(BackTestParaFilePathName, 'r') as load_f:
                    BackTestDict = json.load(load_f)
                print('Load Default FavorList Config success!!')
            except:
                print('Load Default FavorList Config Fail!!')
                BackTestDict = ZfinanceCfg.BackTestPara
            DateTimeStr = time.strftime("%Y-%m-%d %H_%M_%S", time.localtime())
            TempFolderPath = os.getcwd() + '\\Data\\05_BackTestResult\\' + DateTimeStr
            os.mkdir(TempFolderPath)
        else:
            BackTestDict = BTPara

            DateTimeStr = time.strftime("%Y-%m-%d %H_%M_%S", time.localtime())
            TempFolderPath = GroupFolderPath+ '\\'+DateTimeStr
            os.mkdir(TempFolderPath)

        BackTestParaFilePathName = TempFolderPath + '\\BackTestPara.ZFbt.json'
        with open(BackTestParaFilePathName, "w") as f:
            json.dump(BackTestDict, f,indent=1)
        #
        Row = -1
        RSITP = [
            BackTestDict['RSI']['RSI1']['Length'],
            BackTestDict['RSI']['RSI2']['Length'],
            BackTestDict['RSI']['RSI3']['Length']
        ]
        AEMATP = [
            BackTestDict['AEMATP']['Length1'],
            BackTestDict['AEMATP']['Length2'],
            BackTestDict['AEMATP']['Length3'],
            BackTestDict['AEMATP']['Length4'],
            BackTestDict['AEMATP']['Length5'],
            BackTestDict['AEMATP']['Length6']
        ]
        RaiseScaleInTrendUp = BackTestDict['Trading']['TrendUp']['RaiseScale']
        FallScaleInTrendUp  = BackTestDict['Trading']['TrendUp']['FallScale']
        ElimitInTrendup     = BackTestDict['Trading']['TrendUp']['Elimit']

        RaiseScaleInTrendDn = BackTestDict['Trading']['TrendDn']['RaiseScale']
        FallScaleInTrendDn  = BackTestDict['Trading']['TrendDn']['FallScale']
        ElimitInTrendDn     = BackTestDict['Trading']['TrendDn']['Elimit']

        RaiseScaleInTrendNo = BackTestDict['Trading']['TrendNo']['RaiseScale']
        FallScaleInTrendNo  = BackTestDict['Trading']['TrendNo']['FallScale']
        ElimitInTrendNo     = BackTestDict['Trading']['TrendNo']['Elimit']

        LastIndex           = BackTestDict['Trading']['LastIndex']
        LockBuyLen          = BackTestDict['Trading']['LockBuyLen']
        StopLossRate        = BackTestDict['Trading']['StopLossRate']
        TrendDnLen          = BackTestDict['Trading']['TrendDnRatioLen']
        TrendDnRatio        = BackTestDict['Trading']['TrendDnRatio']
        ClosureRatio        = BackTestDict['Trading']['ClosureRatio']
        RSISellLimit        = BackTestDict['Trading']['RSISellLimit']
        TrendGate           = BackTestDict['Trading']['TrendGate']



        StdPLSum = 0
        for Symbol in self.BMList:
            Row += 1
            #读取数据
            ZBaseFunc.Log2LogBox("Start "+Symbol+" Backtest")
            FileName = ZBaseFunc.GetCompleteFileName('Data/01_TickerDatabase/' + Symbol + '/' + Symbol + '_5m')
            if FileName == None:
                continue
            else:
                Tempdf = pd.read_csv('Data/01_TickerDatabase/' + Symbol + '/' + FileName, sep=',', index_col='DateTime')
                cnt = int(BackTestDict["BackTestDayCount"]["Length"] * 192)
                Tempdf = Tempdf.iloc[-cnt:-1]

            StartDate = Tempdf.index[0]
            EndDate = Tempdf.index[-1]

            StartDate = PySide2.QtWidgets.QTableWidgetItem(StartDate.split(" ")[0])
            EndDate   = PySide2.QtWidgets.QTableWidgetItem(EndDate.split(" ")[0])

            self.GlobalMainUI.BackTestandMonitorTable.setItem(Row, 1, StartDate)
            self.GlobalMainUI.BackTestandMonitorTable.setItem(Row, 2, EndDate)

            AEMA = list()
            RSI = list()

            highLowLength = 10
            Tempdf['LowPriceMin'] = Tempdf["Low"].rolling(highLowLength).min()
            Tempdf['HighPriceMax'] = Tempdf["High"].rolling(highLowLength).max()
            Tempdf.dropna(inplace=True)

            ZBaseFunc.Log2LogBox("Start RSI Calc")
            for i in range(3):
                TP = RSITP[i]
                RSI.append(talib.RSI(Tempdf["Close"], timeperiod=TP))
            for i in range(3):
                Tempdf['RSI_[' + str(RSITP[i]) + ']'] = RSI[i]

            ZBaseFunc.Log2LogBox("Start AEMA Calc")
            for i in range(6):
                self.GlobalMainUI.FunAnaGroupProgressBar.setValue(i*20)
                length = AEMATP[i]
                multiplier1 = 2/(length+1)

                Tempdf['multiplier2'] = abs((Tempdf["Close"] - Tempdf['LowPriceMin']) -
                                            (Tempdf['HighPriceMax'] - Tempdf["Close"])) / \
                                        (Tempdf['HighPriceMax'] - Tempdf['LowPriceMin'])
                Tempdf['alpha'] = multiplier1 * (1+Tempdf['multiplier2'])
                result = sum(Tempdf["Close"].tolist()[0:length-1])/length

                AMA = [np.nan for j in range(length)]
                for k in range(length,len(Tempdf)):
                    result = result+ Tempdf.iat[k,-1]*(Tempdf.iat[k,3]-result)
                    AMA.append(result)

                AEMA.append(AMA)
            for i in range(6):
                Tempdf['AEMA_[' + str(AEMATP[i]) + ']'] = AEMA[i]

            Tempdf['TrendVal'] = Tempdf['AEMA_[' + str(AEMATP[5]) + ']'].diff()
            Tempdf.dropna(inplace=True)



            ThisTradingStatus = ZfinanceCfg.TradingStatu.Watch

            FlCAP  = 0
            FlPLList  = list()
            StdPLList = list()
            FixPLList = list()

            ActionList = list()

            StopLossPrice = 0
            SellByRSIFlag = False
            ProcessCntSum = len(Tempdf)
            TrendDnCnt = 0
            DebugStatus = []
            for i in range(LastIndex):
                DebugStatus.append(ZfinanceCfg.DebugStatusStr[ZfinanceCfg.TradingStatu.Watch][0])
            try:
                ActionList.append({
                    'TimeStamp':Tempdf.index.values[0],
                    'Value':Tempdf.iloc[0]['High'],
                    'Action':ZfinanceCfg.DebugStatusStr[ZfinanceCfg.TradingStatu.Watch][0],
                    'Color':ZfinanceCfg.DebugStatusStr[ZfinanceCfg.TradingStatu.Watch][1]
                })
            except:
                print('help')
                continue
            RSI = [0,0,0]
            StartPrice = Tempdf.iloc[0]['Open']
            StartFun = StartPrice*100

            StdFund = StartFun
            FlSharesQt = 0
            StdSharesQt = 0
            ZBaseFunc.Log2LogBox("Start Auto Trading Calc")
            for i in range(LastIndex, ProcessCntSum):
                ClosePrice = Tempdf.iloc[i]['Close']
                OpenPrice  = Tempdf.iloc[i]['Open']
                TimeStamp = Tempdf.index[i]
                AEMA[0] = Tempdf.iloc[i]['AEMA_[' + str(AEMATP[0]) + ']']
                AEMA[1] = Tempdf.iloc[i]['AEMA_[' + str(AEMATP[1]) + ']']
                AEMA[2] = Tempdf.iloc[i]['AEMA_[' + str(AEMATP[2]) + ']']
                AEMA[3] = Tempdf.iloc[i]['AEMA_[' + str(AEMATP[3]) + ']']
                AEMA[4] = Tempdf.iloc[i]['AEMA_[' + str(AEMATP[4]) + ']']
                AEMA[5] = Tempdf.iloc[i]['AEMA_[' + str(AEMATP[5]) + ']']
                AEMA_LastOne   = Tempdf.iloc[i-1]['AEMA_[' + str(AEMATP[5]) + ']']
                AEMA_LastIndex = Tempdf.iloc[i - LastIndex]['AEMA_[' + str(AEMATP[5]) + ']']
                
                
                RSI[0] = Tempdf.iloc[i]['RSI_[' + str(RSITP[0]) + ']']
                RSI[1] = Tempdf.iloc[i]['RSI_[' + str(RSITP[1]) + ']']
                RSI[2] = Tempdf.iloc[i]['RSI_[' + str(RSITP[2]) + ']']

                Temp = ((AEMA[5] - AEMA_LastOne) / AEMA_LastOne)
                if Temp > TrendGate:
                    TrendMode = ZfinanceCfg.TrendMode.UP
                elif Temp  < -TrendGate:
                    TrendMode = ZfinanceCfg.TrendMode.DN
                else:
                    Temp = ((AEMA[5] - AEMA_LastIndex) / AEMA_LastIndex)
                    if Temp > TrendGate:
                        TrendMode = ZfinanceCfg.TrendMode.UP
                    elif Temp < -TrendGate:
                        TrendMode = ZfinanceCfg.TrendMode.DN
                    else:
                        TrendMode = ZfinanceCfg.TrendMode.NO

                if TrendMode == ZfinanceCfg.TrendMode.UP:
                    RaiseScale  =   RaiseScaleInTrendUp
                    FallScale   =   FallScaleInTrendUp
                    Elimit      =   ElimitInTrendup
                elif TrendMode == ZfinanceCfg.TrendMode.DN:
                    RaiseScale  =   RaiseScaleInTrendDn
                    FallScale   =   FallScaleInTrendDn
                    Elimit      =   ElimitInTrendDn
                else:
                    RaiseScale  =   RaiseScaleInTrendNo
                    FallScale   =   FallScaleInTrendNo
                    Elimit      =   ElimitInTrendNo



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

                if Tempdf.iloc[i]['TrendVal'] < 0:
                    TrendDnCnt += 1
                if i >= TrendDnLen:
                    if Tempdf.iloc[i-TrendDnLen]['TrendVal'] < 0:
                        TrendDnCnt -= 1
                #print("TDC = "+str(TrendDnCnt)+" |i = "+str(i)+"|TrendVal = "+str(Tempdf.iloc[i]['TrendVal']))

                if TrendDnCnt <0:
                    print("Error TrendDnCnt i=",i)
                if TrendDnCnt/TrendDnLen *100 > TrendDnRatio:
                    Buycondition_TrendDnRatio = True
                else:
                    Buycondition_TrendDnRatio = False

                # 三条线接近
                if abs(AEMA[3] - AEMA[4])+abs(AEMA[3] - AEMA[5]) +abs(AEMA[4] - AEMA[5]) <ClosureRatio*(AEMA[3]+AEMA[4]+AEMA[5]) :
                    Buycondition_ClosureRatio = True
                else:
                    Buycondition_ClosureRatio = False

                if Buycondition_AEMA0UpAll and Buycondition_TrendDnRatio and Buycondition_ClosureRatio:
                    Buycondition = True
                else:
                    Buycondition = False
                #---------------------------------------------^BUYCONDITION^------------------------------------------------#

                #---------------------------------------------SELLCONDITION------------------------------------------------#
                AMALowerCnt = 0
                for j in range(1, 5):  # AMA8 > 所有
                    if AEMA[0] < AEMA[j] * FallScale:
                        AMALowerCnt += 1
                if AMALowerCnt >=Elimit:
                    SellCondition_AMALowerCnt = True
                else:
                    SellCondition_AMALowerCnt = False

                if RSI[0] > RSISellLimit:
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
                    StopLossPrice = OpenPrice *StopLossRate/ 100
                    ZBaseFunc.Log2LogBox(TimeStamp+'|Buy:'+str(OpenPrice))
                if (ThisTradingStatus is ZfinanceCfg.TradingStatu.Sell):
                    FlCAP = FlCAP + 100 * OpenPrice
                    FlSharesQt = 0

                    StdFund =StdFund + StdSharesQt*OpenPrice
                    StdSharesQt = 0

                    ZBaseFunc.Log2LogBox(TimeStamp+'|Sell:'+str(OpenPrice))
                if (ThisTradingStatus is ZfinanceCfg.TradingStatu.LockBuy):
                    ReachRelease += 1


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
                        ReachRelease = 0
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
                elif ((ThisTradingStatus is  ZfinanceCfg.TradingStatu.LockBuy) and (ReachRelease > LockBuyLen)):        # 锁买期过期
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

            FPLRow = 3
            FlPLShow = PySide2.QtWidgets.QTableWidgetItem(str(round(FlPLList[-1],2))+'$')
            self.GlobalMainUI.BackTestandMonitorTable.setItem(Row, FPLRow, FlPLShow)

            StdPLRow = 4
            StdPLShow = PySide2.QtWidgets.QTableWidgetItem(str(round(StdPLList[-1],2))+'%')
            self.GlobalMainUI.BackTestandMonitorTable.setItem(Row, StdPLRow, StdPLShow)

            FixPLRow = 5
            FixPLShow = PySide2.QtWidgets.QTableWidgetItem(str(round(FixPLList[-1],2))+'%')
            self.GlobalMainUI.BackTestandMonitorTable.setItem(Row, FixPLRow, FixPLShow)

            StdPLSum = StdPLSum+StdPLList[-1]
            Zplot.DrawCharts(
                Symbol,
                Tempdf.index.values.tolist(),
                np.array(Tempdf.loc[:,['Open','Close','Low','High']]).tolist(),
                Tempdf['Volume'].tolist(),
                Tempdf.loc[:,  ['AEMA_[' + str(AEMATP[0]) + ']',
                                'AEMA_[' + str(AEMATP[1]) + ']',
                                'AEMA_[' + str(AEMATP[2]) + ']',
                                'AEMA_[' + str(AEMATP[3]) + ']',
                                'AEMA_[' + str(AEMATP[4]) + ']',
                                'AEMA_[' + str(AEMATP[5]) + ']']],
                Tempdf['TrendVal'].tolist(),
                Tempdf.loc[:, ['RSI_[' + str(RSITP[0]) + ']',
                               'RSI_[' + str(RSITP[1]) + ']',
                               'RSI_[' + str(RSITP[2]) + ']']],
                ActionList,
                FlPLList, StdPLList,FixPLList,FixPLList,
                BackTestDict,
                TempFolderPath
            )

            if self.StopFlag == True:
                return
        BackTestResultDf = ZBaseFunc.dataframe_generation_from_table(self.GlobalMainUI.BackTestandMonitorTable)
        BackTestResultDf.to_csv(TempFolderPath+'\\BTResult.csv', sep=',',index_label='SYM')
        time.sleep(0.1)

        PLandFolderName = TempFolderPath.replace(TempFolderPath.split('\\')[-1],'{:.4g}'.format(StdPLSum)+'_'+TempFolderPath.split('\\')[-1])

        os.rename(TempFolderPath, PLandFolderName)

        print(BackTestResultDf)

        pass

    def CleanTable(self):
        self.GlobalMainUI.BackTestandMonitorTable.clear()
        self.GlobalMainUI.BackTestandMonitorTable.setRowCount(len(self.BMList))
        self.GlobalMainUI.BackTestandMonitorTable.setColumnCount(len(ZfinanceCfg.BMTableColumeItem) + 1)

        self.GlobalMainUI.BackTestandMonitorTable.verticalHeader().setVisible(False)
        self.GlobalMainUI.BackTestandMonitorTable.horizontalHeader().setDefaultAlignment(PySide2.QtCore.Qt.AlignLeft)
        self.GlobalMainUI.BackTestandMonitorTable.setFont(QFont('song', 8))
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
        for i in range(len(ZfinanceCfg.BMTableColumeItem)):
            self.GlobalMainUI.BackTestandMonitorTable.setColumnWidth(Col, 60)
            Col = Col + 1
        self.GlobalMainUI.BackTestandMonitorTable.setColumnWidth(1, 80)
        self.GlobalMainUI.BackTestandMonitorTable.setColumnWidth(2, 80)
        Temp = ['SYM']
        for i in ZfinanceCfg.BMTableColumeItem:
            Temp.append(i)
        self.GlobalMainUI.BackTestandMonitorTable.setHorizontalHeaderLabels(Temp)

