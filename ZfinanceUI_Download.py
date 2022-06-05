#favor的勾选
#position必须是数字的规范化
#停盘的记为灰色
#Favor列表移动
#分类添加Favor列表
#分类进行智能提取并标注颜色


import datetime
from ftplib import FTP
import pandas
import pandas as pd
import efinance
import glob
from joblib import Parallel,delayed

import ZBaseFunc
import Zfinance
import ZfinanceCfg
from ZfinanceCfg import TableColor
import ZFavorEditor
import ZDataClean
from time import sleep
import pathlib
import time

import PySide2.QtWidgets ,PySide2.QtWidgets ,PySide2.QtGui
from PySide2.QtWidgets import QApplication, QMessageBox,QFileDialog,QCheckBox
from PySide2.QtWidgets import QButtonGroup,QSlider,QLabel,QRadioButton,QTableWidget,QHeaderView
from PySide2.QtUiTools  import QUiLoader
from PySide2.QtGui import QFont
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import datetime

import json
import os
import  threading
from threading import Thread



DownloadAbortFlag = True
Process = 0
ProcessLen = 100
TableInitFlag = False
GlobalMainUIx = 1
CfgDict = dict()
TableWidgetChannel = None
DownloadProcessBarChannel = None
VPN = None

TempColorYellow = 1
TempColorRed = 2
TempColorGreen = 3
TempColorGray = 4

ScrollBarPosition = 0

