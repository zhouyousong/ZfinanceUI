from PySide2.QtWidgets import QApplication, QMessageBox,QFileDialog
from PySide2.QtUiTools import QUiLoader

import multiprocessing
import multiprocessing as mp
from threading import Thread
import ZFavorEditor
import ZBaseFunc
import ZfinanceCfg
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
import ZNotify,ZTrader,ZStrategy

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
        self.StrategyPathDict = dict()

        self.GlobalMainUI.SetMonitorAndTradePara.clicked.connect(self.HandleSetMonitorAndTradePara)
        self.GlobalMainUI.StartMonitorAndTrade.clicked.connect(self.HandleStartMonitorAndTrade)


        self.BalanceTable           = ZBaseFunc.TableOpt(TargetTable=self.GlobalMainUI.BalanceTable,
                                                         TableColumeItem= ZfinanceCfg.BalanceTableColumeItem)
        self.MonitorAndTradeTable   = ZBaseFunc.TableOpt(TargetTable=self.GlobalMainUI.MonitorAndTradeTable,
                                                         TableColumeItem=ZfinanceCfg.MonitorTableColumeItem)

        self.MonitorAndTradeCfgUI = QUiLoader().load('UIDesign\MonitorParaEditor.ui')


        self.MonitorAndTradeCfgUI.AddBackTestPara.clicked.connect(self.HandleAddBackTestPara)
        self.MonitorAndTradeCfgUI.ImportToMonitorTable.clicked.connect(self.HandleImportToMonitorTable)

        self.MonitorAndTradeCfgUI.CleanMonitorTable.clicked.connect(self.HandleCleanMonitorTable)
        self.MonitorAndTradeCfgUI.SaveMonitorConfigPara.clicked.connect(self.HandleSaveMonitorAndTradePara)

        self.MonitorAndTradeCfgUI.VerifyTradeConfig.clicked.connect(self.HandleVerifyTradeConfig)
        self.MonitorAndTradeCfgUI.SaveTradeConfig.clicked.connect(self.HandleSaveTradeConfig)
        self.MonitorAndTradeCfgUI.CloseMonitorParaEditor.clicked.connect(self.HandleCloseMonitorParaEditor)


        self.MonitorAndTradeCfgUI.FavorSymbolList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.MonitorAndTradeCfgUI.FavorSymbolList.customContextMenuRequested[QPoint].connect(self.FavorListChechboxSelectMenu)

        self.MonitorAndTradeCfgUI.MonitorParaTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.MonitorAndTradeCfgUI.MonitorParaTree.customContextMenuRequested[QPoint].connect(self.MonitorParaTreeSelectMenu)

        self.GlobalMainUI.MonitorAndTradeTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.GlobalMainUI.MonitorAndTradeTable.customContextMenuRequested[QPoint].connect(self.MonitorAndTradeTableSelectMenu)


        self.StopFlag = True


        self.GlobalMainUI.StartGroupBackTestings.setDisabled(True)
        self.GlobalMainUI.StartGroupBackTestings.setText("??????????????????")

        self.GlobalMainUI.StartBackTesting.setDisabled(True)
        self.GlobalMainUI.StartBackTesting.setText("???????????????")

        self.TradeDict       = ZBaseFunc.LoadConfigFile(FileName="DefaultTradePara.ZFtd",DefaultDict=ZfinanceCfg.TradePara)
        self.MonitorParaDict = ZBaseFunc.LoadConfigFile(FileName="DefaultMonitorPara.ZFmt",DefaultDict=ZfinanceCfg.MonitorPara)
        self.TDAAPI = ZTrader.TDAAPIs(OAuthUserID=self.TradeDict["TdaAPIOAuthUserID"],TdaAccountID=self.TradeDict["TdaAccountID"],RefreshToken=self.TradeDict["TdaAPIRefreshToken"])
    def HandleSetMonitorAndTradePara(self):

        self.MonitorAndTradeCfgUI.show()

        self.MonitorAndTradeCfgUI.MailNotifyEnable.setChecked(self.TradeDict["MailNotifyEnable"])
        self.MonitorAndTradeCfgUI.SendMailBoxAddr.setText(self.TradeDict["SendMailBoxAddr"])
        self.MonitorAndTradeCfgUI.SendMailBoxPwd.setText(self.TradeDict["SendMailBoxPwd"])
        self.MonitorAndTradeCfgUI.RevMailBoxAddr.setText(self.TradeDict["RevMailBoxAddr"])

        self.MonitorAndTradeCfgUI.TdaAccountMonitorEnable.setChecked(self.TradeDict["TdaAccountMonitorEnable"])
        self.MonitorAndTradeCfgUI.TdaTradeRotEnable.setChecked(self.TradeDict["TdaTradeRotEnable"])
        self.MonitorAndTradeCfgUI.TdaAPIOAuthUserID.setText(self.TradeDict["TdaAPIOAuthUserID"])
        self.MonitorAndTradeCfgUI.TdaAccountID.setText(self.TradeDict["TdaAccountID"])
        self.MonitorAndTradeCfgUI.TdaAPIRefreshToken.setText(self.TradeDict["TdaAPIRefreshToken"])

        self.MonitorParaTree = ZBaseFunc.TreeListOpt(TargetTreeList=self.MonitorAndTradeCfgUI.MonitorParaTree,
                                                     TreeColumeItem=ZfinanceCfg.MonitorConfigTreeColumeItem)
        self.FavorSymbolList = ZBaseFunc.TreeListOpt(TargetTreeList=self.MonitorAndTradeCfgUI.FavorSymbolList,
                                                     TreeColumeItem=["SYMBOL"])
        ZFavorEditor.LoadFavorListCfg(self.MonitorAndTradeCfgUI.FavorSymbolList, CheckBox=False)

        TempFolderPath = os.getcwd() + "\\Data\\00_Config\\DefaultMonitorAndTrade.ZMTcfg"
        self.MonitorParaTree.LoadFromConfigFile_L2(FileName=TempFolderPath)

    def HandleVerifyTradeConfig(self):
        SendMailBoxAddr = self.MonitorAndTradeCfgUI.SendMailBoxAddr.text()
        SendMailBoxPwd = self.MonitorAndTradeCfgUI.SendMailBoxPwd.text()
        RevMailBoxAddr =  self.MonitorAndTradeCfgUI.RevMailBoxAddr.text()

        TdaAPIOAuthUserID = self.MonitorAndTradeCfgUI.TdaAPIOAuthUserID.text()
        TdaAPIRefreshToken = self.MonitorAndTradeCfgUI.TdaAPIRefreshToken.text()
        TdaAccountID = self.MonitorAndTradeCfgUI.TdaAccountID.text()

        MailNotifyResult = "NA"
        TDAAPIStatus = "NA"
        TDAAccountStatus = "NA"
        if self.MonitorAndTradeCfgUI.MailNotifyEnable.isChecked():
            MailNotifyResult = ZNotify.send_email(SendAddr=SendMailBoxAddr,SendPwd=SendMailBoxPwd,RevAddr=RevMailBoxAddr,subject="ZfinanceTest",html_body="Check")
        if self.MonitorAndTradeCfgUI.TdaAccountMonitorEnable.isChecked() or self.MonitorAndTradeCfgUI.TdaTradeRotEnable.isChecked():
            TDAAPIStatus,TdaAPIRefreshToken,TdaAPIAccessToken = self.TDAAPI.GetNewAccessToken(OAuthUserID=TdaAPIOAuthUserID,RefreshToken=TdaAPIRefreshToken,TradeDict=self.TradeDict)
            if TDAAPIStatus =="Get Token Successed":
                self.MonitorAndTradeCfgUI.TdaAPIRefreshToken.setText(TdaAPIRefreshToken)
                ZBaseFunc.Log2LogBox("AccessToken:"+TdaAPIAccessToken)
                if self.MonitorAndTradeCfgUI.TdaTradeRotEnable.isChecked():
                    TDAAccountStatus,TDAAccountInfo = self.TDAAPI.GetAccountInfo(TdaAccountID = TdaAccountID,TdaAPIAccessToken = TdaAPIAccessToken)

        QMessageBox.information(None, "??????", "163?????????????????????"+MailNotifyResult+"\r\n"+"TDAmeritrade API ?????????"+TDAAPIStatus+"\r\n"+"Tda Account?????????"+TDAAccountStatus, QMessageBox.Yes,
                                QMessageBox.Yes)
    def HandleCloseMonitorParaEditor(self):
        self.MonitorAndTradeCfgUI.close()
        pass
    def HandleSaveTradeConfig(self):

        self.TradeDict["MailNotifyEnable"]=self.MonitorAndTradeCfgUI.MailNotifyEnable.isChecked()
        self.TradeDict["SendMailBoxAddr"] = self.MonitorAndTradeCfgUI.SendMailBoxAddr.text()
        self.TradeDict["SendMailBoxPwd"] = self.MonitorAndTradeCfgUI.SendMailBoxPwd.text()
        self.TradeDict["RevMailBoxAddr"] = self.MonitorAndTradeCfgUI.RevMailBoxAddr.text()

        self.TradeDict["TdaAccountMonitorEnable"] =self.MonitorAndTradeCfgUI.TdaAccountMonitorEnable.isChecked()
        self.TradeDict["TdaTradeRotEnable"] = self.MonitorAndTradeCfgUI.TdaTradeRotEnable.isChecked()
        self.TradeDict["TdaAPIOAuthUserID"] = self.MonitorAndTradeCfgUI.TdaAPIOAuthUserID.text()
        self.TradeDict["TdaAccountID"] = self.MonitorAndTradeCfgUI.TdaAccountID.text()
        self.TradeDict["TdaAPIRefreshToken"] = self.MonitorAndTradeCfgUI.TdaAPIRefreshToken.text()

        ZBaseFunc.SaveConfigFile(FileName="DefaultTradePara.ZFtd",DumpDict=self.TradeDict)
    def HandleOpenGroupBackTestParas(self):
        self.BackTestParaGroups, ok = QFileDialog.getOpenFileNames(None, "??????????????????", 'Data/00_Config/BackTestParaGroup', '(*.ZFbt)')
        if len(self.BackTestParaGroups) == 0:
            self.GlobalMainUI.StartGroupBackTestings.setDisabled(True)
            self.GlobalMainUI.StartGroupBackTestings.setText("??????????????????")
        else:
            self.GlobalMainUI.StartGroupBackTestings.setText("???????????????")
            if GlobalSingleRunningFlag == False:
                self.GlobalMainUI.StartGroupBackTestings.setDisabled(False)

    def HandleCleanMonitorTable(self):
        self.MonitorAndTradeTable.InitTable()
    def HandleImportToMonitorTable(self):

        SymbolDict = dict()

        StrategyList = self.MonitorParaTree.GetL0RootItems()
        for Strategy in StrategyList:
            SymbolList = self.MonitorParaTree.GetChildrenOfRootByName(Strategy["StrategyName"])
            self.StrategyPathDict[Strategy["StrategyName"]] = Strategy["StrategyPath"]
            for Symbol in SymbolList:
                SymbolDict["Symbol"] = Symbol
                SymbolDict["Strategy"] = Strategy["StrategyName"]
                self.MonitorAndTradeTable.AddOneRowInTable(RowDict=SymbolDict)

        self.GlobalMainUI.StartMonitorAndTrade.setText("????????????")
        pass
    def MonitorAndTradeTableSelectMenu(self):           #??????table???????????????
        popMenu = QMenu()
        print(self.GlobalMainUI.MonitorAndTradeTable.currentRow())
        print(self.GlobalMainUI.MonitorAndTradeTable.currentColumn())
        if(self.GlobalMainUI.MonitorAndTradeTable.currentColumn() == 0):
            SelectAll  = popMenu.addAction("????????????")
            CancelAll  = popMenu.addAction("????????????")
            Delete     = popMenu.addAction("??????")
            ModifyName = popMenu.addAction("??????")
        else:
            SelectAll  = popMenu.addAction('????????????')
            CancelAll  = popMenu.addAction("??????????????????")
            Delete     = popMenu.addAction("????????????")
            ModifyName = popMenu.addAction("??????????????????")

        CancelAll.triggered.connect(self.CancelAllChildrenInMonitorParaTree)
        SelectAll.triggered.connect(self.SelectAllChildrenInMonitorParaTree)
        Delete.triggered.connect(self.DeleteStrategyInMonitorParaTree)
        ModifyName.triggered.connect(self.ModifyNameStrategyNameInMonitorParaTree)

        popMenu.exec_(QCursor.pos())
    def CancelAllChildrenInMonitorParaTree(self):
        self.MonitorParaTree.SetCheckChildrenOfSelectRoot(Check=False)
        pass
    def SelectAllChildrenInMonitorParaTree(self):
        self.MonitorParaTree.SetCheckChildrenOfSelectRoot(Check=True)
        pass
    def DeleteStrategyInMonitorParaTree(self):
        self.MonitorParaTree.DelSelected()
        pass
    def ModifyNameStrategyNameInMonitorParaTree(self):
        TempName = self.MonitorParaTree.GetSelectedItemName()
        text, ok = QInputDialog.getText(None, '???????????????', '?????????????????????:',text=TempName)
        if ok:
            Roots = self.MonitorParaTree.GetL0RootItems()
            RootsName = []
            for temp in Roots:
                RootsName.append(temp['StrategyName'])

            if text  in RootsName:
                QMessageBox.information(None, "??????", "????????????", QMessageBox.Yes,QMessageBox.Yes)
                return
            self.MonitorParaTree.ModifySelected(text)
    def MonitorParaTreeSelectMenu(self):
        popMenu = QMenu()
        if self.MonitorAndTradeCfgUI.MonitorParaTree.currentItem().parent() == None:
            SelectAll  = popMenu.addAction('??????')
            CancelAll  = popMenu.addAction("????????????")
            Delete     = popMenu.addAction("??????")
            ModifyName = popMenu.addAction("??????")

            CancelAll.triggered.connect(self.CancelAllChildrenInMonitorParaTree)
            SelectAll.triggered.connect(self.SelectAllChildrenInMonitorParaTree)
            Delete.triggered.connect(self.DeleteStrategyInMonitorParaTree)
            ModifyName.triggered.connect(self.ModifyNameStrategyNameInMonitorParaTree)
        else:
            Delete = popMenu.addAction("??????")

            Delete.triggered.connect(self.DeleteStrategyInMonitorParaTree)
        popMenu.exec_(QCursor.pos())
    def CancelAllChildrenInFavorList(self):
        self.FavorSymbolList.SetCheckChildrenOfSelectRoot(Check=False)
    def SelectAllChildrenInFavorList(self):
        self.FavorSymbolList.SetCheckChildrenOfSelectRoot(Check=True)
    def ImportAllChildren_To_MonitorParaTree(self):
        SymbolList = self.FavorSymbolList.GetCheckedSymbol(Check=True)
        for SYM in SymbolList:
            self.MonitorParaTree.AddChildToSelectRoot(AddItem=SYM, CheckBox=True)
    def ImportThisChildren_To_MonitorParaTree(self):
        Children = self.FavorSymbolList.GetChildrenOfSelectRoot()
        if type(Children) == type(list()):
            for Child in Children:
                self.MonitorParaTree.AddChildToSelectRoot(AddItem=Child, CheckBox=True)
        else:
            self.MonitorParaTree.AddChildToSelectRoot(AddItem=Children, CheckBox=True)
    def FavorListChechboxSelectMenu(self):
        popMenu = QMenu()
        if self.MonitorAndTradeCfgUI.FavorSymbolList.currentItem().parent() == None:
            SelectAll  = popMenu.addAction('??????')
            CancelAll  = popMenu.addAction("????????????")
            ImportAll = popMenu.addAction("?????????????????????")
            ImportThis = popMenu.addAction("????????????????????????")

            CancelAll.triggered.connect(self.CancelAllChildrenInFavorList)
            SelectAll.triggered.connect(self.SelectAllChildrenInFavorList)
            ImportAll.triggered.connect(self.ImportAllChildren_To_MonitorParaTree)
            ImportThis.triggered.connect(self.ImportThisChildren_To_MonitorParaTree)
        else:
            ImportThis = popMenu.addAction("???????????????")

            ImportThis.triggered.connect(self.ImportThisChildren_To_MonitorParaTree)


        popMenu.exec_(QCursor.pos())
        return
    def HandleSaveMonitorAndTradePara(self):
        TempFolderPath = os.getcwd() + "\\Data\\00_Config\\DefaultMonitorAndTrade.ZMTcfg"
        self.MonitorParaTree.SaveToConfigFile_L2(FilePath=TempFolderPath)
    def HandleAddBackTestPara(self):
        BackTestParaGroups, ok = QFileDialog.getOpenFileNames(None, "??????????????????",
                                                                   'Data/00_Config/BackTestParaGroup',
                                                                   '(*.ZFbt)')
        if ok:
            Roots = self.MonitorParaTree.GetL0RootItems()
            RootsName = []
            for temp in Roots:
                RootsName.append(temp['StrategyName'])

            i = 0
            PropertyX = dict()
            for BackTestPara in BackTestParaGroups:
                ShortName = BackTestPara.split('/')[-1].split('.ZFbt')[0]
                while ShortName in RootsName:
                    i += 1
                    ShortName = BackTestPara.split('/')[-1].split('.ZFbt')[0]+'_('+str(i)+')'
                PropertyX["StrategyPath"] = BackTestPara
                self.MonitorParaTree.AddL1RootToTreeList(AddItem = ShortName,Property=PropertyX,CheckBox=True)
        else:
            return
    def HandleSaveMonitorPara(self):
        self.BackTestCfgUI.close()
        pass
    def GetStrategyParaDict(self,StrategyName):
        return ZBaseFunc.LoadConfigFilePath(self.StrategyPathDict[StrategyName],dict())
    def HandleStartMonitorAndTrade(self):
        global GlobalOnlineFlag
        ##############################################????????????XXXXXXXXX
        self.HandleSetMonitorAndTradePara()
        self.HandleVerifyTradeConfig()
        ZBaseFunc.SetDLAPIPara('PROXY','http://127.0.0.1:7890')
        ZBaseFunc.TestTheAPI(Platfrom=ZfinanceCfg.DownloadPlatform.yfinance)
        ZBaseFunc.TestTheAPI(Platfrom=ZfinanceCfg.DownloadPlatform.efinance)
        ZBaseFunc.TestTheAPI(Platfrom=ZfinanceCfg.DownloadPlatform.TdaAPI)

        #######################################################

  #      self.TDAAPI.GetNewAccessToken(TradeDict=self.TradeDict)

  #      Status,AccountInfo = self.TDAAPI.GetAccountInfo()
  #      self.GlobalMainUI.NetLiqInTdaAccount.display(AccountInfo["NetLiq"])
        sym = self.MonitorAndTradeTable.GetOneRowInTable(1)
        StrategyParas = self.GetStrategyParaDict(sym['Strategy'])
        self.MonitorTheSymbol( sym['Symbol'], StrategyParas)

    def WaitNewData(self, Symbol = "",Interval = "5m",SleepTime = 3,LastDataTimeStamp = ""):
        DisplayResult = dict()
        SYM = ZBaseFunc.MarketQuotations(Symbol)
        DisplayResult["Symbol"] = Symbol

        while True :
            DisplayResult["RT Info"] = SYM.GetCurrentPrice()
            ZBaseFunc.DisplayInTable(ResultTable=self.GlobalMainUI.MonitorAndTradeTable,SymbolResult = DisplayResult)
            time.sleep(SleepTime)
            Tempdf = SYM.GetCurrentData()
            if (Interval == '1d'):
                Tempdf.index = Tempdf.index.strftime("%Y-%m-%d")
            else:
                Tempdf.index = Tempdf.index.strftime("%Y-%m-%d %H:%M")

            if Tempdf.index[-1] != LastDataTimeStamp:
                NewDf = Tempdf.iloc[LastDataTimeStamp:, :]
                break
        DisplayResult["RT Info"] = "Computing.."
        ZBaseFunc.DisplayInTable(ResultTable=self.GlobalMainUI.MonitorAndTradeTable,SymbolResult = DisplayResult)
        return NewDf , len(NewDf)



        pass
    def MonitorTheSymbol(self,Symbol,StrategyParas):

        ActionList = []
        SymbolResult = dict()
        Interval = StrategyParas["Period&Interval"]["Interval"]
        Period   = StrategyParas["Period&Interval"]["Period"]

        SymbolResult["Symbol"] = Symbol

        InitOHLCVDataFrame = ZStrategy.GetSymbolInitOHLCV(Symbol=Symbol,                            # ??????????????????            --??????
                                                          Period=Period,
                                                          Interval=Interval,
                                                          OnlineMode=True)

        USRStrategy  = ZStrategy.OpenStrategysPlatform(InitOHLCVDataFrame, StrategyParas)           # ??????????????????????????????       --??????
        InitResult   = USRStrategy.CalcInitIndicators()                                             # ?????????????????????????????????????????? **????????????**
        SymbolEquity = ZStrategy.EquityPlatform(ShareVol=100,StartPrice=InitResult["StartPrice"])   # ?????????????????????????????????????????? **????????????**

        HeadPt = InitResult["SkipLength"]                                                   # ????????????????????????????????????
        TailPt = InitResult["Length"]                                                       # ???????????????

        ActionList.append({                                                                 # ????????????????????????????????????
            'TimeStamp': InitResult['StartTime'], 'Value': InitResult['HighPrice'],
            'Action': ZfinanceCfg.StrategyStatusTag[ZfinanceCfg.TradingStatu.Watch]["Tag"],
            'Color': ZfinanceCfg.StrategyStatusTag[ZfinanceCfg.TradingStatu.Watch]["Color"]
        })

        #?????????
        while True:
            #for???????????????????????????
            for i in range(HeadPt, TailPt):                                                     # for????????????????????????
                StrategyResult = USRStrategy.LoopStrategys(i)                                   # ??????????????????????????????StrategyResult??????  **????????????**

                if StrategyResult.FlagStatusChanged:                                            # ????????????????????????????????????
                    ActionList.append({                                                         # ??????????????????
                        'TimeStamp': StrategyResult.TimeStamp, 'Value': StrategyResult.HighPrice,
                        'Action': ZfinanceCfg.StrategyStatusTag[StrategyResult.TradingStatus]["Tag"],
                        'Color': ZfinanceCfg.StrategyStatusTag[StrategyResult.TradingStatus]["Color"]
                    })
                EquityResult = SymbolEquity.CalcResidualEquity(TradeAction=StrategyResult.TradingStatus,
                                                               OptPrice=StrategyResult.ClosePrice,
                                                               ClosePrice=StrategyResult.ClosePrice)

            HeadPt = TailPt
            # ?????????????????? ---????????????
            SymbolResult["NOTIFY"]      = 'OFF'
            SymbolResult["TDA AUTO"]    = 'OFF'
            SymbolResult["Trading"]     =ZfinanceCfg.StrategyStatusTag[StrategyResult.TradingStatus]["Tag"]
            SymbolResult["Price@Start"] = str(InitResult["StartPrice"])+'@'+InitResult['StartTime'].split(' ')[0]
            SymbolResult["Update"]      = StrategyResult.TimeStamp.split(' ')[1]
            SymbolResult["Curr Price"]  = str(StrategyResult.ClosePrice)
            SymbolResult["StdPL Ratio"] = str(round(EquityResult["Std_PL_Ratio"], 2)) + '%'
            SymbolResult["FixPL Ratio"] = str(round(EquityResult["Fix_PL_Ratio"], 2)) + '%'

            self.MonitorAndTradeTable.RefreshOneRowInTable(SymbolResult=SymbolResult)

            return
            # ????????????  --????????????
            NewOHLCVDataFrame = self.WaitNewData(Symbol=Symbol,Interval = Interval,SleepTime=1/100)
            TailPt = TailPt + len(NewOHLCVDataFrame)
            #??????????????? ??????????????????= ??????????????????????????????????????????  --?????????
            self.USRStrategy.CalcNewIndicators(NewOHLCVDataFrame)
