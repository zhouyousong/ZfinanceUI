

import datetime
from ftplib import FTP
import pandas
import pandas as pd
import yfinance

import Zfinance
import ZfinanceCfg
from ZfinanceCfg import TableColor
import ZFavorEditor
import time
from time import sleep

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



MulitThreadList_c = ['1','3','5','10','20','40','60','100']
ReConnectList_c = ['1','3','5','10','20']
TimeOutList_c = ['5','10','20','30','60']

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

GlobalAPP = None
class DownloadUIProc:
    def __init__(self,GlobalUI,APP,GlobalFavorEditorUI):
        global GlobalMainUI,CfgDict,TableWidgetChannel,DownloadProcessBarChannel,GlobalDLUI,GlobalAPP
        self.GlobalMainUI = GlobalUI
        GlobalAPP = APP
        GlobalMainUI = GlobalUI
        self.DownloadCfgUI = QUiLoader().load('UIDesign\DownloadConfig.ui')
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
        self.GlobalMainUI.SymbolsDownloadStart.clicked.connect(HandleDownloadStart)


        self.DownloadCfgUI.CancelDownload.clicked.connect(self.CloseDownloadCfgUI)
        self.DownloadCfgUI.ConfirmDownload.clicked.connect(self.HandleConfirmDownload)
        self.DownloadCfgUI.OpenDLConfig.clicked.connect(self.HandleOpenDLConfig)
        self.DownloadCfgUI.SaveDLConfig.clicked.connect(self.HandleSaveDLConfig)
        self.DownloadCfgUI.SaveDLConfig.clicked.connect(self.HandleSaveDLConfig)
        self.DownloadCfgUI.EditFavorList.clicked.connect(GlobalFavorEditorUI.handleFavorEditor)

        self.DownloadCfgUI.UpdateTickerList.clicked.connect(self.HandleUpdateTickerList)
        self.DownloadCfgUI.UpdateTickerList.clicked.connect(self.HandleUpdateTickerList)

        self.DownloadCfgUI.DownloadPeriod.sliderMoved.connect(self.HandleDownloadPeriod)
        self.DownloadCfgUI.DownloadPeriod.valueChanged.connect(self.HandleDownloadPeriod)

        self.DLUIInit = False

        ConfigFilePathName = os.getcwd()+'\\Data\\00_Config\\Default.ZFCfg'
        try:
            with open(ConfigFilePathName,'r') as load_f:
                CfgDict = json.load(load_f)
            self.GlobalMainUI.SymbolsDownloadLog.setText('Load Default Download Config success!!')
        except:
            self.GlobalMainUI.SymbolsDownloadLog.setText('Load Default Download Config Fail!!')
            pass

    def HandleUpdateTickerList(self):

        global GlobalAPP

        self.DownloadCfgUI.SymbolsListProgressBar.setValue(0)
        self.DownloadCfgUI.UpdateTickerList.setDisabled(True)
        GlobalAPP.processEvents()
        ftp = FTP()
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(10)
        ftp.connect(host='ftp.nasdaqtrader.com', port=21, timeout=10)
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(20)
        ftp.login(user=None, passwd=None)
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(40)
        fNasdaq = open('Data/00_Config/NasdaqTickerList.csv', 'wb')
        fNYSEAMEX = open('Data/00_Config/NyseAmexTickerList.csv', 'wb')
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(50)
        ftp.cwd('/Symboldirectory/')
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(60)
        ftp.retrbinary('RETR nasdaqlisted.txt', fNasdaq.write)
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(70)
        ftp.retrbinary('RETR otherlisted.txt', fNYSEAMEX.write)
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(80)
        fNasdaq.close()
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(90)
        fNYSEAMEX.close()
        self.DownloadCfgUI.SymbolsListProgressBar.setValue(100)
        self.DownloadCfgUI.UpdateTickerList.setDisabled(False)
######################################
        # self.DownloadCfgUI.SymbolsListProgressBar.setValue(0)
        #
        # thread = Thread(target=akshare.stock_us_spot,
        #                 args=(self.DownloadCfgUI,self.ListProcessBarChannel.LPBarSignal.emit)
        #                 )
        # thread.start()
