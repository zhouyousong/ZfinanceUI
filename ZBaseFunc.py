import PySide2.QtWidgets ,PySide2.QtWidgets ,PySide2.QtGui
import pandas as pd
from PySide2.QtWidgets import QApplication, QMessageBox,QFileDialog,QCheckBox
from PySide2.QtWidgets import QButtonGroup,QSlider,QLabel,QRadioButton,QTableWidget,QHeaderView
from PySide2.QtUiTools  import QUiLoader
from PySide2.QtGui import QFont
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import glob,os

import time
StartTime = 0
GlobalMainUI = None



def InitLogBox(UI = None):
    global GlobalMainUI,StartTime
    GlobalMainUI = UI
    StartTime = int(round(time.time() * 1000))
    timeArray = time.localtime(StartTime / 1000)
    StartTimestring = time.strftime("%H:%M:%S", timeArray)
    GlobalMainUI.LogBox.append("ZFinance Start:"+StartTimestring)
    return
def Log2LogBox(string =''):
    global GlobalMainUI,StartTime
    NowTime     = int(round(time.time() * 1000))
    timeArray = time.localtime(NowTime / 1000)
    NowTimeStr  = time.strftime("%H:%M:%S", timeArray)
    DeltaTime   = NowTime - StartTime
    StartTime = NowTime
    GlobalMainUI.LogBox.append(NowTimeStr+'|'+str(DeltaTime)+'ms|'+string)
    GlobalMainUI.LogBox.verticalScrollBar().setValue(GlobalMainUI.LogBox.verticalScrollBar().maximum())

InfoBuffer = None

def GetQtreeRootNode(Qtree =None):

    RootNoteList =[]
    Err = False
    i = 0
    while Err == False:
        try:
            RootNote = Qtree.topLevelItem(i).text(0)
            RootNoteList.append(RootNote)
        except:
            Err = True
        i+=1
    return RootNoteList


def SetTickersInfo(IN = None):
    global InfoBuffer
    InfoBuffer = IN

def GetTickersInfo():
    global InfoBuffer
    return InfoBuffer

def SortTrick(TempStr = ''):
    try:
        TempVal = float(TempStr)
    except:
        return TempStr
    if TempVal>=0:
        if TempVal < 1:
            TempStr = 'K*' + TempStr
        elif TempVal < 10:
            TempStr = 'L*' + TempStr
        elif TempVal < 100:
            TempStr = 'M*' + TempStr
        elif TempVal < 1000:
            TempStr = 'N*' + TempStr
        elif TempVal < 10000:
            TempStr = 'O*' + TempStr
        elif TempVal < 100000:
            TempStr = 'P*' + TempStr
        elif TempVal < 1000000:
            TempStr = 'Q*' + TempStr
        elif TempVal < 10000000:
            TempStr = 'R*' + TempStr
        elif TempVal < 100000000:
            TempStr = 'S*' + TempStr
        elif TempVal < 1000000000:
            TempStr = 'T*' + TempStr
        elif TempVal < 10000000000:
            TempStr = 'U*' + TempStr
        elif TempVal < 100000000000:
            TempStr = 'V*' + TempStr
        elif TempVal < 1000000000000:
            TempStr = 'W*' + TempStr
        else:
            TempStr = 'X*' + TempStr
    else:
        if TempVal > -1:
            TempVal = str(1+TempVal)
            TempStr = 'J'+TempVal +TempStr
        elif TempVal > -10:
            TempVal = str(10+TempVal)
            TempStr = 'I'+TempVal +TempStr
        elif TempVal > -100:
            TempVal = str(100+TempVal)
            TempStr = 'H'+TempVal +TempStr
        elif TempVal > -1000:
            TempVal = str(1000+TempVal)
            TempStr = 'G'+TempVal +TempStr
        elif TempVal > -10000:
            TempVal = str(10000+TempVal)
            TempStr = 'F'+TempVal +TempStr
        elif TempVal > -100000:
            TempVal = str(100000+TempVal)
            TempStr = 'E'+TempVal +TempStr
        elif TempVal > -1000000:
            TempVal = str(1000000+TempVal)
            TempStr = 'D'+TempVal +TempStr
        elif TempVal > -10000000:
            TempVal = str(10000000+TempVal)
            TempStr = 'C'+TempVal +TempStr
        elif TempVal > -100000000:
            TempVal = str(100000000+TempVal)
            TempStr = 'B'+TempVal +TempStr
        elif TempVal > -1000000000:
            TempVal = str(1000000000+TempVal)
            TempStr = 'A'+TempVal +TempStr

    return TempStr

def GetCompleteFileName(Path):
    for i in glob.glob(Path+'*'):
        return(os.path.basename(i))
    return None

def dataframe_generation_from_table(table):
    number_of_rows = table.rowCount()
    number_of_columns = table.columnCount()
    TempHeader = []
    TempIndexs = []
    for i in range(1,number_of_columns):
        TempHeader.append(table.horizontalHeaderItem(i).text())
    for i in range(number_of_rows):
        TempIndexs.append(table.item(i,0).text())
    tmp_df = pd.DataFrame(
                columns=TempHeader, # Fill columnets
                index=TempIndexs
                )

    for i in range(number_of_rows):
        for j in range(number_of_columns-1):
            try:
                tmp_df.iloc[i, j] = table.item(i, j+1).text()
            except:
                tmp_df.iloc[i, j] = 'NA'

    return tmp_df