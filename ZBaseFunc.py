import PySide2.QtWidgets ,PySide2.QtWidgets ,PySide2.QtGui
import numpy
import pandas as pd
from PySide2.QtWidgets import QApplication, QMessageBox,QFileDialog,QCheckBox
from PySide2.QtWidgets import QButtonGroup,QSlider,QLabel,QRadioButton,QTableWidget,QHeaderView
from PySide2.QtUiTools  import QUiLoader
from PySide2.QtGui import QFont
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import glob,os,json
import yfinance as yf

import time

import ZfinanceCfg

StartTime = 0
GlobalMainUI = None


def GlobalProxy(string =''):
    global GlobalMainUI,StartTime
    NowTime     = int(round(time.time() * 1000))
    timeArray = time.localtime(NowTime / 1000)
    NowTimeStr  = time.strftime("%H:%M:%S", timeArray)
    DeltaTime   = NowTime - StartTime
    StartTime = NowTime
    GlobalMainUI.LogBox.append(NowTimeStr+'|'+str(DeltaTime)+'ms|'+string)
    GlobalMainUI.LogBox.verticalScrollBar().setValue(GlobalMainUI.LogBox.verticalScrollBar().maximum())
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
#################table Operation###########################
def CleanTable(TableColumeItem,Table):
    Table.clear()
    Table.setColumnCount(len(TableColumeItem) + 1)
    Table.setRowCount(0)
    Table.verticalHeader().setVisible(False)
    Table.horizontalHeader().setDefaultAlignment(PySide2.QtCore.Qt.AlignLeft)
    Table.setFont(QFont('song', 8))
    Table.horizontalHeader().setFont(QFont('song', 8))
    Table.verticalScrollBar().setValue(0)

    Table.setColumnWidth(0, 60)

    Col = 1
    for i in TableColumeItem:
        Table.setColumnWidth(Col, int(i.split(":")[1]))
        Col = Col + 1

    Temp = ['SYM']
    for i in TableColumeItem:
        Temp.append(i.split(":")[0])
    Table.setHorizontalHeaderLabels(Temp)
def AddFavorListToTable(InputTreeList,OutputTable):

    TempIndexs = []
    number_of_rows = OutputTable.rowCount()
    for i in range(number_of_rows):
        TempIndexs.append(OutputTable.item(i,0).text())

    cursor = QTreeWidgetItemIterator(InputTreeList)
    SymbolList = []
    while cursor.value():
        Temp = cursor.value()
        ChildCnt = Temp.childCount()
        if (ChildCnt == 0):
            if (Temp.checkState(0)):
                SymbolList.append(Temp.text(0))
                print('add-' + Temp.text(0))
        elif Temp.text(0) == 'BLACKLIST':
            for i in range(ChildCnt):
                cursor = cursor.__iadd__(1)
                Temp = cursor.value()
                # print('Delete-' + Temp.text(0))
                try:
                    SymbolList.remove(Temp.text(0))
                except:
                    pass
        cursor = cursor.__iadd__(1)
    ############################去重复
    SymbolList.extend(TempIndexs)
    temp_list = []
    for one in SymbolList:
        if one not in temp_list:
            temp_list.append(one)
    SymbolList = temp_list
    ############################
    OutputTable.setRowCount(len(SymbolList))
    Row = 0
    for i in SymbolList:
        SymbolsInTable = PySide2.QtWidgets.QTableWidgetItem(i)
        OutputTable.setRowHeight(Row, 5)
        OutputTable.setItem(Row, 0, SymbolsInTable)
        Row = Row + 1
    ############################
def RefreshTable(Table):    #保留行头列头

    TempHeader = []
    number_of_columns = Table.columnCount()
    for i in range(number_of_columns):
        TempHeader.append(Table.horizontalHeaderItem(i).text())

    TempIndexs = []
    number_of_rows = Table.rowCount()
    for i in range(number_of_rows):
        TempIndexs.append(Table.item(i,0).text())

    Table.clear()

    Table.setHorizontalHeaderLabels(TempHeader)

    Row = 0
    for i in TempIndexs:
        SymbolsInTable = PySide2.QtWidgets.QTableWidgetItem(i)
        Table.setItem(Row, 0, SymbolsInTable)
        Row = Row + 1

    return TempIndexs