######################################


    def HandleDownloadPeriod(self):
        DownloadPeriod_x = ZfinanceCfg.PeriodDict['PeriodStrPara'][self.DownloadCfgUI.DownloadPeriod.value()]
        self.DownloadCfgUI.ShowPeriod.setText(ZfinanceCfg.PeriodDict['PeriodStr'][self.DownloadCfgUI.DownloadPeriod.value()])
      #  QLabel.setText()
    def HandleDownloadConfig(self):
        #  info = self.ui.SymbolsDownloadLog.toPlainText()

        self.GlobalMainUI.SymbolsDownloadLog.setText('HandleDownloadConfig!!')
        self.DownloadCfgUI.show()

        self.DownloadCfgUI.DownloadPeriod.setMaximum(len(ZfinanceCfg.PeriodDict['PeriodStr'])-1)
        self.DownloadCfgUI.DownloadPeriod.setMinimum(0)
        self.DownloadCfgUI.DownloadPeriod.setTickInterval(1)
        if(not self.DLUIInit):
            self.DownloadCfgUI.MulitThreadDL.addItems(MulitThreadList_c)
            self.DownloadCfgUI.ReConnect.addItems(ReConnectList_c)
            self.DownloadCfgUI.TimeOut.addItems(TimeOutList_c)
            self.HandleOpenDLConfig(Default=True)
            self.DLUIInit = True

    def HandleConfirmDownload(self):

        CfgDict['EX_NASDAQGSM_x'] = self.DownloadCfgUI.NASDAQGSM.isChecked()
        CfgDict['EX_NASDAQGM_x']  = self.DownloadCfgUI.NASDAQGM.isChecked()
        CfgDict['EX_NASDAQCM_x']  = self.DownloadCfgUI.NASDAQCM.isChecked()

        CfgDict['EX_NYSEMKT_x'] = self.DownloadCfgUI.NYSEMKT.isChecked()
        CfgDict['EX_NYSE_x']  = self.DownloadCfgUI.NYSE.isChecked()
        CfgDict['EX_NYSEARCA_x']  = self.DownloadCfgUI.NYSEARCA.isChecked()
        CfgDict['EX_BATS_x'] = self.DownloadCfgUI.BATS.isChecked()
        CfgDict['EX_IEXG_x']  = self.DownloadCfgUI.IEXG.isChecked()

        CfgDict['List_Favor_x']  = self.DownloadCfgUI.List_Favor.isChecked()

        CfgDict['Intervial_1Day_x']  = self.DownloadCfgUI.Intervial_1Day.isChecked()
        CfgDict['Intervial_1h_x']  = self.DownloadCfgUI.Intervial_1h.isChecked()
        CfgDict['Intervial_30min_x']  = self.DownloadCfgUI.Intervial_30min.isChecked()
        CfgDict['Intervial_15min_x']  = self.DownloadCfgUI.Intervial_15min.isChecked()
        CfgDict['Intervial_5min_x']  = self.DownloadCfgUI.Intervial_5min.isChecked()
        CfgDict['Intervial_1min_x']  = self.DownloadCfgUI.Intervial_1min.isChecked()
        CfgDict['Intervial_Current_x']  = self.DownloadCfgUI.Intervial_Current.isChecked()

        CfgDict['DownloadIR_x']    = self.DownloadCfgUI.DownloadIR.checkedId()

        CfgDict['DownloadPeriod_x'] = ZfinanceCfg.PeriodDict['PeriodStrPara'][self.DownloadCfgUI.DownloadPeriod.value()]

        CfgDict['MulitThreadDL_x']  = int(self.DownloadCfgUI.MulitThreadDL.currentText())
        CfgDict['ReConnectCnt_x']   = int(self.DownloadCfgUI.ReConnect.currentText())
        CfgDict['TimeOut_x']        = int(self.DownloadCfgUI.TimeOut.currentText())
        CfgDict['VPNEnable_x']      = self.DownloadCfgUI.VPNEnable.isChecked()


        self.DownloadCfgUI.close()
        self.GlobalMainUI.SymbolsDownloadLog.setText('HandleConfirmDownload!!')

    def HandleSaveDLConfig(self):

        CfgDict['EX_NASDAQGSM_x'] = self.DownloadCfgUI.NASDAQGSM.isChecked()
        CfgDict['EX_NASDAQGM_x']  = self.DownloadCfgUI.NASDAQGM.isChecked()
        CfgDict['EX_NASDAQCM_x']  = self.DownloadCfgUI.NASDAQCM.isChecked()

        CfgDict['EX_NYSEMKT_x'] = self.DownloadCfgUI.NYSEMKT.isChecked()
        CfgDict['EX_NYSE_x']  = self.DownloadCfgUI.NYSE.isChecked()
        CfgDict['EX_NYSEARCA_x']  = self.DownloadCfgUI.NYSEARCA.isChecked()
        CfgDict['EX_BATS_x'] = self.DownloadCfgUI.BATS.isChecked()
        CfgDict['EX_IEXG_x']  = self.DownloadCfgUI.IEXG.isChecked()

        CfgDict['List_Favor_x']  = self.DownloadCfgUI.List_Favor.isChecked()

        CfgDict['Intervial_1Day_x']  = self.DownloadCfgUI.Intervial_1Day.isChecked()
        CfgDict['Intervial_1h_x']  = self.DownloadCfgUI.Intervial_1h.isChecked()
        CfgDict['Intervial_30min_x']  = self.DownloadCfgUI.Intervial_30min.isChecked()
        CfgDict['Intervial_15min_x']  = self.DownloadCfgUI.Intervial_15min.isChecked()
        CfgDict['Intervial_5min_x']  = self.DownloadCfgUI.Intervial_5min.isChecked()
        CfgDict['Intervial_1min_x']  = self.DownloadCfgUI.Intervial_1min.isChecked()
        CfgDict['Intervial_Current_x'] = self.DownloadCfgUI.Intervial_Current.isChecked()



        CfgDict['DownloadPeriod_x'] = ZfinanceCfg.PeriodDict['PeriodStrPara'][self.DownloadCfgUI.DownloadPeriod.value()]

        CfgDict['MulitThreadDL_x']  = int(self.DownloadCfgUI.MulitThreadDL.currentText())
        CfgDict['ReConnectCnt_x']   = int(self.DownloadCfgUI.ReConnect.currentText())
        CfgDict['TimeOut_x']        = int(self.DownloadCfgUI.TimeOut.currentText())

        CfgDict['DownloadIR_x']    = self.DownloadCfgUI.DownloadIR.checkedId()

        CfgDict['VPNEnable_x']      = self.DownloadCfgUI.VPNEnable.isChecked()


        ConfigFilePathName ,ok = QFileDialog.getSaveFileName(None, "配置文件保存",'Data/00_Config','ZfinanceCfg (*.ZFCfg)')

        if ConfigFilePathName == "":
            self.GlobalMainUI.SymbolsDownloadLog.setText('Cancel Save ZFCfg!!' )
            return

        with open(ConfigFilePathName, "w") as f:
            json.dump(CfgDict, f)

        self.GlobalMainUI.SymbolsDownloadLog.setText('HandleSaveDLConfig!!'+ConfigFilePathName[0])
        return

    def HandleOpenDLConfig(self,Default = False):
        if Default:
            ConfigFilePathName = 'Data/00_Config/Default.ZFCfg'
            if(not os.path.exists(ConfigFilePathName)):
                return
        else:
            ConfigFilePathName ,ok= QFileDialog.getOpenFileName(None, "选择配置文件",'Data/00_Config','ZfinanceCfg (*.ZFCfg)')
            if ConfigFilePathName == "":
                self.GlobalMainUI.SymbolsDownloadLog.setText('Cancel Save ZFCfg!!' )
                return

        with open(ConfigFilePathName, 'r') as load_f:
            CfgDict = json.load(load_f)
        try:
            self.DownloadCfgUI.NASDAQGSM.setChecked(CfgDict['EX_NASDAQGSM_x'])
            self.DownloadCfgUI.NASDAQGM.setChecked(CfgDict['EX_NASDAQGM_x'])
            self.DownloadCfgUI.NASDAQCM.setChecked(CfgDict['EX_NASDAQCM_x'])

            self.DownloadCfgUI.NYSEMKT.setChecked(CfgDict['EX_NYSEMKT_x'])
            self.DownloadCfgUI.NYSE.setChecked(CfgDict['EX_NYSE_x'])
            self.DownloadCfgUI.NYSEARCA.setChecked(CfgDict['EX_NYSEARCA_x'])
            self.DownloadCfgUI.BATS.setChecked(CfgDict['EX_BATS_x'])
            self.DownloadCfgUI.IEXG.setChecked(CfgDict['EX_IEXG_x'])

            self.DownloadCfgUI.List_Favor.setChecked(CfgDict['List_Favor_x'])

            self.DownloadCfgUI.Intervial_1Day.setChecked(CfgDict['Intervial_1Day_x'])
            self.DownloadCfgUI.Intervial_1h.setChecked(CfgDict['Intervial_1h_x'])
            self.DownloadCfgUI.Intervial_30min.setChecked(CfgDict['Intervial_30min_x'])
            self.DownloadCfgUI.Intervial_15min.setChecked(CfgDict['Intervial_15min_x'] )
            self.DownloadCfgUI.Intervial_5min.setChecked(CfgDict['Intervial_5min_x'])
            self.DownloadCfgUI.Intervial_1min.setChecked(CfgDict['Intervial_1min_x'])
            self.DownloadCfgUI.Intervial_Current.setChecked(CfgDict['Intervial_Current_x'])

            CheckedRadioButton = self.DownloadCfgUI.DownloadIR.button(CfgDict['DownloadIR_x'])
            CheckedRadioButton.setChecked(True)

            self.DownloadCfgUI.DownloadPeriod.setValue(ZfinanceCfg.PeriodDict['PeriodStrPara'].index(CfgDict['DownloadPeriod_x']))

            self.DownloadCfgUI.MulitThreadDL.setCurrentIndex(MulitThreadList_c.index(str(CfgDict['MulitThreadDL_x'])))
            self.DownloadCfgUI.ReConnect.setCurrentIndex(ReConnectList_c.index(str(CfgDict['ReConnectCnt_x'])))
            self.DownloadCfgUI.TimeOut.setCurrentIndex(TimeOutList_c.index(str(CfgDict['TimeOut_x'])))

            self.DownloadCfgUI.VPNEnable.setChecked(CfgDict['VPNEnable_x'])

            self.GlobalMainUI.SymbolsDownloadLog.setText('HandleOpenDLConfig!!'+ConfigFilePathName[0])
        except:
            pass
        print(ConfigFilePathName)


    def CloseDownloadCfgUI(self):
        self.DownloadCfgUI.close()
        self.GlobalMainUI.SymbolsDownloadLog.setText('CloseDownloadCfgUI!!')