GlobalAPP = None
GlobalProcessCnt = 0
class DownloadUIProc:
    def __init__(self,GlobalUI,APP,GlobalFavorEditorUI):
        global GlobalMainUI,CfgDict,TableWidgetChannel,DownloadProcessBarChannel,GlobalDLUI,GlobalAPP
        self.GlobalMainUI = GlobalUI
        GlobalAPP = APP
        GlobalMainUI = GlobalUI
        self.DownloadCfgUI = QUiLoader().load('UIDesign/DownloadConfig.ui')


        self.DataCleanUIx = ZDataClean.DataCleanUIProc(GlobalAPP)
        GlobalDLUI = self.DownloadCfgUI
        ###################发射定义##############################
        TableWidgetChannel = SignalThreadChannel()
        DownloadProcessBarChannel  = SignalThreadChannel()

        TableWidgetChannel.TableSignal.connect(UpdateTableWidget)
        DownloadProcessBarChannel.PBarSignal.connect(UpdateDownloadProcessBarWidget)

        #######################################################
        GlobalMainUI.SymbolsDownloadProgressBar.setValue(0)

        self.DownloadCfgUI.SymbolsListProgressBar.setValue(0)

        self.GlobalMainUI.SymbolsDownloadConfig.clicked.connect(self.HandleDownloadConfig)
        self.DownloadCfgUI.CancelDownload.clicked.connect(self.CloseDownloadCfgUI)
        self.DownloadCfgUI.ConfirmDownload.clicked.connect(self.HandleConfirmDownload)
        self.DownloadCfgUI.OpenDLConfig.clicked.connect(self.HandleOpenDLConfig)
        self.DownloadCfgUI.SaveDLConfig.clicked.connect(self.HandleSaveDLConfig)
        self.DownloadCfgUI.EditFavorList.clicked.connect(GlobalFavorEditorUI.handleFavorEditor)

        self.DownloadCfgUI.DataClean.clicked.connect(self.handleDataCleanUI)
        self.DownloadCfgUI.DataClean.clicked.connect(self.DataCleanUIx.handleDataCleanUI)

        self.GlobalMainUI.SymbolsDownloadStart.clicked.connect(HandleDownloadStart)
        self.GlobalMainUI.SymbolsDownloadAbort.clicked.connect(HandleDownloadAbort)



        self.DownloadCfgUI.UpdateTickerList.clicked.connect(self.HandleUpdateTickerList)

        self.DownloadCfgUI.DownloadPeriod.sliderMoved.connect(self.HandleDownloadPeriod)
        self.DownloadCfgUI.DownloadPeriod.valueChanged.connect(self.HandleDownloadPeriod)

        self.DownloadCfgUI.FavorList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.DownloadCfgUI.FavorList.customContextMenuRequested[QPoint].connect(self.FavorListChechboxSelectMenu)

        self.DLUIInit = False

        # ConfigFilePathName = os.getcwd()+'\\Data\\00_Config\\Default.ZFCfg'
        # try:
        #     with open(ConfigFilePathName,'r') as load_f:
        #         CfgDict = json.load(load_f)
        #     ZBaseFunc.Log2LogBox('Load Default Download Config success!!')
        # except:
        #     ZBaseFunc.Log2LogBox('Load Default Download Config Fail!!')
        #     pass

    def FavorListChechboxSelectMenu(self):
        popMenu = QMenu()
        if self.DownloadCfgUI.FavorList.currentItem().parent() == None:
            SelectAll  = popMenu.addAction('全选')
            CancelAll  = popMenu.addAction("取消全选")

            CancelAll.triggered.connect(self.CancelAllChildrenInFavorList)
            SelectAll.triggered.connect(self.SelectAllChildrenInFavorList)
        popMenu.exec_(QCursor.pos())
        return

    def CancelAllChildrenInFavorList(self):
        self.DownloadCfgUI.FavorList.currentItem().setCheckState(0,PySide2.QtCore.Qt.CheckState.Unchecked)
        cursor = QTreeWidgetItemIterator(self.DownloadCfgUI.FavorList.currentItem())
        ChildCnt = cursor.value().childCount()
        cursor = cursor.__iadd__(1)

        for i in range(ChildCnt):
            cursor.value().setCheckState(0,PySide2.QtCore.Qt.CheckState.Unchecked)
            cursor = cursor.__iadd__(1)
    def SelectAllChildrenInFavorList(self):
        self.DownloadCfgUI.FavorList.currentItem().setCheckState(0,PySide2.QtCore.Qt.CheckState.Checked)
        cursor = QTreeWidgetItemIterator(self.DownloadCfgUI.FavorList.currentItem())
        ChildCnt = cursor.value().childCount()
        cursor = cursor.__iadd__(1)

        for i in range(ChildCnt):
            cursor.value().setCheckState(0,PySide2.QtCore.Qt.CheckState.Checked)
            cursor = cursor.__iadd__(1)

    def handleDataCleanUI(self):
        print('xx')

    def HandleUpdateTickerList(self):

        global GlobalAPP
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(0)
        US = efinance.stock.get_realtime_quotes("美股")
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(30)
        HK = efinance.stock.get_realtime_quotes("港股")
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(60)
        CN = efinance.stock.get_realtime_quotes("沪深A股")
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(90)

        US = US[~US['总市值'].isin(["-"])]
        HK = HK[~HK['总市值'].isin(["-"])]
        CN = CN[~CN['总市值'].isin(["-"])]

        US.to_csv("Data/00_Config/USTickerList.csv")
        HK.to_csv("Data/00_Config/HKTickerList.csv")
        CN.to_csv("Data/00_Config/CNTickerList.csv")
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(100)

        #
        #
        # self.DownloadCfgUI.SymbolsListProgressBar.setValue(0)
        # self.DownloadCfgUI.UpdateTickerList.setDisabled(True)
        # GlobalAPP.processEvents()
        # ftp = FTP()
        # self.DownloadCfgUI.SymbolsListProgressBar.setValue(10)
        # ftp.connect(host='ftp.nasdaqtrader.com', port=21, timeout=10)
        # self.DownloadCfgUI.SymbolsListProgressBar.setValue(20)
        # ftp.login(user=None, passwd=None)
        # self.DownloadCfgUI.SymbolsListProgressBar.setValue(40)
        # fNasdaq = open('Data/00_Config/NasdaqTickerList.csv', 'wb')
        # fNYSEAMEX = open('Data/00_Config/NyseAmexTickerList.csv', 'wb')
        # self.DownloadCfgUI.SymbolsListProgressBar.setValue(50)
        # ftp.cwd('/Symboldirectory/')
        # self.DownloadCfgUI.SymbolsListProgressBar.setValue(60)
        # ftp.retrbinary('RETR nasdaqlisted.txt', fNasdaq.write)
        # self.DownloadCfgUI.SymbolsListProgressBar.setValue(70)
        # ftp.retrbinary('RETR otherlisted.txt', fNYSEAMEX.write)
        # self.DownloadCfgUI.SymbolsListProgressBar.setValue(80)
        # fNasdaq.close()
        # self.DownloadCfgUI.SymbolsListProgressBar.setValue(90)
        # fNYSEAMEX.close()
        # self.DownloadCfgUI.SymbolsListProgressBar.setValue(100)
        # self.DownloadCfgUI.UpdateTickerList.setDisabled(False)

    def HandleDownloadPeriod(self):
        DownloadPeriod_x = self.PeriodDictList[self.DownloadCfgUI.DownloadPeriod.value()]
        self.DownloadCfgUI.ShowPeriod.setText(self.PeriodDictList[self.DownloadCfgUI.DownloadPeriod.value()])
      #  QLabel.setText()

    def LoadSelectMarket(self,SelectList):
        SelectList.setColumnCount(2)
        SelectList.setHeaderLabels(('Market', 'Comment', 'Rule'))

        for Key, Value in ZfinanceCfg.ExchargeMarket.items():
            root = QTreeWidgetItem(SelectList)
            root.setText(0, Key)
            root.setText(1, Value[0])
            root.setText(2, Value[1])
            root.setCheckState(0, Qt.Unchecked)
        SelectList.addTopLevelItem(root)
        SelectList.setCurrentItem((SelectList.topLevelItem(0)))

    def HandleDownloadConfig(self):
        ZFavorEditor.LoadFavorListCfg(self.DownloadCfgUI.FavorList, CheckBox=True)

        self.DownloadCfgUI.show()
        self.PeriodDictList =[]
        for key,value in ZfinanceCfg.Period2DayLenthDict.items():
            self.PeriodDictList.append(key)

        self.DownloadCfgUI.DownloadPeriod.setMaximum(len(self.PeriodDictList)-1)
        self.DownloadCfgUI.DownloadPeriod.setMinimum(0)
        self.DownloadCfgUI.DownloadPeriod.setTickInterval(1)
        self.DownloadCfgUI.ShowPeriod.setText(self.PeriodDictList[self.DownloadCfgUI.DownloadPeriod.value()])
        if(not self.DLUIInit):
            self.DownloadCfgUI.MulitThreadDL.addItems(ZfinanceCfg.MulitThreadList_c)
            self.DownloadCfgUI.SkipPeriod.addItems(ZfinanceCfg.SkipPeriodList_c)
            self.DownloadCfgUI.ReConnect.addItems(ZfinanceCfg.ReConnectList_c)
            self.DownloadCfgUI.TimeOut.addItems(ZfinanceCfg.TimeOutList_c)
            self.DownloadCfgUI.DownloadAPI.addItems(ZfinanceCfg.DownloadAPIList_c)

            self.HandleOpenDLConfig(Default=True)
            self.DLUIInit = True




    def HandleConfirmDownload(self):

        cursor = QTreeWidgetItemIterator(self.DownloadCfgUI.MarketSelector)     ##########刷新选择菜单
        while cursor.value():
            Temp = cursor.value()
            if Temp.checkState(0):
                CfgDict['EX_'+Temp.text(0)+'_x'] = True
            else:
                CfgDict['EX_' + Temp.text(0) + '_x'] = False
            cursor = cursor.__iadd__(1)
        CfgDict['List_Favor_x']  = CfgDict['EX_FAVOR_x']

        CfgDict['Intervial_1Day_x']     = self.DownloadCfgUI.Intervial_1Day.isChecked()
        CfgDict['Intervial_1h_x']       = self.DownloadCfgUI.Intervial_1h.isChecked()
        CfgDict['Intervial_30min_x']    = self.DownloadCfgUI.Intervial_30min.isChecked()
        CfgDict['Intervial_15min_x']    = self.DownloadCfgUI.Intervial_15min.isChecked()
        CfgDict['Intervial_5min_x']     = self.DownloadCfgUI.Intervial_5min.isChecked()
        CfgDict['Intervial_1min_x']     = self.DownloadCfgUI.Intervial_1min.isChecked()

        # Info Financials Balancesheet Cashflow Dividends Splits
        CfgDict['FunAna_Info_x']  = self.DownloadCfgUI.FunAna_Info.isChecked()
        CfgDict['FunAna_Financials_x']  = self.DownloadCfgUI.FunAna_Financials.isChecked()
        CfgDict['FunAna_Balancesheet_x']  = self.DownloadCfgUI.FunAna_Balancesheet.isChecked()
        CfgDict['FunAna_Cashflow_x']  = self.DownloadCfgUI.FunAna_Cashflow.isChecked()
        CfgDict['FunAna_Dividends_x']  = self.DownloadCfgUI.FunAna_Dividends.isChecked()
        CfgDict['FunAna_Splits_x']  = self.DownloadCfgUI.FunAna_Splits.isChecked()


        CfgDict['DownloadPeriod_x'] = self.PeriodDictList[self.DownloadCfgUI.DownloadPeriod.value()]

        CfgDict['MulitThreadDL_x']  = int(self.DownloadCfgUI.MulitThreadDL.currentText())
        CfgDict['ReConnectCnt_x']   = int(self.DownloadCfgUI.ReConnect.currentText())
        CfgDict['TimeOut_x']        = int(self.DownloadCfgUI.TimeOut.currentText())

        CfgDict['DownloadAPI_x'] =  self.DownloadCfgUI.DownloadAPI.currentText()
        CfgDict['ProxyEnable_x']      = self.DownloadCfgUI.ProxyEnable.isChecked()
        CfgDict['ProxyIP_x']        = self.DownloadCfgUI.ProxyIP.text()
        CfgDict['ProxyPort_x']      = self.DownloadCfgUI.ProxyPort.text()

        CfgDict['SkipNG_x']      = self.DownloadCfgUI.SkipNG.isChecked()
        CfgDict['SkipPeriod_x']  = int(self.DownloadCfgUI.SkipPeriod.currentText())

        self.DownloadCfgUI.close()

    def HandleSaveDLConfig(self):


        cursor = QTreeWidgetItemIterator(self.DownloadCfgUI.MarketSelector)
        while cursor.value():
            Temp = cursor.value()
            if Temp.checkState(0):
                CfgDict['EX_'+Temp.text(0)+'_x'] = True
            else:
                CfgDict['EX_' + Temp.text(0) + '_x'] = False
            cursor = cursor.__iadd__(1)

        CfgDict['List_Favor_x']  = CfgDict['EX_FAVOR_x']

        CfgDict['Intervial_1Day_x']  = self.DownloadCfgUI.Intervial_1Day.isChecked()
        CfgDict['Intervial_1h_x']  = self.DownloadCfgUI.Intervial_1h.isChecked()
        CfgDict['Intervial_30min_x']  = self.DownloadCfgUI.Intervial_30min.isChecked()
        CfgDict['Intervial_15min_x']  = self.DownloadCfgUI.Intervial_15min.isChecked()
        CfgDict['Intervial_5min_x']  = self.DownloadCfgUI.Intervial_5min.isChecked()
        CfgDict['Intervial_1min_x']  = self.DownloadCfgUI.Intervial_1min.isChecked()

        CfgDict['FunAna_Info_x']  = self.DownloadCfgUI.FunAna_Info.isChecked()
        CfgDict['FunAna_Financials_x']  = self.DownloadCfgUI.FunAna_Financials.isChecked()
        CfgDict['FunAna_Balancesheet_x']  = self.DownloadCfgUI.FunAna_Balancesheet.isChecked()
        CfgDict['FunAna_Cashflow_x']  = self.DownloadCfgUI.FunAna_Cashflow.isChecked()
        CfgDict['FunAna_Dividends_x']  = self.DownloadCfgUI.FunAna_Dividends.isChecked()
        CfgDict['FunAna_Splits_x']  = self.DownloadCfgUI.FunAna_Splits.isChecked()

        CfgDict['DownloadPeriod_x'] = self.PeriodDictList[self.DownloadCfgUI.DownloadPeriod.value()]

        CfgDict['MulitThreadDL_x']  = int(self.DownloadCfgUI.MulitThreadDL.currentText())
        CfgDict['ReConnectCnt_x']   = int(self.DownloadCfgUI.ReConnect.currentText())
        CfgDict['TimeOut_x']        = int(self.DownloadCfgUI.TimeOut.currentText())

        CfgDict['DownloadAPI_x']    = self.DownloadCfgUI.DownloadAPI.currentText()
        CfgDict['ProxyEnable_x']      = self.DownloadCfgUI.ProxyEnable.isChecked()
        CfgDict['ProxyIP_x']        = self.DownloadCfgUI.ProxyIP.text()
        CfgDict['ProxyPort_x']      = self.DownloadCfgUI.ProxyPort.text()

        CfgDict['SkipPeriod_x']  = int(self.DownloadCfgUI.SkipPeriod.currentText())
        CfgDict['SkipNG_x']      = self.DownloadCfgUI.SkipNG.isChecked()

        ConfigFilePathName ,ok = QFileDialog.getSaveFileName(None, "配置文件保存",'Data/00_Config','ZfinanceDownloadCfg (*.ZFdl)')

        if ConfigFilePathName == "":
            return

        with open(ConfigFilePathName, "w") as f:
            json.dump(CfgDict, f,indent=1)
        return

    def HandleOpenDLConfig(self,Default = False):
        if Default:
            ConfigFilePathName = 'Data/00_Config/DefaultDownload.ZFdl'
            if(not os.path.exists(ConfigFilePathName)):

                self.DownloadCfgUI.MarketSelector.setColumnCount(2)
                self.DownloadCfgUI.MarketSelector.setHeaderLabels(('Market', 'Comment', 'Rule'))

                for Key, Value in ZfinanceCfg.ExchargeMarket.items():
                    root = QTreeWidgetItem(self.DownloadCfgUI.MarketSelector)
                    root.setText(0, Key)
                    root.setText(1, Value[0])
                    root.setText(2, Value[1])
                    root.setCheckState(0, Qt.Unchecked)
                self.DownloadCfgUI.MarketSelector.addTopLevelItem(root)
                self.DownloadCfgUI.MarketSelector.setCurrentItem((self.DownloadCfgUI.MarketSelector.topLevelItem(0)))

                return
        else:
            ConfigFilePathName ,ok= QFileDialog.getOpenFileName(None, "选择配置文件",'Data/00_Config','ZfinanceDownloadCfg (*.ZFdl)')
            if ConfigFilePathName == "":
                return

        with open(ConfigFilePathName, 'r') as load_f:
            CfgDict = json.load(load_f)
        try:

            self.DownloadCfgUI.Intervial_1Day.setChecked(CfgDict['Intervial_1Day_x'])
            self.DownloadCfgUI.Intervial_1h.setChecked(CfgDict['Intervial_1h_x'])
            self.DownloadCfgUI.Intervial_30min.setChecked(CfgDict['Intervial_30min_x'])
            self.DownloadCfgUI.Intervial_15min.setChecked(CfgDict['Intervial_15min_x'] )
            self.DownloadCfgUI.Intervial_5min.setChecked(CfgDict['Intervial_5min_x'])
            self.DownloadCfgUI.Intervial_1min.setChecked(CfgDict['Intervial_1min_x'])

            self.DownloadCfgUI.FunAna_Info.setChecked(CfgDict['FunAna_Info_x'])
            self.DownloadCfgUI.FunAna_Financials.setChecked(CfgDict['FunAna_Financials_x'])
            self.DownloadCfgUI.FunAna_Balancesheet.setChecked(CfgDict['FunAna_Balancesheet_x'])
            self.DownloadCfgUI.FunAna_Cashflow.setChecked(CfgDict['FunAna_Cashflow_x'])
            self.DownloadCfgUI.FunAna_Dividends.setChecked(CfgDict['FunAna_Dividends_x'])
            self.DownloadCfgUI.FunAna_Splits.setChecked(CfgDict['FunAna_Splits_x'])

            self.DownloadCfgUI.DownloadPeriod.setValue(self.PeriodDictList.index(CfgDict['DownloadPeriod_x']))

            self.DownloadCfgUI.MulitThreadDL.setCurrentIndex(ZfinanceCfg.MulitThreadList_c.index(str(CfgDict['MulitThreadDL_x'])))
            self.DownloadCfgUI.ReConnect.setCurrentIndex(ZfinanceCfg.ReConnectList_c.index(str(CfgDict['ReConnectCnt_x'])))
            self.DownloadCfgUI.TimeOut.setCurrentIndex(ZfinanceCfg.TimeOutList_c.index(str(CfgDict['TimeOut_x'])))

            self.DownloadCfgUI.DownloadAPI.setCurrentIndex(ZfinanceCfg.DownloadAPIList_c.index(str(CfgDict['DownloadAPI_x'])))

            self.DownloadCfgUI.ProxyEnable.setChecked(CfgDict['ProxyEnable_x'])
            self.DownloadCfgUI.ProxyIP.setText(CfgDict['ProxyIP_x'])
            self.DownloadCfgUI.ProxyPort.setText(CfgDict['ProxyPort_x'])

            self.DownloadCfgUI.SkipPeriod.setCurrentIndex(ZfinanceCfg.SkipPeriodList_c.index(str(CfgDict['SkipPeriod_x'])))
            self.DownloadCfgUI.SkipNG.setChecked(CfgDict['SkipNG_x'])


            self.DownloadCfgUI.MarketSelector.setColumnCount(2)
            self.DownloadCfgUI.MarketSelector.setHeaderLabels(('Market', 'Comment', 'Rule'))

            for Key, Value in ZfinanceCfg.ExchargeMarket.items():
                root = QTreeWidgetItem(self.DownloadCfgUI.MarketSelector)
                root.setText(0, Key)
                root.setText(1, Value[0])
                root.setText(2, Value[1])
                if CfgDict['EX_'+Key+'_x']:
                    root.setCheckState(0, Qt.Checked)
                else:
                    root.setCheckState(0, Qt.Unchecked)
            self.DownloadCfgUI.MarketSelector.addTopLevelItem(root)
            self.DownloadCfgUI.MarketSelector.setCurrentItem((self.DownloadCfgUI.MarketSelector.topLevelItem(0)))


        except:
            pass
        print(ConfigFilePathName)

        DataBasePath = os.getcwd() + '\\Data\\01_TickerDatabase'
        if (not os.path.exists(DataBasePath)):
            os.mkdir(DataBasePath)
        return

    def CloseDownloadCfgUI(self):
        self.DownloadCfgUI.close()





