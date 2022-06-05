import copy
import random

import pandas

import ZfinanceUI_Download
from PySide2.QtWidgets import QApplication, QMessageBox,QFileDialog
from PySide2.QtUiTools import QUiLoader

import multiprocessing
import multiprocessing as mp
from threading import Thread
import ZFavorEditor
import ZBaseFunc,ZStrategy,ZfinanceCfg
import pandas as pd
import ZFunAna
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

GlobalMainUI = None
GlobalApplyResult = []
GlobalResultFilePath = None

GlobalAPP = None
FunAnaProgressBarChannel = None

UILock = multiprocessing.Semaphore(1)
GroupLock = multiprocessing.Semaphore(1)
GlobalGroupRunningFlag = False
GlobalSingleRunningFlag = False

def ChildProcessMonitor():
    global GlobalApplyResult,GlobalMainUI,GlobalAPP,FunAnaProgressBarChannel,GlobalGroupRunningFlag

    RestProcess = -1
    FinishedProcess = 0
    for i in GlobalApplyResult:
        try:
            A = i.successful()
            FinishedProcess += 1
        except:
            RestProcess += 1

    if FinishedProcess > 5:
        GlobalMainUI.BackTestTable.verticalScrollBar().setValue(FinishedProcess - 4)

#    UILock.acquire()
    if GlobalGroupRunningFlag == False:
        FunAnaProgressBarChannel.PBarSignal.emit((FinishedProcess + 1)/len(GlobalApplyResult)*100)
#    UILock.release()

    return RestProcess


def SingleBackTestMultiProcessFinished():
    global GlobalMainUI,GlobalResultFilePath,GlobalSingleRunningFlag,GlobalGroupRunningFlag,GroupLock
    StdPLSum = 0
    TempFolderPath = GlobalResultFilePath

#    UILock.acquire()
    BackTestResultDf = ZBaseFunc.dataframe_generation_from_table(GlobalMainUI.BackTestTable)
    BackTestResultDf.to_csv(TempFolderPath + '\\BTResult.csv', sep=',', index_label='SYM')

    PLandFolderName = TempFolderPath.replace(TempFolderPath.split('\\')[-1],
                                             '{:.4g}'.format(StdPLSum) + '_' + TempFolderPath.split('\\')[-1])

    os.rename(TempFolderPath, PLandFolderName)

    print(BackTestResultDf)
    if GlobalGroupRunningFlag == False:
        if GlobalMainUI.StartGroupBackTestings.text() != "请选参数文件":
            GlobalMainUI.StartGroupBackTestings.setDisabled(False)
        GlobalMainUI.StartBackTesting.setDisabled(False)
        GlobalMainUI.StartBackTesting.setText("开始单测试")
        GlobalSingleRunningFlag = False
    else:
        GroupLock.release()
    ZBaseFunc.Log2LogBox("BackTest Finished!!")
#    UILock.release()


def SignelBackTestingErorrCallBack(e):
    print('error')
    print(dir(e), "\n")
    print("-->{}<--".format(e.__cause__))

    if ChildProcessMonitor() == 0:
        SingleBackTestMultiProcessFinished()


def SignelBackTestingCallBack(SymbolResult):
    global GlobalMainUI

    ZBaseFunc.DisplayInTable(GlobalMainUI.BackTestTable,SymbolResult)
    ZBaseFunc.Log2LogBox(SymbolResult["Symbol"] + " BackTest Finished!")

    if ChildProcessMonitor() == 0:
        SingleBackTestMultiProcessFinished()

