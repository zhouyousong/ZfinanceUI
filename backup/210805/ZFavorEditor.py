#管理收藏列表(增加黑名单)
#停盘的记为灰色
#编辑(持仓，说明)，添加分类
#

import pandas as pd
import json,os

from PySide2.QtUiTools  import QUiLoader
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtCore

class FavorEditorUIProc:
    def __init__(self):
        self.FavorEditorUI = QUiLoader().load('UIDesign\FavorEditor.ui')
        self.FavorEditorUI.Input.textChanged.connect(self.HandleInputChanged)
        self.FavorEditorUI.ListFilter.doubleClicked.connect(self.HandleAddSymbol)
        self.FavorEditorUI.FavorList.itemDoubleClicked.connect(self.HandleFavorListDelete)
        self.FavorEditorUI.Save.clicked.connect(self.HandleSaveFavorList)

    def handleFavorEditor(self,SelectList=[],Input=''):
        if False:
            self.FavorEditorUI.FavorList = QTreeWidget()
            self.FavorEditorUI.Save = QPushButton()
            self.FavorEditorUI.Cancel = QPushButton()
            self.FavorEditorUI.ListFilter = QListView().setEditTriggers()
            self.FavorEditorUI.Input = QLineEdit()
        self.FavorEditorUI.show()
        self.FavorEditorUI.FavorList.setColumnCount(2)
        self.FavorEditorUI.FavorList.setHeaderLabels(('SYMBOL','POSITION','COMMENT'))
        self.FavorEditorUI.ListFilter.setEditTriggers(QAbstractItemView.NoEditTriggers)

 #       self.FavorEditorUI.Cancel.clicked.connect(self.HandleCancelFavorList)

        self.FavorListFilePathName = os.getcwd()+'\\Data\\00_Config\\DefaultFavor.ZFfv'
        try:
            with open(self.FavorListFilePathName,'r') as load_f:
                FavorDict = json.load(load_f)
            print('Load Default FavorList Config success!!')
        except:
            print('Load Default FavorList Config Fail!!')
            FavorDict={
                "DEFAULT":['AAPL'],
                'BLACKLIST':['QT']
            }
        self.FavorEditorUI.FavorList.clear()
        for FLGroup,FLSymbol in FavorDict.items():
            root = QTreeWidgetItem(self.FavorEditorUI.FavorList)
            root.setText(0, FLGroup)
            for i in FLSymbol:
                child = QTreeWidgetItem(root)
                child.setText(0, i[0])
                child.setText(1, i[1])
                child.setText(2, i[2])
                child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
        self.FavorEditorUI.FavorList.addTopLevelItem(root)

        self.FavorEditorUI.FavorList.setCurrentItem((self.FavorEditorUI.FavorList.topLevelItem(0)))

        if(len(SelectList) == 0):

            NasdaqTickerList = pd.read_csv('Data\\00_Config\\NasdaqTickerList.csv', sep='|')
            NyseAmexTickerList = pd.read_csv('Data\\00_Config\\NyseAmexTickerList.csv', sep='|')

            Temp = NasdaqTickerList.loc[NasdaqTickerList['Market Category'].isin(['Q'])]
            SelectList.extend(Temp['Symbol'].tolist())
            Temp = NasdaqTickerList.loc[NasdaqTickerList['Market Category'].isin(['G'])]
            SelectList.extend(Temp['Symbol'].tolist())
            Temp = NasdaqTickerList.loc[NasdaqTickerList['Market Category'].isin(['S'])]
            SelectList.extend(Temp['Symbol'].tolist())

            Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['A'])]
            SelectList.extend(Temp['ACT Symbol'].tolist())
            Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['N'])]
            SelectList.extend(Temp['ACT Symbol'].tolist())
            Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['P'])]
            SelectList.extend(Temp['ACT Symbol'].tolist())
            Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['Z'])]
            SelectList.extend(Temp['ACT Symbol'].tolist())
            Temp = NyseAmexTickerList.loc[NyseAmexTickerList['Exchange'].isin(['V'])]
            SelectList.extend(Temp['ACT Symbol'].tolist())

        self.SelectList = SelectList

        if(Input == ''):
            self.HandleInputChanged()

    def HandleItemText(self):
        print('fuck')

    def HandleInputChanged(self):
        if False:
            self.FavorEditorUI.FavorList = QTreeWidget().CurrentChanged.topLevelItem().setCurrentIndex()
            self.FavorEditorUI.Save = QPushButton()
            self.FavorEditorUI.Cancel = QPushButton()
            self.FavorEditorUI.ListFilter = QListView()
            self.FavorEditorUI.Input = QLineEdit()
        VagueSymbol = self.FavorEditorUI.Input.text()

        slm = QStringListModel()
        self.FliteredList=list(filter(lambda x: VagueSymbol in x, self.SelectList))
        slm.setStringList(self.FliteredList)
        self.FavorEditorUI.ListFilter.setModel(slm)


    def HandleAddSymbol(self):
        SelectedSymbol = self.FliteredList[self.FavorEditorUI.ListFilter.currentIndex().row()]
        print(SelectedSymbol)
        if (self.FavorEditorUI.FavorList.currentIndex().parent().row() != -1):
            cursor = QTreeWidgetItemIterator(self.FavorEditorUI.FavorList.currentItem().parent())
        else:
            cursor = QTreeWidgetItemIterator(self.FavorEditorUI.FavorList.currentItem())
        ChildCnt = cursor.value().childCount()
        cursor = cursor.__iadd__(1)
        for i in range(ChildCnt):
            Temp = cursor.value()
            print('dddd'+Temp.text(0) )
            print('xxxsss')
            print(Temp.childCount())
            if Temp.text(0) == SelectedSymbol:
                print('xxxxxxx' )
                return
            cursor = cursor.__iadd__(1)

        child = QTreeWidgetItem()
        child.setText(0, SelectedSymbol)
        child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
        if (self.FavorEditorUI.FavorList.currentIndex().parent().row() != -1):
            self.FavorEditorUI.FavorList.currentItem().parent().addChild(child)
        else:
            self.FavorEditorUI.FavorList.currentItem().addChild(child)

    def HandleFavorListDelete(self,item,colume):
        print(item)
        print('-*************')
        if(colume == 0):
            currNode = self.FavorEditorUI.FavorList.currentItem()
            if (self.FavorEditorUI.FavorList.currentIndex().parent().row() == -1):
                if (self.FavorEditorUI.FavorList.currentItem().text(0) != 'DEFAULT' and
                    self.FavorEditorUI.FavorList.currentItem().text(0) != 'BLACKLIST'):
                    self.FavorEditorUI.FavorList.takeTopLevelItem(self.FavorEditorUI.FavorList.indexOfTopLevelItem(currNode))
                else:
                    text, ok = QInputDialog.getText(self.FavorEditorUI, '添加分类', '输入新的分类名:')
                    if ok:
                        root = QTreeWidgetItem(self.FavorEditorUI.FavorList)
                        root.setText(0, text)

            else:
                TempParent = currNode.parent()
                TempParent.removeChild(currNode)


    def HandleSaveFavorList(self):
        FavorDict=dict()
        cursor = QTreeWidgetItemIterator(self.FavorEditorUI.FavorList)
        while cursor.value():
            Temp = cursor.value()
            print(self.FavorEditorUI.FavorList.indexOfTopLevelItem(Temp))
            print(Temp.text(0))
            if self.FavorEditorUI.FavorList.indexOfTopLevelItem(Temp) != -1:
                GroupLabel= Temp.text(0)
                FavorDict[GroupLabel] = []
            else:
                FavorDict[GroupLabel].append([Temp.text(0),Temp.text(1),Temp.text(2)])

            cursor = cursor.__iadd__(1)

        with open(self.FavorListFilePathName, "w") as f:
            json.dump(FavorDict, f)
        pass