def HandleDownloadAbort(self):
    global DownloadAbortFlag,TableWidgetChannel,GlobalMainUI,GlobalAPP
    DownloadAbortFlag = True
    GlobalMainUI.SymbolsDownloadAbort.setDisabled(True)
    GlobalAPP.processEvents()


def HandleDownloadStart(self):
    global DownloadAbortFlag
    global Process,ProcessLen, GlobalMainUI,TableInitFlag,CfgDict,VPN
    DownloadAbortFlag = False
    Process = 0
    PeriodLimitlList = []
    IntervialAndPeriodList = []
    GlobalMainUI.SymbolsDownloadStart.setDisabled(True)
    GlobalAPP.processEvents()

    DownloadPeriod = CfgDict['DownloadPeriod_x']
    Period2Days = ZfinanceCfg.PeriodDict['Period2Days'][ZfinanceCfg.PeriodDict['PeriodStrPara'].index(DownloadPeriod)]

    if CfgDict['Intervial_1Day_x']:
        IntervialAndPeriodList.append(['1d',DownloadPeriod,Period2Days])
    if CfgDict['Intervial_1h_x']:
        if ZfinanceCfg.PeriodDict['PeriodStrPara'].index(DownloadPeriod) > ZfinanceCfg.PeriodDict['PeriodStrPara'].index('1mo'):
            IntervialAndPeriodList.append(['1h', '1mo',20])
        else:
            IntervialAndPeriodList.append(['1h', DownloadPeriod,Period2Days])

    if CfgDict['Intervial_30min_x']:
        if ZfinanceCfg.PeriodDict['PeriodStrPara'].index(DownloadPeriod) > ZfinanceCfg.PeriodDict['PeriodStrPara'].index('1mo'):
            IntervialAndPeriodList.append(['30m', '1mo',20])
        else:
            IntervialAndPeriodList.append(['30m', DownloadPeriod,Period2Days])
    if CfgDict['Intervial_15min_x']:
        if ZfinanceCfg.PeriodDict['PeriodStrPara'].index(DownloadPeriod) > ZfinanceCfg.PeriodDict['PeriodStrPara'].index('1mo'):
            IntervialAndPeriodList.append(['15m', '1mo',20])
        else:
            IntervialAndPeriodList.append(['15m', DownloadPeriod,Period2Days])
    if CfgDict['Intervial_5min_x']:
        if ZfinanceCfg.PeriodDict['PeriodStrPara'].index(DownloadPeriod) > ZfinanceCfg.PeriodDict['PeriodStrPara'].index('1mo'):
            IntervialAndPeriodList.append(['5m', '1mo',20])
        else:
            IntervialAndPeriodList.append(['5m', DownloadPeriod,Period2Days])
    if CfgDict['Intervial_1min_x']:
        if ZfinanceCfg.PeriodDict['PeriodStrPara'].index(DownloadPeriod) > ZfinanceCfg.PeriodDict['PeriodStrPara'].index('5d'):
            IntervialAndPeriodList.append(['1m', '5d',3])
        else:
            IntervialAndPeriodList.append(['1m', DownloadPeriod,Period2Days])
    if CfgDict['Intervial_Current_x']:
        IntervialAndPeriodList.append(['Cur', '*', '*'])

    ReConnectCnt = CfgDict['ReConnectCnt_x']

    if CfgDict['VPNEnable_x']:
        VPN = '127.0.0.1:7890'
    else:
        VPN = None
    #http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs

    SymbolsList = []
    NasdaqTickerList = pd.read_csv('Data\\00_Config\\NasdaqTickerList.csv',sep='|')
    NyseAmexTickerList = pd.read_csv('Data\\00_Config\\NyseAmexTickerList.csv', sep='|')
    if CfgDict['EX_NASDAQGSM_x']:
        Temp = NasdaqTickerList.loc[NasdaqTickerList['Market Category'].isin(['Q'])]
        SymbolsList.extend(Temp['Symbol'].tolist())
    if CfgDict['EX_NASDAQGM_x']:
        Temp = NasdaqTickerList.loc[NasdaqTickerList['Market Category'].isin(['G'])]
        SymbolsList.extend(Temp['Symbol'].tolist())
    if CfgDict['EX_NASDAQCM_x']:
        Temp = NasdaqTickerList.loc[NasdaqTickerList['Market Category'].isin(['S'])]
        SymbolsList.extend(Temp['Symbol'].tolist())

    if CfgDict['EX_NYSEMKT_x']:
        Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['A'])]
        SymbolsList.extend(Temp['ACT Symbol'].tolist())
    if CfgDict['EX_NYSE_x']:
        Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['N'])]
        SymbolsList.extend(Temp['ACT Symbol'].tolist())
    if CfgDict['EX_NYSEARCA_x']:
        Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['P'])]
        SymbolsList.extend(Temp['ACT Symbol'].tolist())
    if CfgDict['EX_BATS_x']:
        Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['Z'])]
        SymbolsList.extend(Temp['ACT Symbol'].tolist())
    if CfgDict['EX_IEXG_x']:
        Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['V'])]
        SymbolsList.extend(Temp['ACT Symbol'].tolist())


    IntervalCfg = 0
    ProcessLen = len(SymbolsList)
    GlobalMainUI.SymbolsDownloadProgressBar.setValue(0)
    #QTableWidget.setRowHeight()horizontalHeader().setSectionResizeMode(QHeaderView.Fixed);

    if False:#TableInitFlag:
        GlobalMainUI.SymbolsDownloadTable.clear()
       # GlobalMainUI.SymbolsDownloadTable.setRowCount(0)
        pass
    else:
        TableInitFlag = True
        GlobalMainUI.SymbolsDownloadTable.clear()
        GlobalMainUI.SymbolsDownloadTable.setRowCount(0)
        GlobalMainUI.SymbolsDownloadTable.setColumnCount(len(IntervialAndPeriodList)+1)
        GlobalMainUI.SymbolsDownloadTable.setRowCount(ProcessLen)
        GlobalMainUI.SymbolsDownloadTable.verticalHeader().setVisible(False)
        #GlobalMainUI.SymbolsDownloadTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        GlobalMainUI.SymbolsDownloadTable.horizontalHeader().setDefaultAlignment(PySide2.QtCore.Qt.AlignLeft)
        GlobalMainUI.SymbolsDownloadTable.setFont(QFont('song', 6))
        GlobalMainUI.SymbolsDownloadTable.horizontalHeader().setFont(QFont('song', 6))
        GlobalMainUI.SymbolsDownloadTable.verticalScrollBar().setValue(0)
        Row = 0
        for i in SymbolsList:
            SymbolsInTable = PySide2.QtWidgets.QTableWidgetItem(i)
            GlobalMainUI.SymbolsDownloadTable.setRowHeight(Row, 5)
            GlobalMainUI.SymbolsDownloadTable.setItem(Row, 0, SymbolsInTable)
            Row = Row+1

        GlobalMainUI.SymbolsDownloadTable.setColumnWidth(0, 35)

        Col = 1
        for i in range(len(IntervialAndPeriodList)):
            GlobalMainUI.SymbolsDownloadTable.setColumnWidth(Col,25)
            Col = Col+1
        Temp = ['SYM']
        for i in IntervialAndPeriodList:
            Temp.append(i[0])
        GlobalMainUI.SymbolsDownloadTable.setHorizontalHeaderLabels(Temp)
        # ############################非线程启动测试
        # Process = 0
        # for i in range(len(SymbolsList)):
        #     for j in range(len(IntervialList) - 1):
        #         #time.sleep(0.01)
        #         TempColorGreen = PySide2.QtWidgets.QTableWidgetItem('')
        #         TempColorGreen.setBackgroundColor(PySide2.QtGui.QColor(0, 255, 0))
        #         GlobalMainUI.SymbolsDownloadTable.setItem(i, j + 1, TempColorGreen)
        #         Process = Process+1
        #         GlobalMainUI.SymbolsDownloadProgressBar.setValue(Process / ProcessLen * 100)
        # #############################

    ThreadNum =  CfgDict['MulitThreadDL_x']
    ProcessLen = ProcessLen*ThreadNum
    TimeStamp = str(int(time.time()))
    # GlobalMainUI.SymbolsDownloadTable.verticalScrollBar().setValue(10)
    # return

    SYM = Zfinance.SingleStockQuotations('AAPL')
    Tempdf = SYM.FetchHistoryData(period='5d', interval='1d',PROXY=VPN)
    NewFileEndTime = int(Tempdf.index[-1].strftime("%Y%m%d"))

    global ThreadCnt
    ThreadCnt = ThreadNum
    for i in range(ThreadNum):
        thread = Thread(target=DownloadThread,
                        args=(SymbolsList,IntervialAndPeriodList,i,ReConnectCnt,TimeStamp,NewFileEndTime)
                        )
        thread.start()
    pass

