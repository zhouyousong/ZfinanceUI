import Zfinance
from ZfinanceCfg import TableColor

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


import json
import os
import  threading
from threading import Thread

ProcessLock = threading.Lock()
TableLock   = threading.Lock()

MulitThreadList_c = ['1','3','5','10','20']
ReConnectList_c = ['1','3','5','10','20']
TimeOutList_c = ['5','10','20','30','60']

DownloadAbortFlag = True
Process = 0
ProcessLen = 100
TableInitFlag = False
GlobalMainUIx = 1
CfgDict = dict()
TableWidgetChannel = None
ProcessBarChannel = None

TempColorYellow = PySide2.QtWidgets.QTableWidgetItem('')
TempColorYellow.setBackgroundColor(PySide2.QtGui.QColor(255, 255, 0))

TempColorRed = PySide2.QtWidgets.QTableWidgetItem('')
TempColorRed.setBackgroundColor(PySide2.QtGui.QColor(255, 0, 0))

TempColorGreen = PySide2.QtWidgets.QTableWidgetItem('')
TempColorGreen.setBackgroundColor(PySide2.QtGui.QColor(0, 255, 0))

class DownloadUIProc:
    def __init__(self,GlobalUI):
        global GlobalMainUI,CfgDict,TableWidgetChannel,ProcessBarChannel
        self.GlobalMainUI = GlobalUI
        GlobalMainUI = GlobalUI
        self.DownloadCfgUI = QUiLoader().load('UIDesign\DownloadConfig.ui')
        ###################发射定义##############################
        TableWidgetChannel = SignalThreadChannel()
        ProcessBarChannel  = SignalThreadChannel()

        TableWidgetChannel.TableSignal.connect(UpdateTableWidget)
        ProcessBarChannel.PBarSignal.connect(UpdateProcessBarWidget)
        #######################################################

        self.GlobalMainUI.SymbolsDownloadConfig.clicked.connect(self.HandleDownloadConfig)
        self.GlobalMainUI.SymbolsDownloadStart.clicked.connect(HandleDownloadStart)
        self.GlobalMainUI.SymbolsDownloadAbort.clicked.connect(HandleDownloadAbort)

        self.DownloadCfgUI.CancelDownload.clicked.connect(self.CloseDownloadCfgUI)
        self.DownloadCfgUI.ConfirmDownload.clicked.connect(self.HandleConfirmDownload)
        self.DownloadCfgUI.OpenDLConfig.clicked.connect(self.HandleOpenDLConfig)
        self.DownloadCfgUI.SaveDLConfig.clicked.connect(self.HandleSaveDLConfig)
        self.DownloadCfgUI.DownloadPeriod.sliderMoved.connect(self.HandleDownloadPeriod)
        self.DownloadCfgUI.DownloadPeriod.valueChanged.connect(self.HandleDownloadPeriod)


        ConfigFilePathName = os.getcwd()+'\\Data\\00_Config\\Default.ZFCfg'
        try:
            with open(ConfigFilePathName,'r') as load_f:
                CfgDict = json.load(load_f)
            self.GlobalMainUI.SymbolsDownloadLog.setText('Load Default Download Config success!!')
        except:
            self.GlobalMainUI.SymbolsDownloadLog.setText('Load Default Download Config Fail!!')
            pass

    def HandleDownloadPeriod(self):
        DownloadPeriod_x = self.DownloadCfgUI.DownloadPeriod.value()
        PeriodStr = ["1 Day","7 Days",'15 Days','30 Days','60 Days','90 Days','180 Days','360 Days','720 Days',"10 Years",'20 Years','MAX']
        self.DownloadCfgUI.ShowPeriod.setText(str(DownloadPeriod_x)+':'+PeriodStr[DownloadPeriod_x])
      #  QLabel.setText()
    def HandleDownloadConfig(self):
        #  info = self.ui.SymbolsDownloadLog.toPlainText()
        self.GlobalMainUI.SymbolsDownloadLog.setText('HandleDownloadConfig!!')
        self.DownloadCfgUI.show()
        self.DownloadCfgUI.DownloadPeriod.setMaximum(11)
        self.DownloadCfgUI.DownloadPeriod.setMinimum(0)
        self.DownloadCfgUI.DownloadPeriod.setTickInterval(1)

        self.DownloadCfgUI.MulitThreadDL.addItems(MulitThreadList_c)
        self.DownloadCfgUI.ReConnect.addItems(ReConnectList_c)
        self.DownloadCfgUI.TimeOut.addItems(TimeOutList_c)

    def HandleConfirmDownload(self):

        CfgDict['EX_NYSE_x'] = self.DownloadCfgUI.EX_NYSE.isChecked()
        CfgDict['EX_NASDAQ_x']  = self.DownloadCfgUI.EX_NASDAQ.isChecked()
        CfgDict['EX_AMEX_x']  = self.DownloadCfgUI.EX_AMEX.isChecked()
        CfgDict['List_Favor_x']  = self.DownloadCfgUI.List_Favor.isChecked()

        CfgDict['Intervial_1Day_x']  = self.DownloadCfgUI.Intervial_1Day.isChecked()
        CfgDict['Intervial_4h_x']  = self.DownloadCfgUI.Intervial_4h.isChecked()
        CfgDict['Intervial_1h_x']  = self.DownloadCfgUI.Intervial_1h.isChecked()
        CfgDict['Intervial_30min_x']  = self.DownloadCfgUI.Intervial_30min.isChecked()
        CfgDict['Intervial_15min_x']  = self.DownloadCfgUI.Intervial_15min.isChecked()
        CfgDict['Intervial_10min_x']  = self.DownloadCfgUI.Intervial_10min.isChecked()
        CfgDict['Intervial_5min_x']  = self.DownloadCfgUI.Intervial_5min.isChecked()
        CfgDict['Intervial_1min_x']  = self.DownloadCfgUI.Intervial_1min.isChecked()
        CfgDict['Intervial_Current_x']  = self.DownloadCfgUI.Intervial_Current.isChecked()

        CfgDict['DownloadIR_x']    = self.DownloadCfgUI.DownloadIR.checkedId()

        CfgDict['DownloadPeriod_x'] = self.DownloadCfgUI.DownloadPeriod.value()

        CfgDict['MulitThreadDL_x'] = self.DownloadCfgUI.MulitThreadDL.currentIndex()
        CfgDict['ReConnect_x'] = self.DownloadCfgUI.ReConnect.currentIndex()
        CfgDict['TimeOut_x'] = self.DownloadCfgUI.TimeOut.currentIndex()
        CfgDict['VPNEnable_x'] = self.DownloadCfgUI.VPNEnable.isChecked()


        self.DownloadCfgUI.close()
        self.GlobalMainUI.SymbolsDownloadLog.setText('HandleConfirmDownload!!')

    def HandleSaveDLConfig(self):

        CfgDict['EX_NYSE_x'] = self.DownloadCfgUI.EX_NYSE.isChecked()
        CfgDict['EX_NASDAQ_x']  = self.DownloadCfgUI.EX_NASDAQ.isChecked()
        CfgDict['EX_AMEX_x']  = self.DownloadCfgUI.EX_AMEX.isChecked()
        CfgDict['List_Favor_x']  = self.DownloadCfgUI.List_Favor.isChecked()

        CfgDict['Intervial_1Day_x']  = self.DownloadCfgUI.Intervial_1Day.isChecked()
        CfgDict['Intervial_4h_x']  = self.DownloadCfgUI.Intervial_4h.isChecked()
        CfgDict['Intervial_1h_x']  = self.DownloadCfgUI.Intervial_1h.isChecked()
        CfgDict['Intervial_30min_x']  = self.DownloadCfgUI.Intervial_30min.isChecked()
        CfgDict['Intervial_15min_x']  = self.DownloadCfgUI.Intervial_15min.isChecked()
        CfgDict['Intervial_10min_x']  = self.DownloadCfgUI.Intervial_10min.isChecked()
        CfgDict['Intervial_5min_x']  = self.DownloadCfgUI.Intervial_5min.isChecked()
        CfgDict['Intervial_1min_x']  = self.DownloadCfgUI.Intervial_1min.isChecked()
        CfgDict['Intervial_Current_x'] = self.DownloadCfgUI.Intervial_Current.isChecked()

        CfgDict['DownloadIR_x']    = self.DownloadCfgUI.DownloadIR.checkedId()

        CfgDict['DownloadPeriod_x'] = self.DownloadCfgUI.DownloadPeriod.value()

        CfgDict['MulitThreadDL_x'] = self.DownloadCfgUI.MulitThreadDL.currentIndex()
        CfgDict['ReConnect_x'] = self.DownloadCfgUI.ReConnect.currentIndex()
        CfgDict['TimeOut_x'] = self.DownloadCfgUI.TimeOut.currentIndex()
        CfgDict['VPNEnable_x'] = self.DownloadCfgUI.VPNEnable.isChecked()


        ConfigFilePathName ,ok = QFileDialog.getSaveFileName(None, "配置文件保存",'Data/00_Config','ZfinanceCfg (*.ZFCfg)')

        if ConfigFilePathName == "":
            self.GlobalMainUI.SymbolsDownloadLog.setText('Cancel Save ZFCfg!!' )
            return

        with open(ConfigFilePathName, "w") as f:
            json.dump(CfgDict, f,indent=1)

        self.GlobalMainUI.SymbolsDownloadLog.setText('HandleSaveDLConfig!!'+ConfigFilePathName[0])
        return

    def HandleOpenDLConfig(self):
        ConfigFilePathName ,ok= QFileDialog.getOpenFileName(None, "选择配置文件",'Data/00_Config','ZfinanceCfg (*.ZFCfg)')
        if ConfigFilePathName == "":
            self.GlobalMainUI.SymbolsDownloadLog.setText('Cancel Save ZFCfg!!' )
            return

        with open(ConfigFilePathName, 'r') as load_f:
            CfgDict = json.load(load_f)

        self.DownloadCfgUI.EX_NYSE.setChecked(CfgDict['EX_NYSE_x'])
        self.DownloadCfgUI.EX_NASDAQ.setChecked(CfgDict['EX_NASDAQ_x'])
        self.DownloadCfgUI.EX_AMEX.setChecked(CfgDict['EX_AMEX_x'])
        self.DownloadCfgUI.List_Favor.setChecked(CfgDict['List_Favor_x'])

        self.DownloadCfgUI.Intervial_1Day.setChecked(CfgDict['Intervial_1Day_x'])
        self.DownloadCfgUI.Intervial_4h.setChecked(CfgDict['Intervial_4h_x'])
        self.DownloadCfgUI.Intervial_1h.setChecked(CfgDict['Intervial_1h_x'])
        self.DownloadCfgUI.Intervial_30min.setChecked(CfgDict['Intervial_30min_x'])
        self.DownloadCfgUI.Intervial_15min.setChecked(CfgDict['Intervial_15min_x'] )
        self.DownloadCfgUI.Intervial_10min.setChecked(CfgDict['Intervial_10min_x'])
        self.DownloadCfgUI.Intervial_5min.setChecked(CfgDict['Intervial_5min_x'])
        self.DownloadCfgUI.Intervial_1min.setChecked(CfgDict['Intervial_1min_x'])
        self.DownloadCfgUI.Intervial_Current.setChecked(CfgDict['Intervial_Current_x'])

        CheckedRadioButton = self.DownloadCfgUI.DownloadIR.button(CfgDict['DownloadIR_x'])
        CheckedRadioButton.setChecked(True)

        self.DownloadCfgUI.DownloadPeriod.setValue(CfgDict['DownloadPeriod_x'])

        self.DownloadCfgUI.MulitThreadDL.setCurrentIndex(CfgDict['MulitThreadDL_x'] )
        self.DownloadCfgUI.ReConnect.setCurrentIndex(CfgDict['ReConnect_x'])
        self.DownloadCfgUI.TimeOut.setCurrentIndex(CfgDict['TimeOut_x'])
        self.DownloadCfgUI.VPNEnable.setChecked(CfgDict['VPNEnable_x'])

        self.GlobalMainUI.SymbolsDownloadLog.setText('HandleOpenDLConfig!!'+ConfigFilePathName[0])
        print(ConfigFilePathName)


    def CloseDownloadCfgUI(self):
        self.DownloadCfgUI.close()
        self.GlobalMainUI.SymbolsDownloadLog.setText('CloseDownloadCfgUI!!')