def HandleDownloadAbort():
    global DownloadAbortFlag,TableWidgetChannel,GlobalMainUI,GlobalAPP
    DownloadAbortFlag = True
    GlobalMainUI.SymbolsDownloadAbort.setDisabled(True)
    GlobalAPP.processEvents()


def HandleDownloadStart():
    global DownloadAbortFlag,GlobalDLUI,GlobalProcessCnt
    global Process,ProcessLen, GlobalMainUI,TableInitFlag,CfgDict,VPN,ScrollBarPosition
    DownloadAbortFlag = False
    Process = 0
    PeriodLimitlList = []
    KlineIntervialAndPeriodDictList = []
    BaseInfoList = []
    GlobalMainUI.SymbolsDownloadStart.setDisabled(True)
    GlobalAPP.processEvents()

    if  CfgDict == dict():
        ConfigFilePathName = 'Data/00_Config/DefaultDownload.ZFdl'
        with open(ConfigFilePathName, 'r') as load_f:
            CfgDict = json.load(load_f)

    DownloadPeriod = CfgDict['DownloadPeriod_x']
    DayLenth = ZfinanceCfg.Period2DayLenthDict[DownloadPeriod]
    if CfgDict['Intervial_1Day_x']:
        KlineIntervialAndPeriodDictList.append({'Interval': '1d','Period' : DayLenth} )
    if CfgDict['Intervial_1h_x']:
        KlineIntervialAndPeriodDictList.append({'Interval': '60m','Period': DayLenth})
    if CfgDict['Intervial_30min_x']:
        KlineIntervialAndPeriodDictList.append({'Interval': '30m','Period': DayLenth})
    if CfgDict['Intervial_15min_x']:
        KlineIntervialAndPeriodDictList.append({'Interval': '15m','Period': DayLenth})
    if CfgDict['Intervial_5min_x']:
        KlineIntervialAndPeriodDictList.append({'Interval': '5m','Period': DayLenth})
    if CfgDict['Intervial_1min_x']:
        KlineIntervialAndPeriodDictList.append({'Interval': '1m','Period': DayLenth})