def DisplayInTable(Table,SymbolResult):
    number_of_rows    = Table.rowCount()
    number_of_columns = Table.columnCount()

    for Row in range(number_of_rows):
        if SymbolResult["Symbol"] == Table.item(Row,0).text():
            break

    for key, value in SymbolResult.items():
        if key == "Symbol":
            continue
        else:
            for Col in range(1, number_of_columns):
                if key ==  Table.horizontalHeaderItem(Col).text():
                    StrShow = PySide2.QtWidgets.QTableWidgetItem(SymbolResult[key])
                    Table.setItem(Row, Col, StrShow)
#################table Operation New###########################
class TableOpt:
    def __init__(self,TargetTable,TableColumeItem):
        self.Table = TargetTable
        self.TableColumeItem = TableColumeItem
        self.Table.clear()
        self.Table.setColumnCount(len(self.TableColumeItem) + 1)
        self.Table.setRowCount(0)
        self.Table.verticalHeader().setVisible(False)
        self.Table.horizontalHeader().setDefaultAlignment(PySide2.QtCore.Qt.AlignLeft)
        self.Table.setFont(QFont('song', 8))
        self.Table.horizontalHeader().setFont(QFont('song', 8))
        self.Table.verticalScrollBar().setValue(0)

        self.Table.setColumnWidth(0, 60)

        Col = 1
        for i in TableColumeItem:
            self.Table.setColumnWidth(Col, int(i.split(":")[1]))
            Col = Col + 1

        Temp = ['SYM']
        for i in TableColumeItem:
            Temp.append(i.split(":")[0])
        self.Table.setHorizontalHeaderLabels(Temp)
    def InitTable(self):
        self.Table.clear()
        self.Table.setColumnCount(len(self.TableColumeItem) + 1)
        self.Table.setRowCount(0)
        self.Table.verticalHeader().setVisible(False)
        self.Table.horizontalHeader().setDefaultAlignment(PySide2.QtCore.Qt.AlignLeft)
        self.Table.setFont(QFont('song', 8))
        self.Table.horizontalHeader().setFont(QFont('song', 8))
        self.Table.verticalScrollBar().setValue(0)

        self.Table.setColumnWidth(0, 60)
        Col = 1
        for i in self.TableColumeItem:
            self.Table.setColumnWidth(Col, int(i.split(":")[1]))
            Col = Col + 1

        Temp = ['SYM']
        for i in self.TableColumeItem:
            Temp.append(i.split(":")[0])
        self.Table.setHorizontalHeaderLabels(Temp)
    def CleanTable(self,HoldColumes = None):    #保留行头列头
        TempHeader = []
        HoldColumeNo_Label = []
        TempColume = dict()
        number_of_columns = self.Table.columnCount()
        for Col in range(1, number_of_columns):
            for HoldColume in HoldColumes:
                if HoldColume == self.Table.horizontalHeaderItem(Col).text():
                    TempColume["Num"]   = Col
                    TempColume["Label"] = HoldColume
                    HoldColumeNo_Label.append(TempColume)


        for i in range(number_of_columns):
            TempHeader.append(self.Table.horizontalHeaderItem(i).text())

        TempIndexs = []
        number_of_rows = self.Table.rowCount()
        for i in range(number_of_rows):
            TempIndexs.append(self.Table.item(i,0).text())

        self.Table.clear()
        self.Table.setHorizontalHeaderLabels(TempHeader)

        for i in len(TempIndexs):
            SymbolsInTable = PySide2.QtWidgets.QTableWidgetItem(TempIndexs[i])
            self.Table.setItem(i, 0, SymbolsInTable)
            for HoldColumeNo_Label_Index in range(len(HoldColumeNo_Label)):

                SymbolsInTable = PySide2.QtWidgets.QTableWidgetItem(HoldColumeNo_Label_Index['Label'])
                self.Table.setItem(i, HoldColumeNo_Label_Index['Num'], SymbolsInTable)

        return TempIndexs
    def ImportSymbol_From_TreeList(self,InputTreeList,BlockBlackList = True):

        TempIndexs = []
        number_of_rows = self.Table.rowCount()
        for i in range(number_of_rows):
            TempIndexs.append(self.Table.item(i,0).text())
        if BlockBlackList:
            BlockItem = 'BLACKLIST'
        else:
            BlockItem = ''
        cursor = QTreeWidgetItemIterator(InputTreeList)
        SymbolList = []
        while cursor.value():
            Temp = cursor.value()
            ChildCnt = Temp.childCount()
            if (ChildCnt == 0):
                if (Temp.checkState(0)):
                    SymbolList.append(Temp.text(0))
                    print('add-' + Temp.text(0))
            elif Temp.text(0) == BlockItem:
                for i in range(ChildCnt):
                    cursor = cursor.__iadd__(1)
                    Temp = cursor.value()
                    # print('Delete-' + Temp.text(0))
                    try:
                        SymbolList.remove(Temp.text(0))
                    except:
                        pass
            cursor = cursor.__iadd__(1)
        ############################去重复
        SymbolList.extend(TempIndexs)
        temp_list = []
        for one in SymbolList:
            if one not in temp_list:
                temp_list.append(one)
        SymbolList = temp_list
        ############################
        self.Table.setRowCount(len(SymbolList))
        Row = 0
        for i in SymbolList:
            SymbolsInTable = PySide2.QtWidgets.QTableWidgetItem(i)
            self.Table.setRowHeight(Row, 5)
            self.Table.setItem(Row, 0, SymbolsInTable)
            Row = Row + 1
        ############################
    def RefreshOneRowInTable(self,SymbolResult):
        number_of_rows    = self.Table.rowCount()
        number_of_columns = self.Table.columnCount()

        for Row in range(number_of_rows):
            if SymbolResult["Symbol"] == self.Table.item(Row,0).text():
                break

        for key, value in SymbolResult.items():
            if key == "Symbol":
                continue
            else:
                for Col in range(1, number_of_columns):
                    if key ==  self.Table.horizontalHeaderItem(Col).text():
                        StrShow = PySide2.QtWidgets.QTableWidgetItem(SymbolResult[key])
                        self.Table.setItem(Row, Col, StrShow)
    def AddOneRowInTable(self,RowDict):
        number_of_rows    = self.Table.rowCount()
        number_of_columns = self.Table.columnCount()
        self.Table.setRowCount(number_of_rows +1)
        self.Table.setRowHeight(number_of_rows, 5)

        for key, value in RowDict.items():
            if key == "Symbol":
                StrShow = PySide2.QtWidgets.QTableWidgetItem(RowDict[key])
                self.Table.setItem(number_of_rows , 0, StrShow)
                continue
            else:
                for Col in range(1, number_of_columns):
                    if key ==  self.Table.horizontalHeaderItem(Col).text():
                        StrShow = PySide2.QtWidgets.QTableWidgetItem(RowDict[key])
                        self.Table.setItem(number_of_rows, Col, StrShow)
    def GetOneRowInTable(self,Row):
        number_of_columns = self.Table.columnCount()
        TempDict=dict()
        TempDict['Symbol'] = self.Table.item(Row, 0).text()
        for i in range(1, number_of_columns):
            try:
                TempDict[self.Table.horizontalHeaderItem(i).text()] = self.Table.item(Row, i).text()
            except:
                pass

        return TempDict
    def GetAllRowIndexInTable(self):
        number_of_rows = self.Table.rowCount()
        TempIndexs = []
        for i in range(number_of_rows):
            TempIndexs.append(self.Table.item(i, 0).text())
        return TempIndexs