ProcessLocker = threading.Lock()
CreatFolderLocker   = threading.Lock()
CreatInUseLocker   = threading.Lock()
import glob

def DeleteUselessOKNG(FolderPath):
    for i in glob.glob(FolderPath+'/TAG_*'):
        os.remove(i)

def GetCompleteFileName(Path):
    for i in glob.glob(Path+'*'):
        return(os.path.basename(i))
    return None

ScrollBarPosition = 0

def DownloadThread(SymbolsList=[],IntervialAndPeriodList = [],ThreadIndex = 0,ReConnectCnt = 1,TimeStamp='',NewFileEndTime=None):
    global GlobalMainUI, DownloadProcessBarChannel,DownloadAbortFlag,Process,ScrollBarPosition
    global TempColorGreen, TempColorYellow, TempColorRed,VPN,ThreadCnt

    RootDir = 'Data/01_TickerDatabase/'
    TempRow = -1

    for Symbol in SymbolsList:

        TempRow += 1
        if(TempRow>ScrollBarPosition):
            ScrollBarPosition = TempRow
            if ScrollBarPosition>5:
                GlobalMainUI.SymbolsDownloadTable.verticalScrollBar().setValue(ScrollBarPosition-4)

        ProcessLocker.acquire()
        Process += 1
        ProcessLocker.release()
        if DownloadAbortFlag:
            break
        TempFolderPath = RootDir + Symbol
        CreatFolderLocker.acquire()
        if (not os.path.exists(TempFolderPath)):
            try:
                os.mkdir(TempFolderPath)
            except:
                GlobalMainUI.SymbolsDownloadLog.append('Creat Folder : <'+TempFolderPath+'> Failed')
        CreatFolderLocker.release()

        OKFilePath = TempFolderPath + '/TAG_OK_' + TimeStamp
        NGFilePath = TempFolderPath + '/TAG_NG_' + TimeStamp
        InUseFilePath = TempFolderPath + '/InUse'

        if os.path.exists(OKFilePath) or os.path.exists(NGFilePath):
            continue
        else:
            CreatInUseLocker.acquire()
            if(not os.path.exists(InUseFilePath)):
                open(InUseFilePath,'w').close()
                DeleteUselessOKNG(TempFolderPath)       #删除之前的NG OK标签
                CreatInUseLocker.release()
            else:
                CreatInUseLocker.release()
                continue
            TempCol = 0
            OKFLAG = True
            for IntervialAndPeriodList_i in IntervialAndPeriodList:
                TempCol += 1
                TempIntervial   = IntervialAndPeriodList_i[0]
                TempPeriod      = IntervialAndPeriodList_i[1]
                TableWidgetChannel.TableSignal.emit(TempRow, TempCol, TempColorYellow)

                for ReConnectCnt_i in range(ReConnectCnt):
                    if(IntervialAndPeriodList_i[0] == 'Cur'):
                        SYM = yfinance.Ticker(Symbol)
                       # SYM.info
                        TickerCurrentInfo = SYM.get_info(proxy=VPN)
                        try:
                            TickerInfo = pd.read_csv(TempFolderPath+'/'+Symbol+'_Info.csv')
                        except:
                            TickerInfo = pd.DataFrame(TickerCurrentInfo)
                            TickerInfo.set_index(['symbol'], inplace=True)

                        TempTickersDataFrame = pd.DataFrame([TickerCurrentInfo])
                        TempTickersDataFrame.set_index(['symbol'], inplace=True)

                        TickerInfo = TickerInfo.append(TempTickersDataFrame)
                        TickerInfo.to_csv(TempFolderPath+'/'+Symbol+'_Info.csv',sep=',',index_label='symbol')
                        continue
                    TempPath = GetCompleteFileName(Path = TempFolderPath + '/' + Symbol + "_" + IntervialAndPeriodList_i[0])
                    if IntervialAndPeriodList_i[2] == -1:
                        NewFileStartTime = 19000101
                    else:
                        NewFileStartTime = int((datetime.datetime.now() - datetime.timedelta(days=IntervialAndPeriodList_i[2])).strftime("%Y%m%d"))

                    if(TempPath != None):
                        ExistFileStartTime  = int(TempPath.split('_')[2])
                        ExistFileEndTime    = int(TempPath.split('_')[3])
                        if ((TempPath.split('_')[4] == 'max.csv')and (ExistFileEndTime>=NewFileEndTime)) or\
                        ((ExistFileStartTime<=NewFileStartTime) and (ExistFileEndTime>=NewFileEndTime)):        #如果已存在文件范围比要下载的大
                            TableWidgetChannel.TableSignal.emit(TempRow, TempCol, TempColorGreen)               #不再下载，直接标绿色
                            continue                                                                            #退出此次循环
                        Tempdf_Exist = pd.read_csv(TempFolderPath + '/' + TempPath, sep=',', index_col='DateTime')
                        os.remove(TempFolderPath + '/' + TempPath)
                    else:
                        ExistFileEndTime = ExistFileStartTime = NewFileEndTime


                    try:
                        SYM = Zfinance.SingleStockQuotations(Symbol)
                        NewFileStartTimeStr = str(NewFileStartTime)
                        NewFileEndTimeStr   = str(NewFileEndTime)
                        if(ExistFileStartTime<NewFileStartTime<ExistFileEndTime):
                            Tempstr_list = list(str(ExistFileEndTime))
                            Tempstr_list.insert(4,'-')
                            Tempstr_list.insert(7, '-')
                            Temp = ''.join(Tempstr_list)
                            Tempdf = SYM.FetchHistoryData(start=Temp, interval=TempIntervial,PROXY=VPN)

                        else:
                            Tempdf = SYM.FetchHistoryData(period=TempPeriod,interval=TempIntervial,PROXY=VPN)
                            Tempdf_Exist = pd.DataFrame()

                        if (len(Tempdf) != 0):
                            Tempdf.index = Tempdf.index.strftime("%Y-%m-%d")
                            Tempdf = Tempdf_Exist.append(Tempdf)
                            Tempdf = Tempdf[~Tempdf.index.duplicated(keep='last')]

                            NewFileStartTimeStr = Tempdf.index[0].replace('-','')
                            NewFileEndTimeStr   = Tempdf.index[-1].replace('-','')


                            TempSYMFileName = TempFolderPath + '/' + Symbol + "_" + str(TempIntervial) + "_" + \
                                              NewFileStartTimeStr + '_' + NewFileEndTimeStr + '_'+TempPeriod+'.csv'
                            Tempdf.to_csv(TempSYMFileName, sep=',', index_label='DateTime')
                            TableWidgetChannel.TableSignal.emit(TempRow, TempCol, TempColorGreen)
                        else:
                            TableWidgetChannel.TableSignal.emit(TempRow, TempCol, TempColorRed)
                            OKFLAG = False
                    except:
                        GlobalMainUI.SymbolsDownloadLog.append('Download Fail : <' + Symbol + "_" + str(TempIntervial) + "_" + \
                                              NewFileStartTimeStr + '_' + NewFileEndTimeStr + '_'+TempPeriod+'.csv'+'> Failed')
                        TableWidgetChannel.TableSignal.emit(TempRow, TempCol, TempColorRed)
                        OKFLAG = False
            if OKFLAG:
                open(OKFilePath,'w').close()
            else:
                open(NGFilePath,'w').close()

            os.remove(InUseFilePath)
        DownloadProcessBarChannel.PBarSignal.emit(Process)
    ThreadCnt-=1
    if ThreadCnt == 0:
        GlobalMainUI.SymbolsDownloadStart.setDisabled(False)
        GlobalMainUI.SymbolsDownloadAbort.setDisabled(False)
        GlobalAPP.processEvents()



import enum

class SignalThreadChannel(QObject):
    TableSignal = Signal(int,int,int)
    PBarSignal = Signal(int)
    LPBarSignal = Signal(pd.DataFrame)

def UpdateListProcessBarWidget(df = pandas.DataFrame()):
    df.to_csv('Data/00_Config/TickerList.csv',sep=',')


def UpdateDownloadProcessBarWidget(Process):
    global  GlobalMainUI,ProcessLen
    GlobalMainUI.SymbolsDownloadProgressBar.setValue(Process / ProcessLen * 100)

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