def SymbolBackTesting(Symbol, StrategyParas,ResultFolderPath):
    ActionList = []
    FlPLList = []
    StdPLList = []
    FixPLList = []
    DrawParaDict = StrategyParas


    Interval = StrategyParas["BackTestPeriod&Interval"]["Interval"]
    Period = StrategyParas["BackTestPeriod&Interval"]["Period"]


    InitOHLCVDataFrame = ZStrategy.GetSymbolInitOHLCV(Symbol=Symbol,                    # 读取初始数据            --系统
                                                      Period=Period,
                                                    Interval=Interval,
                                                  OnlineMode=False)

    USRStrategy = ZStrategy.OpenStrategysPlatform(InitOHLCVDataFrame, StrategyParas)    # 创建开放策略平台对象       --系统
    InitResult = USRStrategy.CalcInitIndicators()                                       # 计算初始指数数据（原始数据） **用户编写**
    SymbolEquity = ZStrategy.EquityPlatform(ShareVol=100,
                                            StartPrice=InitResult["StartPrice"])        # 计算初始指数数据（原始数据） **用户编写**

    HeadPt          = InitResult["SkipLength"]                                          # 前面多少个数据要跳过运算
    TailPt          = InitResult["Length"]                                              # 数据总长度

    ActionList.append({                                                                 # 初始化第一次的状态为观望
        'TimeStamp': InitResult['StartTime'], 'Value': InitResult['HighPrice'],
        'Action': ZfinanceCfg.StrategyStatusTag[ZfinanceCfg.TradingStatu.Watch]["Tag"],
        'Color':  ZfinanceCfg.StrategyStatusTag[ZfinanceCfg.TradingStatu.Watch]["Color"]
    })

    for i in range(HeadPt, TailPt):                                                     # for循环开始迭代计算
        StrategyResult = USRStrategy.LoopStrategys(i)                                   # 策略计算，输出要按照StrategyResult对上  **用户编写**

        if StrategyResult.FlagStatusChanged:                                            # 如果系统有操作状态的变化
            ActionList.append({                                                         # 记录操作变化
                'TimeStamp': StrategyResult.TimeStamp, 'Value': StrategyResult.HighPrice,
                'Action': ZfinanceCfg.StrategyStatusTag[StrategyResult.TradingStatus]["Tag"],
                'Color': ZfinanceCfg.StrategyStatusTag[StrategyResult.TradingStatus]["Color"]
            })
        EquityResult = SymbolEquity.CalcResidualEquity(TradeAction=StrategyResult.TradingStatus,
                                                               OptPrice=StrategyResult.ClosePrice,
                                                               ClosePrice=StrategyResult.ClosePrice)


        FlPLList.append(EquityResult['Float_PL'])                     # 记录floatprofit盈利变化趋势
        StdPLList.append(EquityResult['Std_PL_Ratio'])
        FixPLList.append(EquityResult['Fix_PL_Ratio'])

    Zplot.DrawCharts_X(                                                                 # 输出结果显示 ---系统函数
        Symbol=Symbol,
        TimeStamp=InitOHLCVDataFrame.index.values.tolist(),
        KlineData=np.array(InitOHLCVDataFrame.loc[:, ['Open', 'Close', 'Low', 'High']]).tolist(),
        Volume=InitOHLCVDataFrame['Volume'].tolist(),
        AEMAData=InitOHLCVDataFrame.loc[:, InitResult["IndictorInKlineDraw"]],
        TrendVal = InitOHLCVDataFrame['TrendVal'].tolist(),
        RSIData =InitOHLCVDataFrame.loc[:, InitResult["RSIInDraw"]],
        ActionList = ActionList,
        FlPL=FlPLList, StdPL=StdPLList, FixPL=FixPLList, SP500PL=FixPLList,
        DrawParaDict= DrawParaDict,
        TempFolderPath=ResultFolderPath
    )

    BackTestResult = dict()                                                             # 填入需要在表格里显示的结果数据
    BackTestResult["Symbol"] = Symbol
    BackTestResult["Start"] = InitResult["StartTime"]
    BackTestResult["End"]   = InitResult["EndTime"]
    BackTestResult["FlPL"] = str(round(FlPLList[-1], 2)) + '$'
    BackTestResult["StdPL"] = str(round(StdPLList[-1], 2)) + '%'
    BackTestResult["FixPL"] = str(round(FixPLList[-1], 2)) + '%'
    BackTestResult["ClosePrice"] = str(round(StrategyResult.ClosePrice , 2)) + '$'
    return BackTestResult

class SignalThreadChannel(QObject):
    TableSignal = Signal(int,int,int)
    PBarSignal = Signal(int)
    LPBarSignal = Signal(pd.DataFrame)