#    Info Financials Balancesheet Cashflow Dividends Splits
    if CfgDict['FunAna_Info_x']:
        BaseInfoList.append('inf')
    if CfgDict['FunAna_Financials_x'] == True:
        BaseInfoList.append('fin')
    if CfgDict['FunAna_Balancesheet_x']:
        BaseInfoList.append('bal')
    if CfgDict['FunAna_Cashflow_x']:
        BaseInfoList.append('cas')
    if CfgDict['FunAna_Dividends_x']:
        BaseInfoList.append('div')
    if CfgDict['FunAna_Splits_x']:
        BaseInfoList.append('spl')

    ReConnectCnt = CfgDict['ReConnectCnt_x']

    if CfgDict['ProxyEnable_x']:
        VPN = 'http://'+CfgDict['ProxyIP_x']+':'+CfgDict['ProxyPort_x']
        ZBaseFunc.SetDLAPIPara(key='PROXY',value=VPN)
    else:
        VPN = None
        ZBaseFunc.SetDLAPIPara(key='PROXY', value=None)

    SymbolsList = []
    CNTickerList = pd.read_csv('Data\\00_Config\\CNTickerList.csv', sep=',',dtype={'股票代码':str})#http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs
    HKTickerList = pd.read_csv('Data\\00_Config\\HKTickerList.csv', sep=',',dtype={'股票代码':str})
    USTickerList = pd.read_csv('Data\\00_Config\\USTickerList.csv', sep=',',dtype={'股票代码':str})

    if CfgDict['EX_CN-SHH_x']:
        Temp = CNTickerList.loc[CNTickerList['市场类型'].isin(['沪A'])]
        SymbolsList.extend([str(i)+ '.ss' for i in Temp['股票代码'].tolist() ])

    if CfgDict['EX_CN-SHZ_x']:
        Temp = CNTickerList.loc[CNTickerList['市场类型'].isin(['深A'])]
        SymbolsList.extend([str(i)+'.sz' for i in Temp['股票代码'].tolist() ])

    if CfgDict['EX_HK_x']:
        Temp = HKTickerList['股票代码'].tolist()
        for i in Temp:
            if int(i)<10000:
                SymbolsList.append(i[-4:]+'.hk')

    if CfgDict['EX_US-ASE_x']:
        Temp = USTickerList['行情ID'].tolist()
        for i in Temp:
            sym = i.split('.')
            if int(sym[0]) == 105:
                SymbolsList.append(sym[1])

    if CfgDict['EX_US-NYQ_x']:
        Temp = USTickerList['行情ID'].tolist()
        for i in Temp:
            sym = i.split('.')
            if int(sym[0]) == 106:
                SymbolsList.append(sym[1])

    if CfgDict['EX_US-NMS_x']:
        Temp = USTickerList['行情ID'].tolist()
        for i in Temp:
            sym = i.split('.')
            if int(sym[0]) == 107:
                SymbolsList.append(sym[1])