def HandleDownloadAbort(self):
    global DownloadAbortFlag,TableWidgetChannel
    TableWidgetChannel.emitSignal.emit("Signal emit with para")
    DownloadAbortFlag = True

def HandleDownloadStart(self):
    global DownloadAbortFlag
    global Process,ProcessLen, GlobalMainUIm,TableInitFlag
    DownloadAbortFlag = False
    Process = 0
    IntervialList = ['SYM']

    if CfgDict['Intervial_1Day_x']:
        IntervialList.append('1D')
    if CfgDict['Intervial_4h_x']:
        IntervialList.append('4h')
    if CfgDict['Intervial_1h_x']:
        IntervialList.append('1h')
    if CfgDict['Intervial_30min_x']:
        IntervialList.append('30m')
    if CfgDict['Intervial_15min_x']:
        IntervialList.append('15m')
    if CfgDict['Intervial_10min_x']:
        IntervialList.append('10m')
    if CfgDict['Intervial_5min_x']:
        IntervialList.append('5m')
    if CfgDict['Intervial_1min_x']:
        IntervialList.append('1m')
    if CfgDict['Intervial_Current_x']:
        IntervialList.append('Cur')

    SymbolsList = []
    if CfgDict['EX_AMEX_x']:
        SymbolsList.extend(Zfinance.GetExchangeSymbolList('AMEX'))
    if CfgDict['EX_NYSE_x']:
        SymbolsList.extend(Zfinance.GetExchangeSymbolList('NYSE'))
    if CfgDict['EX_NASDAQ_x']:
        SymbolsList.extend(Zfinance.GetExchangeSymbolList('NASDAQ'))
    IntervalCfg = 0
    ProcessLen = len(SymbolsList)

    #QTableWidget.setRowHeight()horizontalHeader().setSectionResizeMode(QHeaderView.Fixed);

    if False:#TableInitFlag:
        GlobalMainUI.SymbolsDownloadTable.clear()
       # GlobalMainUI.SymbolsDownloadTable.setRowCount(0)
        pass
    else:
        TableInitFlag = True
        GlobalMainUI.SymbolsDownloadTable.clear()
        GlobalMainUI.SymbolsDownloadTable.setRowCount(0)
        GlobalMainUI.SymbolsDownloadTable.setColumnCount(len(IntervialList))
        GlobalMainUI.SymbolsDownloadTable.setRowCount(ProcessLen)
        GlobalMainUI.SymbolsDownloadTable.verticalHeader().setVisible(False)
        GlobalMainUI.SymbolsDownloadTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        GlobalMainUI.SymbolsDownloadTable.horizontalHeader().setDefaultAlignment(PySide2.QtCore.Qt.AlignLeft)
        GlobalMainUI.SymbolsDownloadTable.setFont(QFont('song', 6))
        GlobalMainUI.SymbolsDownloadTable.horizontalHeader().setFont(QFont('song', 6))

        Row = 0
        for i in SymbolsList:
            SymbolsInTable = PySide2.QtWidgets.QTableWidgetItem(i)
            GlobalMainUI.SymbolsDownloadTable.setRowHeight(Row, 5)
            GlobalMainUI.SymbolsDownloadTable.setItem(Row, 0, SymbolsInTable)
            Row = Row+1

        GlobalMainUI.SymbolsDownloadTable.setColumnWidth(0, 30)

        Col = 1
        for i in range(len(IntervialList)-1):
            GlobalMainUI.SymbolsDownloadTable.setColumnWidth(Col,25)
            Col = Col+1

        GlobalMainUI.SymbolsDownloadTable.setHorizontalHeaderLabels(IntervialList)
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

    ThreadNum = 10
    ProcessLen = ProcessLen*ThreadNum
    for i in range(ThreadNum):
        thread = Thread(target=DownloadThread,
                        args=(SymbolsList,IntervialList,i)
                        )
        time.sleep(0.002)
        thread.start()
    pass
    return