#################TreeList Operation#############################
class TreeListOpt:
    def __init__(self,TargetTreeList,TreeColumeItem):
        self.TreeList = TargetTreeList
        self.TreeList.setColumnCount(len(TreeColumeItem)-1)
        self.TreeList.setHeaderLabels(TreeColumeItem)
        self.TreeList.clear()
    def CleanTreeList(self):
        self.TreeList.clear()
    def AddL1RootToTreeList(self,AddItem,Property = dict(),CheckBox=None):

        root = QTreeWidgetItem(self.TreeList)
        root.setText(0, AddItem)
        for Key, Value in Property.items():
            for i in range(1, self.TreeList.columnCount()):
                if Key == self.TreeList.headerItem().text(i):
                    root.setText(i, Value)
        if CheckBox:
            root.setCheckState(0, Qt.Checked)
        elif CheckBox == False:
            root.setCheckState(0, Qt.Unchecked)
        pass
        self.TreeList.addTopLevelItem(root)

        self.TreeList.setCurrentItem((self.TreeList.topLevelItem(0)))
    def AddChildToSelectRoot(self, AddItem,CheckBox=None):#没有去重

        child = QTreeWidgetItem()
        child.setText(0, AddItem)
        if CheckBox != None:
            if CheckBox:
                child.setCheckState(0, Qt.Checked)
            else :
                child.setCheckState(0, Qt.Unchecked)
            child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)

        if (self.TreeList.currentIndex().parent().row() != -1):
            self.TreeList.currentItem().parent().addChild(child)
        else:
            self.TreeList.currentItem().addChild(child)
    def AddChildToRootByName(self, AddItem,RootName,CheckBox=None):#没有去重
        child = QTreeWidgetItem()
        child.setText(0, AddItem)
        if CheckBox != None:
            if CheckBox:
                child.setCheckState(0, Qt.Checked)
            else :
                child.setCheckState(0, Qt.Unchecked)
            child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)

        cursor = QTreeWidgetItemIterator(self.TreeList)
        while cursor.value():
            Temp = cursor.value()
            if(Temp.text(0) == RootName) and (Temp.parent().row() == -1):
                Temp.addChild(child)
                return
            cursor = cursor.__iadd__(1)
    def DelSelected(self):#没有去重
        currNode = self.TreeList.currentItem()
        if (self.TreeList.currentIndex().parent().row() != -1):
            TempParent = currNode.parent()
        else:
            TempParent = currNode
        TempParent.removeChild(currNode)
    def ModifySelected(self,NewString):  # 没有去重
        currNode = self.TreeList.currentItem()
        currNode.setText(0,NewString)
    def GetL0RootItems(self):
        Items = []
        Key = []
        Tempx = dict()
        self.TreeList.headerItem().text(0)
        for i in range(self.TreeList.columnCount()):
            Key.append(self.TreeList.headerItem().text(i))

        cursor = QTreeWidgetItemIterator(self.TreeList)

        while cursor.value():
            Temp = cursor.value()
            if Temp.parent() == None:
                i = 0
                for k in Key:
                    Tempx[k] = Temp.text(i)
                    i += 1
                Items.append(Tempx.copy())
            cursor = cursor.__iadd__(1)
        return Items
    def GetChildrenOfSelectRoot(self):
        Children = []
        ChildCnt = self.TreeList.currentItem().childCount()
        if ChildCnt == 0:
            return self.TreeList.currentItem().text(0)
        else:
            cursor = QTreeWidgetItemIterator(self.TreeList.currentItem())

        cursor = cursor.__iadd__(1)

        for i in range(ChildCnt):
            Temp = cursor.value()
            Children.append(Temp.text(0))
            cursor = cursor.__iadd__(1)

        return Children
    def GetSelectedItemName(self):

        return self.TreeList.currentItem().text(0)
    def GetChildrenOfRootByName(self,RootName):
        Children = []
        cursor = QTreeWidgetItemIterator(self.TreeList)
        while cursor.value():
            Temp = cursor.value()
            if(Temp.text(0) == RootName) and (Temp.childCount() != 0):
                ChildCnt = Temp.childCount()
                cursor = cursor.__iadd__(1)
                for i in range(ChildCnt):
                    Temp = cursor.value()
                    Children.append(Temp.text(0))
                    cursor = cursor.__iadd__(1)
                break
            cursor = cursor.__iadd__(1)
        return Children
    def GetCheckedSymbol(self,Check):
        if Check == True:
            checkstatus = PySide2.QtCore.Qt.CheckState.Checked
        else:
            checkstatus = PySide2.QtCore.Qt.CheckState.Unchecked

        TempIndexs = []
        SymbolList = []
        cursor = QTreeWidgetItemIterator(self.TreeList)
        while cursor.value():
            Temp = cursor.value()
            ChildCnt = Temp.childCount()
            if (ChildCnt == 0):
                if (Temp.checkState(0) == checkstatus):
                    SymbolList.append(Temp.text(0))
            elif Temp.text(0) == 'BLACKLIST':
                for i in range(ChildCnt):
                    cursor = cursor.__iadd__(1)
                    Temp = cursor.value()
                    try:
                        SymbolList.remove(Temp.text(0))
                    except:
                        pass
            cursor = cursor.__iadd__(1)
        ############################去重复
        SymbolList.extend(TempIndexs)
        temp_list = []
        for one in SymbolList:
            if one not in temp_list:
                temp_list.append(one)
        return temp_list
        ############################
    def SetCheckChildrenOfSelectRoot(self,Check):
        if Check == True:
            checkstatus = PySide2.QtCore.Qt.CheckState.Checked
        else:
            checkstatus = PySide2.QtCore.Qt.CheckState.Unchecked
        self.TreeList.currentItem().setCheckState(0, checkstatus)
        cursor = QTreeWidgetItemIterator(self.TreeList.currentItem())
        ChildCnt = cursor.value().childCount()
        cursor = cursor.__iadd__(1)
        for i in range(ChildCnt):
            cursor.value().setCheckState(0, checkstatus)
            cursor = cursor.__iadd__(1)
    def SetCheckChildrenOfRootByName(self,RootName,Check):
        if Check == True:
            checkstatus = PySide2.QtCore.Qt.CheckState.Unchecked
        else:
            checkstatus = PySide2.QtCore.Qt.CheckState.Checked

        cursor = QTreeWidgetItemIterator(self.TreeList)
        while cursor.value():
            Temp = cursor.value()
            if(Temp.text(0) == RootName) and (Temp.childCount() != 0):
                ChildCnt = Temp.childCount()
                Temp.setCheckState(0, checkstatus)
                cursor = cursor.__iadd__(1)
                for i in range(ChildCnt):
                    Temp = cursor.value()
                    Temp.setCheckState(0, checkstatus)
                    cursor = cursor.__iadd__(1)
                break
            cursor = cursor.__iadd__(1)
    def SaveToConfigFile_L2(self, FilePath):
        SaveDict = dict()
        cursor = QTreeWidgetItemIterator(self.TreeList)
        while cursor.value():
            Temp = cursor.value()
            if self.TreeList.indexOfTopLevelItem(Temp) != -1:    #顶层
                GroupLabel = Temp.text(0)
                SaveDict[GroupLabel] = {
                    'Property': dict(),
                    'Children': []
                }
                try:
                    if Temp.checkState(0) == PySide2.QtCore.Qt.CheckState.Checked:
                        SaveDict[GroupLabel]["Checked"] = True
                    else:
                        SaveDict[GroupLabel]["Children"][-1]["Checked"] = False
                except:
                    pass
                for i in range(1,self.TreeList.columnCount()):
                    SaveDict[GroupLabel]['Property'][self.TreeList.headerItem().text(i)] = Temp.text(i)

            else:
                X = {
                    'Key':Temp.text(0),
                    'Property':dict()
                }
                SaveDict[GroupLabel]["Children"].append(X)
                try:
                    if Temp.checkState(0) == PySide2.QtCore.Qt.CheckState.Checked:
                        SaveDict[GroupLabel]["Children"][-1]["Checked"] = True
                    else:
                        SaveDict[GroupLabel]["Children"][-1]["Checked"] = False
                except:
                    pass
                for i in range(1, self.TreeList.columnCount()):
                    SaveDict[GroupLabel]["Children"][-1]['Property'][self.TreeList.headerItem().text(i)] = Temp.text(i)
            cursor = cursor.__iadd__(1)
        with open(FilePath, "w") as f:
            json.dump(SaveDict, f,indent=1)
    def LoadFromConfigFile_L2(self, FileName):


        try:
            with open(FileName, 'r') as load_f:
                TreeListDict = json.load(load_f)
        except:
            print('Load Default FavorList Config Fail!!')
            return

        self.TreeList.clear()
        # FavorList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        for Group, Member in TreeListDict.items():
            root = QTreeWidgetItem(self.TreeList)
            root.setText(0, Group)
            try:
                if Member["Checked"]:
                    root.setCheckState(0, Qt.Checked)
                else:
                    root.setCheckState(0, Qt.Unchecked)
            except:
                pass

            for Key, Value in Member['Property'].items():
                for i in range(1, self.TreeList.columnCount()):
                    if Key == self.TreeList.headerItem().text(i):
                        root.setText(i, Value)

            for Member_i in Member['Children']:
                child = QTreeWidgetItem(root)
                child.setText(0, Member_i['Key'])
                try:
                    if Member_i["Checked"]:
                        child.setCheckState(0, Qt.Checked)
                    else:
                        child.setCheckState(0, Qt.Unchecked)
                except:
                    pass
                for Key, Value in Member_i['Property'].items():
                    for i in range(1, self.TreeList.columnCount()):
                        if Key == self.TreeList.headerItem().text(i):
                            child.setText(i, Value)


                child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
        self.TreeList.addTopLevelItem(root)
        self.TreeList.setCurrentItem((self.TreeList.topLevelItem(0)))
        return