#############
    if CfgDict['List_Favor_x']:
        cursor = QTreeWidgetItemIterator(GlobalDLUI.FavorList)
        RemoveList = []

        while cursor.value():
            Temp = cursor.value()
            ChildCnt = Temp.childCount()
            if(ChildCnt == 0):
                if(Temp.checkState(0)):
                    SymbolsList.append(Temp.text(0))
                    print('add-' + Temp.text(0))
            elif Temp.text(0) =='BLACKLIST':
                for i in range(ChildCnt):
                    cursor = cursor.__iadd__(1)
                    Temp = cursor.value()
                    RemoveList.append(Temp.text(0))
            cursor = cursor.__iadd__(1)
############################去重复
        temp_list = []
        for one in SymbolsList:
            if one not in temp_list:
                temp_list.append(one)
        SymbolsList = temp_list
############################
        for i in RemoveList:
            try:
                print("Remove:"+i)
                SymbolsList.remove(i)
            except:
                pass
############################
    ProcessLen = len(SymbolsList)
    ZBaseFunc.Log2LogBox('SymbolsList count ='+str(ProcessLen))
    GlobalMainUI.SymbolsDownloadProgressBar.setValue(0)
    #QTableWidget.setRowHeight()horizontalHeader().setSectionResizeMode(QHeaderView.Fixed);

    ScrollBarPosition = 0
    if False:#TableInitFlag:
        GlobalMainUI.SymbolsDownloadTable.clear()
        GlobalMainUI.SymbolsDownloadTable.verticalScrollBar().setValue(0)
        pass
    else:
        TableInitFlag = True
        GlobalMainUI.SymbolsDownloadTable.clear()
        GlobalMainUI.SymbolsDownloadTable.setRowCount(0)
        GlobalMainUI.SymbolsDownloadTable.setColumnCount(len(KlineIntervialAndPeriodDictList)+len(BaseInfoList)+1)
        GlobalMainUI.SymbolsDownloadTable.setRowCount(ProcessLen)
        GlobalMainUI.SymbolsDownloadTable.verticalHeader().setVisible(False)
        #GlobalMainUI.SymbolsDownloadTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        GlobalMainUI.SymbolsDownloadTable.horizontalHeader().setDefaultAlignment(PySide2.QtCore.Qt.AlignLeft)
        GlobalMainUI.SymbolsDownloadTable.setFont(QFont('song', 7))
        GlobalMainUI.SymbolsDownloadTable.horizontalHeader().setFont(QFont('song', 7))
        GlobalMainUI.SymbolsDownloadTable.verticalScrollBar().setValue(0)
        Row = 0
        for i in SymbolsList:
            SymbolsInTable = PySide2.QtWidgets.QTableWidgetItem(i)
            GlobalMainUI.SymbolsDownloadTable.setRowHeight(Row, 6)
            GlobalMainUI.SymbolsDownloadTable.setItem(Row, 0, SymbolsInTable)
            Row = Row+1

        GlobalMainUI.SymbolsDownloadTable.setColumnWidth(0, 55)

        Col = 1
        for i in range(len(KlineIntervialAndPeriodDictList)+len(BaseInfoList)):
            GlobalMainUI.SymbolsDownloadTable.setColumnWidth(Col,25)
            Col = Col+1
        Temp = ['SYM']
        for i in KlineIntervialAndPeriodDictList:
            Temp.append(i['Interval'])
        for i in BaseInfoList:
            Temp.append(i)
        GlobalMainUI.SymbolsDownloadTable.setHorizontalHeaderLabels(Temp)
    GlobalAPP.processEvents()
    ThreadNum =  CfgDict['MulitThreadDL_x']

    SYM = ZBaseFunc.StockSymbolData(Platfrom=CfgDict['DownloadAPI_x'],Symbol='AAPL')
    Result = SYM.DownloadSymbolHistoryData(Period=30,Interval='1d')
    if Result['Success']:
        NewFileEndTime = int(datetime.datetime.fromtimestamp(Result['TimeStamp']).strftime("%Y%m%d"))
    else:
        ZBaseFunc.Log2LogBox('Can not start Download,please check Network!')
        GlobalMainUI.SymbolsDownloadStart.setDisabled(False)
        return
    thread = Thread(target=ThreadingOfDownload,args=(ThreadNum,
                                                    SymbolsList,
                                                    CfgDict['DownloadAPI_x'],5,NewFileEndTime,
                                                    KlineIntervialAndPeriodDictList,
                                                    BaseInfoList,
                                                    CfgDict['ReConnectCnt_x'],
                                                    CfgDict['SkipPeriod_x'],
                                                    CfgDict['SkipNG_x'],
                                                    DownloadProcessBarChannel))

    thread.start()