def DownloadThread(SymbolsList=[],IntervialList = [],ThreadIndex = 0):
    global GlobalMainUI,ProcessBarChannel
    global Process, ProcessLen,TempColorRed,TempColorYellow,TempColorGreen
    RootDir = 'Data/01_SymbolsData/'
    TempRow = 0

    for i in SymbolsList:
        if DownloadAbortFlag:
            break
        TempFolderPath = RootDir+i
        TempInUseFilePath = RootDir+i+'/FileInUse'
        if(os.path.exists(TempFolderPath)) == False:
            try:
                os.mkdir(TempFolderPath)
            except:
                pass
        if(os.path.exists(TempInUseFilePath)):
            for j in range(len(IntervialList) - 1):
                try:
                    ProcessLock.acquire()
                    try:
                        pass
                        TableWidgetChannel.TableSignal.emit(TempRow, j + 1, 1)
                        # TempColorGreen = PySide2.QtWidgets.QTableWidgetItem('')
                        # TempColorGreen.setBackgroundColor(PySide2.QtGui.QColor(0, 255, 0))
                        # GlobalMainUI.SymbolsDownloadTable.setItem(TempRow, j + 1, TempColorGreen)
                    finally:
                        ProcessLock.release()
                except:
                    pass
            pass
        else:
            try:
                fpA = open(TempInUseFilePath, 'w')
                fpB = open(TempInUseFilePath + str(ThreadIndex), 'w')

                for j in range(len(IntervialList)-1):
                    ProcessLock.acquire()
                    try:
                        pass
                        #TableWidgetChannel.TableSignal.emit(TempRow, j + 1, 2)
                        TempColorYellow = PySide2.QtWidgets.QTableWidgetItem('')
                        TempColorYellow.setBackgroundColor(PySide2.QtGui.QColor(255, 255, 0))
                        GlobalMainUI.SymbolsDownloadTable.setItem(TempRow, j+1, TempColorYellow)
                    finally:
                        ProcessLock.release()
                    time.sleep(0.1)
                    ProcessLock.acquire()
                    try:
                        pass
                        #TableWidgetChannel.TableSignal.emit(TempRow,j+1,1)
                        TempColorGreen = PySide2.QtWidgets.QTableWidgetItem('')
                        TempColorGreen.setBackgroundColor(PySide2.QtGui.QColor(0, 255, 0))
                        GlobalMainUI.SymbolsDownloadTable.setItem(TempRow, j+1, TempColorGreen)
                    finally:
                        ProcessLock.release()

                fpB.close()
                fpA.close()
            except:
                pass
        ProcessLock.acquire()
        try:
            Process = Process+1
            ProcessBarChannel.PBarSignal.emit(Process)
        finally:
            ProcessLock.release()

        TempRow = TempRow+1
    pass
#查看文件夹是否存在，不存在则创建文件夹
#下载时间间隔的临时j文件
#如果是全新下载，删除之前的文件，把临时文件改为最终文件
#如果是增量下载，拼接时间
#可拼接，重新计算
######################################################

import enum

class SignalThreadChannel(QObject):
    TableSignal = Signal(int,int,int)
    PBarSignal = Signal(int)

def UpdateProcessBarWidget(Process):
    global  GlobalMainUI,ProcessLen
    GlobalMainUI.SymbolsDownloadProgressBar.setValue(Process / ProcessLen * 100)


def UpdateTableWidget(row,col,color):
    global GlobalMainUI
    TempColor = PySide2.QtWidgets.QTableWidgetItem('')
    TempColor.setBackgroundColor(PySide2.QtGui.QColor(0, 0, 255))
    if color == 1:
        TempColor.setBackgroundColor(PySide2.QtGui.QColor(0, 255, 0))
    if color == 2:
       TempColor.setBackgroundColor(PySide2.QtGui.QColor(255, 255, 0))
    if color == 3:
        TempColor.setBackgroundColor(PySide2.QtGui.QColor(0, 255, 0))

    GlobalMainUI.SymbolsDownloadTable.setItem(row, col, TempColor)

###########################################################
