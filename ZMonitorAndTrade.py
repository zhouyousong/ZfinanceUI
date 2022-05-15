import copy
import random

import requests

import ZfinanceUI_Download
from PySide2.QtWidgets import QApplication, QMessageBox,QFileDialog
from PySide2.QtUiTools import QUiLoader

import multiprocessing
import multiprocessing as mp
from threading import Thread
import ZFavorEditor
import ZBaseFunc
import ZfinanceCfg
import pandas as pd
import ZFunAna
import ZBackTest
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
import ZNotify,ZTrader

GlobalMainUI = None
GlobalApplyResult = []
GlobalResultFilePath = None

GlobalAPP = None
FunAnaProgressBarChannel = None

UILock = multiprocessing.Semaphore(1)
GroupLock = multiprocessing.Semaphore(1)
GlobalGroupRunningFlag = False
GlobalSingleRunningFlag = False


class MonitorAndTradeProc:
    def __init__(self,GlobalUI,APP):
        global GlobalMainUI,GlobalAPP,FunAnaProgressBarChannel

        GlobalMainUI = GlobalUI
        GlobalAPP = APP
        self.GlobalAPP = APP
        self.GlobalMainUI = GlobalUI

        self.GlobalMainUI.SetMonitorAndTradePara.clicked.connect(self.HandleSetMonitorAndTradePara)
        self.GlobalMainUI.StartMonitorAndTrade.clicked.connect(self.HandleStartMonitorAndTrade)

        self.GlobalMainUI.BalanceTable.clear()
        self.GlobalMainUI.BalanceTable.setRowCount(0)
        self.GlobalMainUI.BalanceTable.setColumnCount(len(ZfinanceCfg.BalanceTableColumeItem) + 1)

        ZBaseFunc.CleanTable(ZfinanceCfg.MonitorTableColumeItem,self.GlobalMainUI.MonitorAndTradeTable)

        self.MonitorAndTradeCfgUI = QUiLoader().load('UIDesign\MonitorParaEditor.ui')



        self.MonitorAndTradeCfgUI.LoadMonitorPara.clicked.connect(self.HandleLoadBackTestPara)
        self.MonitorAndTradeCfgUI.ApplyBackTestPara.clicked.connect(self.HandleApplyBackTestPara)
        self.MonitorAndTradeCfgUI.SaveMonitorPara.clicked.connect(self.HandleSaveMonitorPara)

        self.MonitorAndTradeCfgUI.VerifyTradeConfig.clicked.connect(self.HandleVerifyTradeConfig)
        self.MonitorAndTradeCfgUI.SaveTradeConfig.clicked.connect(self.HandleSaveTradeConfig)
        self.MonitorAndTradeCfgUI.CloseMonitorParaEditor.clicked.connect(self.HandleCloseMonitorParaEditor)


        self.MonitorAndTradeCfgUI.MonitorSymbolList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.MonitorAndTradeCfgUI.MonitorSymbolList.customContextMenuRequested[QPoint].connect(self.FavorListChechboxSelectMenu)

        self.MonitorAndTradeCfgUI.ImportToMonitorTable.clicked.connect(self.HandleImportToMonitorTable)

        self.StopFlag = True


        self.GlobalMainUI.StartGroupBackTestings.setDisabled(True)
        self.GlobalMainUI.StartGroupBackTestings.setText("请选参数文件")

        self.GlobalMainUI.StartBackTesting.setDisabled(True)
        self.GlobalMainUI.StartBackTesting.setText("请加入股票")

        self.TradeDict       = ZBaseFunc.LoadConfigFile(FileName="DefaultTradePara.ZFtd",DefaultDict=ZfinanceCfg.TradePara)
        self.MonitorParaDict = ZBaseFunc.LoadConfigFile(FileName="DefaultMonitorPara.ZFmt",DefaultDict=ZfinanceCfg.MonitorPara)

    def HandleSetMonitorAndTradePara(self):

        self.MonitorAndTradeCfgUI.show()

        ZFavorEditor.LoadFavorListCfg(self.MonitorAndTradeCfgUI.MonitorSymbolList, CheckBox=False)

        self.MonitorAndTradeCfgUI.MailNotifyEnable.setChecked(self.TradeDict["MailNotifyEnable"])
        self.MonitorAndTradeCfgUI.SendMailBoxAddr.setText(self.TradeDict["SendMailBoxAddr"])
        self.MonitorAndTradeCfgUI.SendMailBoxPwd.setText(self.TradeDict["SendMailBoxPwd"])
        self.MonitorAndTradeCfgUI.RevMailBoxAddr.setText(self.TradeDict["RevMailBoxAddr"])

        self.MonitorAndTradeCfgUI.TdaAccountMonitorEnable.setChecked(self.TradeDict["TdaAccountMonitorEnable"])
        self.MonitorAndTradeCfgUI.TdaTradeRotEnable.setChecked(self.TradeDict["TdaTradeRotEnable"])
        self.MonitorAndTradeCfgUI.TdaAPIOAuthUserID.setText(self.TradeDict["TdaAPIOAuthUserID"])
        self.MonitorAndTradeCfgUI.TdaAPIRefreshToken.setText(self.TradeDict["TdaAPIRefreshToken"])


        self.MonitorAndTradeCfgUI.MonitorPara.setColumnCount(3)
        self.MonitorAndTradeCfgUI.MonitorPara.setHeaderLabels(('Key', 'Value', 'Comment'))
        self.MonitorAndTradeCfgUI.MonitorPara.clear()
        # self.BackTestCfgUI.BackTestPara.setColumnHidden(2,True)
        for Lv1Key, Lv1Val in self.MonitorParaDict.items():
            Lv1Child = QTreeWidgetItem(self.MonitorAndTradeCfgUI.MonitorPara)
            Lv1Child.setText(0, Lv1Key)
            Lv1Child.setExpanded(True)
            if isinstance(Lv1Val, dict):
                for Lv2Key, Lv2Val in Lv1Val.items():
                    if Lv2Key == 'Enable':
                        Lv1Child.setText(2, 'CheckBox')
                        if Lv2Val == True:
                            Lv1Child.setCheckState(0, Qt.Checked)
                        else:
                            Lv1Child.setCheckState(0, Qt.Unchecked)
                    else:
                        Lv2Child = QTreeWidgetItem(Lv1Child)
                        Lv2Child.setExpanded(True)
                        if isinstance(Lv2Val, dict):
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
                                    if (isinstance(Lv3Val, bool)):
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

    def HandleApplyBackTestPara(self):
        pass

    def HandleVerifyTradeConfig(self):
        SendMailBoxAddr = self.MonitorAndTradeCfgUI.SendMailBoxAddr.text()
        SendMailBoxPwd = self.MonitorAndTradeCfgUI.SendMailBoxPwd.text()
        RevMailBoxAddr =  self.MonitorAndTradeCfgUI.RevMailBoxAddr.text()

        TdaAPIOAuthUserID = self.MonitorAndTradeCfgUI.TdaAPIOAuthUserID.text()
        TdaAPIRefreshToken = self.MonitorAndTradeCfgUI.TdaAPIRefreshToken.text()

        MailNotifyResult = "NA"
        TDAStatus = "NA"
        if self.MonitorAndTradeCfgUI.MailNotifyEnable.isChecked():
            MailNotifyResult = ZNotify.send_email(SendAddr=SendMailBoxAddr,SendPwd=SendMailBoxPwd,RevAddr=RevMailBoxAddr,subject="ZfinanceTest",html_body="Check")
        if self.MonitorAndTradeCfgUI.TdaAccountMonitorEnable.isChecked() or self.MonitorAndTradeCfgUI.TdaTradeRotEnable.isChecked():
            TDAStatus,TdaAPIRefreshToken,TdaAPIAccessToken = ZTrader.GetNewAccessToken(OAuthUserID=TdaAPIOAuthUserID,RefreshToken=TdaAPIRefreshToken,TradeDict=self.TradeDict)
            if TDAStatus =="Get Token Successed":
                self.MonitorAndTradeCfgUI.TdaAPIRefreshToken.setText(TdaAPIRefreshToken)

        QMessageBox.information(None, "警告", "163邮件提醒验证："+MailNotifyResult+"\r\n"+"TDAmeritrade API 验证："+TDAStatus, QMessageBox.Yes,
                                QMessageBox.Yes)


    def HandleCloseMonitorParaEditor(self):
        pass

    def HandleSaveTradeConfig(self):
        self.TradeDict["SendMailBoxAddr"] = self.MonitorAndTradeCfgUI.SendMailBoxAddr.text()
        self.TradeDict["SendMailBoxPwd"] = self.MonitorAndTradeCfgUI.SendMailBoxPwd.text()
        self.TradeDict["RevMailBoxAddr"] = self.MonitorAndTradeCfgUI.RevMailBoxAddr.text()
        self.TradeDict["MailNotifyEnable"]=self.MonitorAndTradeCfgUI.MailNotifyEnable.isChecked()

        self.TradeDict["TdaAPIOAuthUserID"] = self.MonitorAndTradeCfgUI.TdaAPIOAuthUserID.text()
        self.TradeDict["TdaAPIRefreshToken"] = self.MonitorAndTradeCfgUI.TdaAPIRefreshToken.text()
        self.TradeDict["TdaAccountMonitorEnable"] =self.MonitorAndTradeCfgUI.TdaAccountMonitorEnable.isChecked()
        self.TradeDict["TdaTradeRotEnable"] = self.MonitorAndTradeCfgUI.TdaTradeRotEnable.isChecked()

        ZBaseFunc.SaveConfigFile(FileName="DefaultTradePara.ZFtd",DumpDict=self.TradeDict)

    def HandleOpenGroupBackTestParas(self):
        self.BackTestParaGroups, ok = QFileDialog.getOpenFileNames(None, "选择配置文件", 'Data/00_Config/BackTestParaGroup', '(*.ZFbt)')
        if len(self.BackTestParaGroups) == 0:
            self.GlobalMainUI.StartGroupBackTestings.setDisabled(True)
            self.GlobalMainUI.StartGroupBackTestings.setText("请选参数文件")
        else:
            self.GlobalMainUI.StartGroupBackTestings.setText("开始组测试")
            if GlobalSingleRunningFlag == False:
                self.GlobalMainUI.StartGroupBackTestings.setDisabled(False)

    def HandleImportToMonitorTable(self):
        ZBaseFunc.CleanTable(Table=self.GlobalMainUI.MonitorAndTradeTable,TableColumeItem=ZfinanceCfg.MonitorTableColumeItem)
        ZBaseFunc.AddFavorListToTable(InputList=self.MonitorAndTradeCfgUI.MonitorSymbolList,OutputTable=self.GlobalMainUI.MonitorAndTradeTable)
        self.GlobalMainUI.StartMonitorAndTrade.setDisabled(False)
        self.GlobalMainUI.StartMonitorAndTrade.setText("开始监控")
        pass

    def CancelAllChildrenInFavorList(self):
        self.MonitorAndTradeCfgUI.MonitorSymbolList.currentItem().setCheckState(0, PySide2.QtCore.Qt.CheckState.Unchecked)
        cursor = QTreeWidgetItemIterator(self.MonitorAndTradeCfgUI.MonitorSymbolList.currentItem())
        ChildCnt = cursor.value().childCount()
        cursor = cursor.__iadd__(1)

        for i in range(ChildCnt):
            cursor.value().setCheckState(0, PySide2.QtCore.Qt.CheckState.Unchecked)
            cursor = cursor.__iadd__(1)

    def SelectAllChildrenInFavorList(self):
        self.MonitorAndTradeCfgUI.MonitorSymbolList.currentItem().setCheckState(0, PySide2.QtCore.Qt.CheckState.Checked)
        cursor = QTreeWidgetItemIterator(self.MonitorAndTradeCfgUI.MonitorSymbolList.currentItem())
        ChildCnt = cursor.value().childCount()
        cursor = cursor.__iadd__(1)

        for i in range(ChildCnt):
            cursor.value().setCheckState(0, PySide2.QtCore.Qt.CheckState.Checked)
            cursor = cursor.__iadd__(1)

    def FavorListChechboxSelectMenu(self):
        popMenu = QMenu()
        if self.MonitorAndTradeCfgUI.MonitorSymbolList.currentItem().parent() == None:

            SelectAll  = popMenu.addAction('全选')
            CancelAll  = popMenu.addAction("取消全选")

            CancelAll.triggered.connect(self.CancelAllChildrenInFavorList)
            SelectAll.triggered.connect(self.SelectAllChildrenInFavorList)
        popMenu.exec_(QCursor.pos())
        return


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

    def HandleSaveMonitorPara(self):
        self.BackTestCfgUI.close()
        pass

    def HandleStartMonitorAndTrade(self):
        global GlobalOnlineFlag
        if GlobalOnlineFlag:
            requests.Request()

        else:
            pass



    def CleanTable(self):
        self.GlobalMainUI.BackTestTable.clear()
        self.GlobalMainUI.BackTestTable.setRowCount(len(self.BMList))
        self.GlobalMainUI.BackTestTable.setColumnCount(len(ZfinanceCfg.BMTableColumeItem) + 1)

        self.GlobalMainUI.BackTestTable.verticalHeader().setVisible(False)
        self.GlobalMainUI.BackTestTable.horizontalHeader().setDefaultAlignment(PySide2.QtCore.Qt.AlignLeft)
        self.GlobalMainUI.BackTestTable.setFont(QFont('song', 8))
        self.GlobalMainUI.BackTestTable.horizontalHeader().setFont(QFont('song', 8))
        self.GlobalMainUI.BackTestTable.verticalScrollBar().setValue(0)
        Row = 0
        for i in self.BMList:
            SymbolsInTable = PySide2.QtWidgets.QTableWidgetItem(i)
            self.GlobalMainUI.BackTestTable.setRowHeight(Row, 5)
            self.GlobalMainUI.BackTestTable.setItem(Row, 0, SymbolsInTable)
            Row = Row + 1

        self.GlobalMainUI.BackTestTable.setColumnWidth(0, 40)

        Col = 1
        for i in range(len(ZfinanceCfg.BMTableColumeItem)):
            self.GlobalMainUI.BackTestTable.setColumnWidth(Col, 60)
            Col = Col + 1
        self.GlobalMainUI.BackTestTable.setColumnWidth(1, 80)
        self.GlobalMainUI.BackTestTable.setColumnWidth(2, 80)
        Temp = ['SYM']
        for i in ZfinanceCfg.BMTableColumeItem:
            Temp.append(i)
        self.GlobalMainUI.BackTestTable.setHorizontalHeaderLabels(Temp)