###############Config File Operation##############################
def LoadConfigFile(FileName,DefaultDict):
    FilePathName = os.getcwd() + '\\Data\\00_Config\\'+FileName
    try:
        with open(FilePathName, 'r') as load_f:
            LoadDict = json.load(load_f)
        Log2LogBox("Load User Config file:[" + FileName + "]Successed")
    except:
        Log2LogBox("Load User Config file:[" + FileName + "]Failed,system default will used")
        LoadDict = DefaultDict

    return LoadDict
def LoadConfigFilePath(FilePath,DefaultDict):
    try:
        with open(FilePath, 'r') as load_f:
            LoadDict = json.load(load_f)
        Log2LogBox("Load User Config file:[" + FilePath + "]Successed")
    except:
        Log2LogBox("Load User Config file:[" + FilePath + "]Failed,system default will used")
        LoadDict = DefaultDict

    return LoadDict
def SaveConfigFile(FileName, DumpDict):
    FilePathName = os.getcwd() + '\\Data\\00_Config\\'+FileName
    try:
        with open(FilePathName, "w") as f:
            json.dump(DumpDict, f,indent=1)
            Log2LogBox("Save User Config file:[" + FileName + "] Successed")
    except:
        Log2LogBox("Save User Config file:[" + FileName + "] Failed")

    return