def ThreadingOfDownload(ThreadNum,
                       SymbolsList,
                       Platfrom ,
                       Timeout,
                       NewFileEndTime ,
                       KlineIntervialAndPeriodDictList ,
                       BaseInfoList ,
                       ReConnectCnt ,
                       SkipLenth ,
                       SkipNG ,
                       PrgressSignal):
    global GlobalProcessCnt

    #ThreadNum = 1
    GlobalProcessCnt = 0
    Parallel(n_jobs=ThreadNum,backend='threading')(delayed(DownloadThread)(Symbol = Symbol,
                                                       Platfrom = Platfrom,
                                                       Timeout = Timeout,
                                                       NewFileEndTime = NewFileEndTime,
                                                       CurrRow = SymbolsList.index(Symbol),
                                                       KlineIntervialAndPeriodDictList = KlineIntervialAndPeriodDictList,
                                                       BaseInfoList = BaseInfoList,
                                                       ReConnectCnt = ReConnectCnt,
                                                       SkipLenth = SkipLenth,
                                                       SkipNG = SkipNG,
                                                       PrgressSignal = PrgressSignal) for Symbol in SymbolsList)

    GlobalMainUI.SymbolsDownloadStart.setDisabled(False)
    GlobalMainUI.SymbolsDownloadAbort.setDisabled(False)