def UpdateFunAnaProgressBarWidget(Process):
    global GlobalMainUI
    GlobalMainUI.FunAnaGroupProgressBar.setValue(Process)

class BackTestProc:
    def __init__(self,GlobalUI,APP):
        global GlobalMainUI,GlobalAPP,FunAnaProgressBarChannel

        GlobalMainUI = GlobalUI
        GlobalAPP = APP
        self.GlobalAPP = APP
        self.GlobalMainUI = GlobalUI

        self.GlobalMainUI.SetBackTestPara.clicked.connect(self.HandleSetBackTestPara)
        self.GlobalMainUI.StartBackTesting.clicked.connect(self.HandleStartBackTesting)
        self.GlobalMainUI.OpenGroupBackTestParas.clicked.connect(self.HandleOpenGroupBackTestParas)
        self.GlobalMainUI.StartGroupBackTestings.clicked.connect(self.HandleStartGroupBackTestings)

        ZBaseFunc.CleanTable(ZfinanceCfg.BackTestTableColumeItem,self.GlobalMainUI.BackTestTable)

        self.GlobalMainUI.BackTestTable.verticalHeader().setVisible(False)
        self.GlobalMainUI.BackTestTable.horizontalHeader().setDefaultAlignment(PySide2.QtCore.Qt.AlignLeft)
        self.GlobalMainUI.BackTestTable.setFont(QFont('song', 8))
        self.GlobalMainUI.BackTestTable.horizontalHeader().setFont(QFont('song', 8))
        self.GlobalMainUI.BackTestTable.verticalScrollBar().setValue(0)


        self.BackTestCfgUI = QUiLoader().load('UIDesign\BackTestingParaEditor.ui')

        self.BackTestCfgUI.SaveBackTestPara.clicked.connect(self.HandleSaveBackTestPara)
        self.BackTestCfgUI.GenBackTestParaFiles.clicked.connect(self.HandleGenBackTestParaFiles)
        self.BackTestCfgUI.LoadBackTestPara.clicked.connect(self.HandleLoadBackTestPara)
        self.BackTestCfgUI.CancelBackTestPara.clicked.connect(self.HandleCancelBackTestPara)


        self.BackTestCfgUI.BackTestSymbolList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.BackTestCfgUI.BackTestSymbolList.customContextMenuRequested[QPoint].connect(self.FavorListChechboxSelectMenu)
        self.BackTestCfgUI.ImportSymbolsToBackTest.clicked.connect(self.HandleImportSymbolsToBackTest)
        self.GlobalMainUI.FunAnaGroupProgressBar.setValue(0)

        self.StopFlag = True

        FunAnaProgressBarChannel = SignalThreadChannel()
        FunAnaProgressBarChannel.PBarSignal.connect(UpdateFunAnaProgressBarWidget)

        self.GlobalMainUI.StartGroupBackTestings.setDisabled(True)
        self.GlobalMainUI.StartGroupBackTestings.setText("请选参数文件")

        self.GlobalMainUI.StartBackTesting.setDisabled(True)
        self.GlobalMainUI.StartBackTesting.setText("请加入股票")


    def HandleOpenGroupBackTestParas(self):
        self.BackTestParaGroups, ok = QFileDialog.getOpenFileNames(None, "选择配置文件", 'Data/00_Config/BackTestParaGroup', '(*.ZFbt)')
        if len(self.BackTestParaGroups) == 0:
            self.GlobalMainUI.StartGroupBackTestings.setDisabled(True)
            self.GlobalMainUI.StartGroupBackTestings.setText("请选参数文件")
        else:
            self.GlobalMainUI.StartGroupBackTestings.setText("开始组测试")
            if GlobalSingleRunningFlag == False:
                self.GlobalMainUI.StartGroupBackTestings.setDisabled(False)

    def HandleImportSymbolsToBackTest(self):

        ZBaseFunc.CleanTable(Table=self.GlobalMainUI.BackTestTable,TableColumeItem=ZfinanceCfg.BackTestTableColumeItem)
        ZBaseFunc.AddFavorListToTable(InputList=self.BackTestCfgUI.BackTestSymbolList,OutputTable=self.GlobalMainUI.BackTestTable)
        self.GlobalMainUI.StartBackTesting.setDisabled(False)
        self.GlobalMainUI.StartBackTesting.setText("开始单测试")

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
                                elif type(self.BackTestDict[Lv1Key][Lv2Key][cursor.value().text(0)]) == int:
                                    self.BackTestDict[Lv1Key][Lv2Key][cursor.value().text(0)] = int(cursor.value().text(1))
                                elif type(self.BackTestDict[Lv1Key][Lv2Key][cursor.value().text(0)]) == str:
                                    self.BackTestDict[Lv1Key][Lv2Key][cursor.value().text(0)] = str(cursor.value().text(1))
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
                            elif type(self.BackTestDict[Lv1Key][cursor.value().text(0)]) == int:
                                self.BackTestDict[Lv1Key][cursor.value().text(0)] = int(cursor.value().text(1))
                            elif type(self.BackTestDict[Lv1Key][cursor.value().text(0)]) == str:
                                self.BackTestDict[Lv1Key][cursor.value().text(0)] = str(cursor.value().text(1))
                        cursor = cursor.__iadd__(1)
            else:
                if type(self.BackTestDict[Lv1Key[cursor.value().text(0)]]) == float:
                    self.BackTestDict[Lv1Key[cursor.value().text(0)]] = float(cursor.value().text(1))
                elif type(self.BackTestDict[Lv1Key[cursor.value().text(0)]]) == int:
                    self.BackTestDict[Lv1Key][cursor.value().text(0)] = int(cursor.value().text(1))
                elif type(self.BackTestDict[Lv1Key[cursor.value().text(0)]]) == str:
                    self.BackTestDict[Lv1Key][cursor.value().text(0)] = str(cursor.value().text(1))
                cursor = cursor.__iadd__(1)

        BackTestParaFilePathName = os.getcwd() + '\\Data\\00_Config\\DefaultBackTestPara.ZFbt'
        with open(BackTestParaFilePathName, "w") as f:
            json.dump(self.BackTestDict, f,indent=1)
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
    def GroupBackTestMgrThread(self,TempFolderPath):
        global GlobalGroupRunningFlag,FunAnaProgressBarChannel,GroupLock
        i = 0
        TempLen = len(self.BackTestParaGroups)
        GroupLock.acquire()
        while len(self.BackTestParaGroups) != 0:
            print("start:" + str(i))
            BackTestParaFilePathName = self.BackTestParaGroups.pop()
            with open(BackTestParaFilePathName, 'r') as load_f:
                BackTestDict = json.load(load_f)
            self.StartBackTesting(BackTestDict, TempFolderPath)
            GroupLock.acquire()
            if GlobalGroupRunningFlag == False:
                self.BackTestParaGroups.insert(0,BackTestParaFilePathName)
                break
            os.remove(BackTestParaFilePathName)
            i += 1
            time.sleep(0.2)
            FunAnaProgressBarChannel.PBarSignal.emit((i) / TempLen * 100)
            time.sleep(0.2)

            print("End:"+ str(i))


        GroupLock.release()
        #FunAnaProgressBarChannel.PBarSignal.emit(100)
        self.GlobalMainUI.StartBackTesting.setDisabled(False)
        self.GlobalMainUI.StartGroupBackTestings.setDisabled(False)
        self.GlobalMainUI.StartGroupBackTestings.setText("开始组测试")
        GlobalGroupRunningFlag = False
        if len(self.BackTestParaGroups) == 0:
            self.GlobalMainUI.StartGroupBackTestings.setDisabled(True)
            self.GlobalMainUI.StartGroupBackTestings.setText("请选参数文件")

    def HandleStartGroupBackTestings(self):
        global  GlobalGroupRunningFlag,GroupLock
        if GlobalGroupRunningFlag == False:
            GlobalGroupRunningFlag = True
            ZBaseFunc.Log2LogBox("Start Group BackTest")
            TempFolderPath = os.getcwd() + '\\Data\\05_BackTestResult\\'
            DateTimeStr = time.strftime("%Y-%m-%d %H_%M_%S", time.localtime())
            TempFolderPath = TempFolderPath + DateTimeStr
            os.mkdir(TempFolderPath)
            self.GlobalMainUI.StartBackTesting.setDisabled(True)
            self.GlobalMainUI.StartGroupBackTestings.setText("停止测试")
            time.sleep(1.5)                 #   一定要大于1s，为了让上级文件夹和本级不重名

           # GroupProcessSum = len(self.BackTestParaGroups)
            self.GlobalMainUI.FunAnaGroupProgressBar.setValue(0)
            thread = Thread(target=self.GroupBackTestMgrThread,
                            args=(TempFolderPath,)
                            )
            thread.start()
            #
            # for BackTestParaFilePathName in self.BackTestParaGroups:
            #     i+=1
            #     with open(BackTestParaFilePathName, 'r') as load_f:
            #         BackTestDict = json.load(load_f)
            #
            #     GroupLock.acquire()
            #     self.StartBackTesting(BackTestDict, TempFolderPath)
            #
            #     os.remove(BackTestParaFilePathName)
            #     if self.StopFlag == True:
            #         break

            # self.GlobalMainUI.StartBackTesting.setDisabled(False)
            # self.GlobalMainUI.StartGroupBackTestings.setDisabled(False)
            # self.GlobalMainUI.StartGroupBackTestings.setText("开始组测试")
        else:
            ZBaseFunc.Log2LogBox("Stop Group BackTest")
            self.GlobalMainUI.StartGroupBackTestings.setText("停止测试中")
            self.GlobalMainUI.StartGroupBackTestings.setDisabled(True)
            GlobalGroupRunningFlag = False
            self.p.terminate()
            time.sleep(0.5)
            try:
                GroupLock.release()
            except:
                pass
            # self.GlobalMainUI.StartBackTesting.setDisabled(False)
            # self.GlobalMainUI.StartGroupBackTestings.setDisabled(False)
            # self.GlobalMainUI.StartGroupBackTestings.setText("开始组测试")
            #

    def HandleStartBackTesting(self):
        global GlobalSingleRunningFlag
        if GlobalSingleRunningFlag == False:
            GlobalSingleRunningFlag = True
            ZBaseFunc.Log2LogBox("Start Single BackTest")
            self.GlobalMainUI.StartGroupBackTestings.setDisabled(True)
            self.GlobalMainUI.StartBackTesting.setText("停止测试")
            self.GlobalMainUI.FunAnaGroupProgressBar.setValue(0)
            self.StartBackTesting()
        else:
            ZBaseFunc.Log2LogBox("Stop Single BackTest")
            self.GlobalMainUI.StartBackTesting.setDisabled(True)
            self.GlobalMainUI.StartBackTesting.setText("停止测试中")
            self.p.terminate()

            self.GlobalMainUI.StartBackTesting.setDisabled(False)
            self.GlobalMainUI.StartBackTesting.setText("开始单测试")
            if GlobalMainUI.StartGroupBackTestings.text() != "请选参数文件":
                self.GlobalMainUI.StartGroupBackTestings.setDisabled(False)
            GlobalSingleRunningFlag = False

    def StartBackTesting(self,BTPara=None,GroupFolderPath=None):
        global GlobalApplyResult,GlobalResultFilePath
        global GlobalMainUI, GlobalResultFilePath

        BackTestList = ZBaseFunc.RefreshTable(Table=self.GlobalMainUI.BackTestTable)
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

        GlobalResultFilePath = TempFolderPath

        ZBaseFunc.Log2LogBox("Start Backtest ")
        self.p = mp.Pool(processes=BackTestDict['ProcessConfig']['ProcessorCnt'])
        j = 0
        AsyncResult = []
        for i in  BackTestList:
            j += 1
            AsyncResult.append(self.p.apply_async(func=SymbolBackTesting, args=(i,BackTestDict,TempFolderPath),callback=SignelBackTestingCallBack,error_callback=SignelBackTestingErorrCallBack)),print("SymbolBackTesting")
        GlobalApplyResult = AsyncResult
        self.p.close()