###############Market Data Operation##############################
import yfinance,efinance,requests,time,datetime,numpy
DLNetPara = dict()

def SetDLAPIPara(key,value):
    global DLNetPara
    DLNetPara[key] = value

def DownloadSymbolList(Exchange='US'):
    pass
class StockSymbolData:
    def __init__(self,Symbol = '',Platfrom = ZfinanceCfg.DownloadPlatform.yfinance.value):
        if Platfrom == ZfinanceCfg.DownloadPlatform.yfinance.value:
            self.Symbol = yfinance.Ticker(Symbol)
            self.SymbolStr = Symbol
            self.Proxy = DLNetPara['PROXY']
            self.Platfrom = ZfinanceCfg.DownloadPlatform.yfinance
        elif Platfrom == ZfinanceCfg.DownloadPlatform.TdaAPI.value:
            self.Symbol = Symbol
            self.Platfrom = ZfinanceCfg.DownloadPlatform.TdaAPI
        elif Platfrom == ZfinanceCfg.DownloadPlatform.efinance.value:
            self.Symbol = Symbol.split('.')[0]
            self.Platfrom = ZfinanceCfg.DownloadPlatform.efinance
        try:
            self.MarketType = Symbol.split('.')[1]
        except:
            self.MarketType = None
        return
    def DownloadSymbolHistoryData(self,Period = 0,Interval = '5m',timeout = 5):
        global DLNetPara
        result = {'Success': False}
        print("--------------" )
        print("PeriodIn:"+str(Period))
        print("IntervalIn:" + str(Interval))

        PeriodMax = ZfinanceCfg.PeriodLimitDict['LimitPeriodInDay'][self.Platfrom.value][Interval]
        PeriodUnit = ZfinanceCfg.PeriodLimitDict['UnitExchange'][self.Platfrom.value]['DefaultPeriodUnit']

        if Period ==0:
            Period = PeriodMax
        elif type(PeriodMax) == type(int()):
            if Period >PeriodMax:
                Period = PeriodMax

        try:
            UnitExchange = ZfinanceCfg.PeriodLimitDict['UnitExchange'][self.Platfrom.value][Interval]
            for UnitExchange_i in UnitExchange:
                if Period%UnitExchange_i['PeriodDiv'] == 0:
                    Period = int(Period / UnitExchange_i['PeriodDiv'])
                    PeriodUnit = UnitExchange_i['PeriodUnit']
                    Interval = UnitExchange_i['Intervalunit']
                    break
        except:
            if Period == 'max':
                PeriodUnit = ''
            pass
        print("Period:"+str(Period))
        print("PeriodUnit:" + str(PeriodUnit))
        print("Interval:" + str(Interval))
        tempdf = pd.DataFrame()
        if self.Platfrom == ZfinanceCfg.DownloadPlatform.yfinance:
            if Period == 0:
                Period = 'max'
                PeriodUnit = ''
            try:
                tempdf = self.Symbol.history(prepost=True,period = str(Period)+PeriodUnit,interval=Interval,proxy=self.Proxy)
            except:
                Log2LogBox('TdaAPI yfinance Failed')

        elif self.Platfrom == ZfinanceCfg.DownloadPlatform.TdaAPI:
            if 'm' in Interval:
                frequencyType = 'minute'
            elif 'd' in Interval:
                frequencyType = 'daily'
            else:
                print('Error')
            frequency = Interval[:-1]
            headers = {
            'Authorization':'Bearer '+DLNetPara['AccessToken']
                }
            ParaDict = {
                'apikey':DLNetPara['OAuthUserID'],
                'periodType' : PeriodUnit,
                'period' : str(Period),
                'frequencyType' : frequencyType,
                'frequency' : frequency,
                'endDate':str(int(round(time.time() * 1000))),
                'needExtendedHoursData' :'true'
            }
            ParaDictstr = ''
            for key,value in ParaDict.items():
                ParaDictstr = ParaDictstr+key+'='+value+'&'
            ParaDictstr = ParaDictstr[:-1]
            url = 'https://api.tdameritrade.com/v1/marketdata/' + self.Symbol + '/pricehistory?'+ParaDictstr

            try:
                response = requests.get(url = url, headers=headers)
                Result = json.loads(response.content.decode())['candles']
                tempdf = pd.read_json(json.dumps(Result),orient = 'records')

                tempdf.rename(columns={'datetime':'DateTime',
                                       'open': 'Open',
                                       'high': 'High',
                                       'low': 'Low',
                                       'close': 'Close',
                                       'volume': 'Volume'},inplace=True)
                tempdf['Dividends'] = tempdf['Stock Splits'] = numpy.nan
                tempdf.set_index('DateTime',inplace=True)
            except:
                Log2LogBox('TdaAPI Download Failed')

        elif self.Platfrom == ZfinanceCfg.DownloadPlatform.efinance:
            try:
                tempdfx = efinance.stock.get_quote_history(stock_codes=self.Symbol,klt=Interval)
                tempdf = pd.DataFrame()
                tempdf['DateTime'] = tempdfx['日期']
                tempdf['Open'] = tempdfx['开盘']
                tempdf['High'] = tempdfx['最高']
                tempdf['Low'] = tempdfx['最低']
                tempdf['Close'] = tempdfx['收盘']
                tempdf['Volume'] = tempdfx['成交量']
                tempdf['Volume'] = tempdfx['成交量']
                tempdf['Dividends'] = tempdf['Stock Splits'] = numpy.nan
                tempdf.set_index('DateTime', inplace=True)
            except:
                Log2LogBox('efinance Download Failed')

        if len(tempdf) != 0:
            if self.Platfrom != ZfinanceCfg.DownloadPlatform.efinance:

                    if (Interval == '1d'):
                        tempdf.index = tempdf.index.strftime("%Y-%m-%d")
                        timeArray = time.strptime(tempdf.index[-1], '%Y-%m-%d')
                    else:
                        tempdf.index = tempdf.index.strftime("%Y-%m-%d %H:%M")
                        timeArray = time.strptime(tempdf.index[-1], '%Y-%m-%d %H:%M')
            else:
                if (Interval == 101):
                    timeArray = time.strptime(tempdf.index[-1], '%Y-%m-%d')
                else:
                    timeArray = time.strptime(tempdf.index[-1], '%Y-%m-%d %H:%M')
            LastTimeStamp = int(time.mktime(timeArray))

            result = {
                'Success': True,
                'DataFrame':tempdf,
                'TimeStamp':LastTimeStamp
            }

        return result
    def GetRealTimeData(self):
        result = dict()
        result['Success'] = False
        if self.Platfrom == ZfinanceCfg.DownloadPlatform.yfinance:
            try:
                Temp = yfinance.Ticker(self.SymbolStr)
                ResponseJson = Temp.get_info(proxy=self.Proxy)
                result['Price'] = ResponseJson['regularMarketPrice']
                result['Timestamp'] = int(round(time.time() * 1000))
                result['Success'] = True
            except:
                pass
        elif self.Platfrom == ZfinanceCfg.DownloadPlatform.TdaAPI:
            headers = {
            'Authorization':'Bearer '+DLNetPara['AccessToken']
                }
            ParaDict = {
                'apikey':DLNetPara['OAuthUserID'],
             }
            ParaDictstr = ''
            for key,value in ParaDict.items():
                ParaDictstr = ParaDictstr+key+'='+value+'&'
            ParaDictstr = ParaDictstr[:-1]
            url = 'https://api.tdameritrade.com/v1/marketdata/' + self.Symbol + '/quotes?'+ParaDictstr

            try:
                response = requests.get(url = url, headers=headers)
                ResponseJson = json.loads(response.content.decode())[self.Symbol]
                result['Price'] = ResponseJson['mark']
                result['Timestamp'] = int(ResponseJson['quoteTimeInLong']/1000)
                result['Success'] = True
            except:
                pass
        elif self.Platfrom == ZfinanceCfg.DownloadPlatform.efinance:
            try:
                Tempdf = efinance.stock.get_latest_quote([self.Symbol])
                result['Price']     = Tempdf['最新价'][0]
                result['Timestamp'] = int(round(time.time() * 1000))
                result['Success'] = True
            except:
                pass

        return result
    def DownloadSymbolBaseInfoData(self):#行业，市值等信息
        result = dict()
        result['Success'] = False
        if self.Platfrom == ZfinanceCfg.DownloadPlatform.yfinance:
            try:
                BaseInfo = self.Symbol.get_info(proxy=self.Proxy)
                BaseInfo['UpdateTime'] = datetime.datetime.now().strftime('%Y-%m-%d')
                BaseInfo = pd.DataFrame([BaseInfo])
                BaseInfo.set_index(['symbol'], inplace=True)
                result['Success'] = True
                result['DataFrame'] = BaseInfo
            except:
                pass
        elif self.Platfrom == ZfinanceCfg.DownloadPlatform.TdaAPI:
            pass
        elif self.Platfrom == ZfinanceCfg.DownloadPlatform.efinance:
            try:
                BaseInfo = efinance.stock.get_base_info(self.Symbol)
                BaseInfo['UpdateTime'] = [datetime.datetime.now().strftime('%Y-%m-%d')]
                BaseInfo = pd.DataFrame(BaseInfo.to_frame().T)
                BaseInfo.set_index(['股票代码'], inplace=True)
                result['Success'] = True
                result['DataFrame'] = BaseInfo
            except:
                pass
        return result
    def DownloadSymbolFinanceData(self,FinanceItem = 'fin'):#分红等
        result = dict()
        result['Success'] = False
        try:
            if   FinanceItem == 'fin':
                Reply = self.Symbol.get_financials(proxy=self.Proxy, freq='quarterly').stack().unstack(0)
            elif FinanceItem == 'bal':
                Reply = self.Symbol.get_balancesheet(proxy=self.Proxy, freq='quarterly').stack().unstack(0)
            elif FinanceItem == 'cas':
                Reply = self.Symbol.get_cashflow(proxy=self.Proxy, freq='quarterly').stack().unstack(0)
            elif FinanceItem == 'div':
                Reply = self.Symbol.get_dividends(proxy=self.Proxy)
            elif FinanceItem == 'spl':
                Reply = self.Symbol.get_splits(proxy=self.Proxy)
            if len(Reply) != 0:
                result(
                    {
                        'Success': True,
                        'Type':FinanceItem,
                        'DataFrame':Reply
                    }
                )
        except:
            pass

        return result

#####################################################################
def TestTheAPI(Platfrom=ZfinanceCfg.DownloadPlatform.yfinance):
    X = StockSymbolData(Symbol='AAPL', Platfrom=Platfrom)
    intervalList =['1m','5m','15m','30m','60m','1d']
    PeriodList = [1,5,30,60,90,180,365,730,1825,3650,0]
    intervalList =['1d']
    PeriodList = [0]
    for interval in intervalList:
        for Period in PeriodList:
            df = X.DownloadSymbolHistoryData(Interval=interval, Period=Period)
            if df['Success']:
                print(df['DataFrame'])