def DeleteUselessOKNG(FolderPath):
    for i in glob.glob(FolderPath+'/TAG_*'):
        os.remove(i)

def DownloadThread(Symbol,
                   Platfrom,
                   Timeout,
                   NewFileEndTime=None,
                   CurrRow = 0,
                   KlineIntervialAndPeriodDictList=[],
                   BaseInfoList=[],
                   ReConnectCnt=1,
                   SkipLenth = 0,
                   SkipNG = True,
                   PrgressSignal = None):
    global GlobalMainUI, DownloadAbortFlag,ScrollBarPosition
    global TempColorGreen, TempColorYellow, TempColorRed

    if (CurrRow > ScrollBarPosition):
        ScrollBarPosition = CurrRow
        if ScrollBarPosition > 5:
            GlobalMainUI.SymbolsDownloadTable.verticalScrollBar().setValue(ScrollBarPosition - 4)



    TimeStamp = str(int(time.time()))
    RootDir = 'Data/01_TickerDatabase/'
    if DownloadAbortFlag:   #停止下载
        PrgressSignal.PBarSignal.emit(CurrRow + 1)
        return
    TempFolderPath = RootDir + Symbol
    if (not os.path.exists(TempFolderPath)):
        try:
            os.mkdir(TempFolderPath)
        except:
            ZBaseFunc.Log2LogBox('Creat Folder ['+TempFolderPath+'] Failed,Please check access Permission')
    OKFilePath = TempFolderPath + '/TAG_OK_' + TimeStamp
    NGFilePath = TempFolderPath + '/TAG_NG_' + TimeStamp
    TempCol = 0
    OKFLAG = True
    DeleteUselessOKNG(TempFolderPath)
    for KlineIntervialAndPeriod in KlineIntervialAndPeriodDictList:
        TempCol += 1
        TempIntervial   = KlineIntervialAndPeriod['Interval']
        TempPeriod      = KlineIntervialAndPeriod['Period']
        TableWidgetChannel.TableSignal.emit(CurrRow, TempCol, TempColorYellow)

        for ReConnectCnt_i in range(ReConnectCnt):

            if TempPeriod == 0:     #MAX
                NewFileStartTime = 19000101
            else:
                NewFileStartTime = int((datetime.datetime.now() - datetime.timedelta(days=TempPeriod)).strftime("%Y%m%d"))

            LastFileName = ZBaseFunc.GetCompleteFileName(Path=TempFolderPath + '/' + Symbol + "_" + TempIntervial)
            Tempdf_Exist = pd.DataFrame()
            if(LastFileName != None):                                                                                   #如果已经有文件存在
                ExistFileStartTime  = int(LastFileName.split('_')[2])
                ExistFileEndTime    = int(LastFileName.split('_')[3])
                if LastFileName.split('_')[4] == 'max.csv':
                    ExistFileStartTime = 190000000

                if SkipNG:
                    LastNGFile = ZBaseFunc.GetCompleteFileName(Path=TempFolderPath + '/TAG_NG_')
                    if LastNGFile != None:
                        ExistFileEndTime = int(datetime.datetime.fromtimestamp(int(LastNGFile.split('NG_')[1])).strftime("%Y%m%d"))

                NewExistEndTime = int((datetime.datetime.strptime(str(ExistFileEndTime), "%Y%m%d") + datetime.timedelta(SkipLenth)).strftime("%Y%m%d"))
                if (ExistFileStartTime<=NewFileStartTime) and (NewExistEndTime>=NewFileEndTime):                        #已有文件已经包含了要下载的数据段
                    TableWidgetChannel.TableSignal.emit(CurrRow, TempCol, TempColorGreen)                               #直接标绿色，退出
                    break
                Tempdf_Exist = pd.read_csv(TempFolderPath + '/' + LastFileName, sep=',', index_col='DateTime')
                TempPeriod = CalcReasonablePeriod(ExistFileStartTime,ExistFileEndTime,NewFileStartTime,NewFileEndTime,TempPeriod)
            SYMBOL = ZBaseFunc.StockSymbolData(Symbol=Symbol, Platfrom=Platfrom)

            HistorydfDict = SYMBOL.DownloadSymbolHistoryData(Period=TempPeriod,Interval=TempIntervial,timeout=Timeout)
            if HistorydfDict['Success']:

                Tempdf = Tempdf_Exist.append(HistorydfDict['DataFrame'])
                Tempdf = Tempdf[~Tempdf.index.duplicated(keep='last')]

                NewFileStartTimeStr = Tempdf.index[0][:10].replace('-','')
                NewFileEndTimeStr   = Tempdf.index[-1][:10].replace('-','')

                if TempPeriod == 0:                                                                                     ###给加_30d，或者_max后缀
                    TempPeriodStr = 'max'
                else:
                    TempPeriodStr = str(TempPeriod) + 'd'

                TempSYMFileName = TempFolderPath + '/' + Symbol + "_" + str(TempIntervial) + "_" + \
                                  NewFileStartTimeStr + '_' + NewFileEndTimeStr + '_'+TempPeriodStr+'.csv'
                try:
                    os.remove(TempFolderPath + '/' + LastFileName)
                except:
                    pass
                Tempdf.to_csv(TempSYMFileName, sep=',', index_label='DateTime')
                TableWidgetChannel.TableSignal.emit(CurrRow, TempCol, TempColorGreen)
                break
            else:
                TableWidgetChannel.TableSignal.emit(CurrRow, TempCol, TempColorRed)
                ZBaseFunc.Log2LogBox('Download Fail : <' + Symbol + "_" + TempIntervial+'> Failed')
                if ReConnectCnt_i == ReConnectCnt-1:
                    OKFLAG = False

    for BaseFinInfo in BaseInfoList:
        TempCol += 1
        TableWidgetChannel.TableSignal.emit(CurrRow, TempCol, TempColorYellow)
        if BaseFinInfo == 'inf':
            BaseInfoDataframe = SYMBOL.DownloadSymbolBaseInfoData()
        else:
            BaseInfoDataframe = SYMBOL.DownloadSymbolFinanceData(BaseFinInfo)
        if BaseInfoDataframe['Success']:
            BaseInfoDataframe['DataFrame'].to_csv(TempFolderPath + '/' + Symbol + '_' + BaseFinInfo + '.csv', sep=',',
                                                  index_label='symbol')
            TableWidgetChannel.TableSignal.emit(CurrRow, TempCol, TempColorGreen)
        else:
            TableWidgetChannel.TableSignal.emit(CurrRow, TempCol, TempColorRed)
            OKFLAG = False

    if OKFLAG:
        FlagPath = OKFilePath
    else:
        FlagPath = NGFilePath
    try:
        open(FlagPath,'w').close()
    except:
        pass

    PrgressSignal.PBarSignal.emit(CurrRow + 1)
    return

class SignalThreadChannel(QObject):
    TableSignal = Signal(int,int,int)
    PBarSignal = Signal(int)
    LPBarSignal = Signal(pd.DataFrame)

def CalcReasonablePeriod(ExistFileStartTime,ExistFileEndTime,NewFileStartTime,NewFileEndTime,TempPeriod):
    if NewFileStartTime < ExistFileStartTime:
        return TempPeriod
    else:
        TempPeriod = (datetime.datetime.strptime(str(NewFileEndTime), "%Y%m%d") - datetime.datetime.strptime(str(ExistFileEndTime), "%Y%m%d")).days
        for key,value in ZfinanceCfg.Period2DayLenthDict.items():
            if value >= TempPeriod:
                TempPeriod = value

                return TempPeriod

def UpdateListProcessBarWidget(df = pandas.DataFrame()):
    df.to_csv('Data/00_Config/TickerList.csv',sep=',')

def UpdateDownloadProcessBarWidget(Process):
    global  GlobalMainUI,ProcessLen,GlobalProcessCnt

    GlobalProcessCnt +=1
    GlobalMainUI.SymbolsDownloadProgressBar.setValue(GlobalProcessCnt / ProcessLen * 100)

def UpdateTableWidget(row,col,color):
    global GlobalMainUI,TempColorGreen,TempColorYellow,TempColorRed
    TempColor = PySide2.QtWidgets.QTableWidgetItem('')
    TempColor.setBackgroundColor(PySide2.QtGui.QColor(0, 0, 255))
    if color == TempColorGreen:
        TempColor.setBackgroundColor(PySide2.QtGui.QColor(0, 255, 0))
    if color == TempColorYellow:
       TempColor.setBackgroundColor(PySide2.QtGui.QColor(255, 255, 0))
    if color == TempColorRed:
        TempColor.setBackgroundColor(PySide2.QtGui.QColor(255, 0, 0))
    if color == TempColorGray:
        TempColor.setBackgroundColor(PySide2.QtGui.QColor(100, 100, 100))
    GlobalMainUI.SymbolsDownloadTable.setItem(row, col, TempColor)

###########################################################
