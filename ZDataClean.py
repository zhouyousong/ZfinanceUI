import pandas as pd
import json,os
import shutil

from PySide2.QtUiTools  import QUiLoader
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtCore

import ZBaseFunc,ZFavorEditor


class DataCleanUIProc:
    def __init__(self,GlobalAPP = None):

        self.DataCleanUI = QUiLoader().load('UIDesign\DataClean.ui')
        self.DataCleanUI.DataCleanProgressBar.setValue(0)

        self.DataCleanUI.DeleteAllDataBase.clicked.connect(self.handleDeleteAllDataBase)
        self.DataCleanUI.DeleteAllInfoFile.clicked.connect(self.handleDeleteAllInfoFile)
        self.DataCleanUI.DeleteInUseFile.clicked.connect(self.handleDeleteInUseFile)
        self.DataCleanUI.Delete1dShortFolder.clicked.connect(self.handleDelete1dShortFolder)
        self.DataCleanUI.DeleteInfoShortFolder.clicked.connect(self.handleDeleteInfoShortFolder)
        self.DataCleanUI.Pickup1dShort.clicked.connect(self.handlePickup1dShort)
        self.DataCleanUI.PickupInfoShort.clicked.connect(self.handlePickupInfoShort)
        self.GlobalApp = GlobalAPP

        self.DCFavorEditorFavorUI = ZFavorEditor.FavorEditorUIProc()

    def handleDataCleanUI(self):
        self.DataCleanUI.show()
        self.DataBasePath = os.getcwd() + '\\Data\\01_TickerDatabase'
        self.TickerFolders = os.listdir(self.DataBasePath)
        self.Mnt = len(self.TickerFolders)

    def handleDeleteAllDataBase(self):
        text, ok = QInputDialog.getText(self.DataCleanUI, '确定删除所有文件', '输入密码:')
        if ok == False:
            return
        if text != '123':
            return
        cnt = 0
        for TickerFolder in self.TickerFolders:
            cnt +=1
            try:
                shutil.rmtree(self.DataBasePath + '/' + TickerFolder )
                ZBaseFunc.Log2LogBox('Delete ' + TickerFolder + ' Folder successed')
            except:
                ZBaseFunc.Log2LogBox('Delete '+ TickerFolder+' Folder Failed')

            self.DataCleanUI.DataCleanProgressBar.setValue(cnt / self.Mnt * 100)
            self.GlobalApp.processEvents()

    def handleDeleteAllInfoFile(self):
        text, ok = QInputDialog.getText(self.DataCleanUI, '确定删除所有info文件？', '输入密码:')
        if ok == False:
            return
        if text != '123':
            return

        cnt = 0
        for TickerFolder in self.TickerFolders:
            cnt +=1
            TempInfPath = self.DataBasePath + '/' + TickerFolder + '/' + TickerFolder + '_inf'

            CompleteFileName = ZBaseFunc.GetCompleteFileName(TempInfPath)
            if CompleteFileName != None:
                try:
                    os.remove(self.DataBasePath + '/' + TickerFolder + '/'+CompleteFileName)
                except:
                    ZBaseFunc.Log2LogBox('Delete '+ CompleteFileName+' InfoFiles Failed')

            self.DataCleanUI.DataCleanProgressBar.setValue(cnt / self.Mnt * 100)
            self.GlobalApp.processEvents()

    def handleDeleteInUseFile(self):
        cnt = 0
        for TickerFolder in self.TickerFolders:
            cnt +=1
            TempInfPath = self.DataBasePath + '/' + TickerFolder + '/InUse'
            if os.path.exists(TempInfPath):
                try:
                    os.remove(TempInfPath)
                    ZBaseFunc.Log2LogBox('Delete InUse File ' + TickerFolder + ' Successed')
                except:
                    ZBaseFunc.Log2LogBox('Delete '+ TickerFolder+' InUse File Failed')

            self.DataCleanUI.DataCleanProgressBar.setValue(cnt / self.Mnt * 100)
            self.GlobalApp.processEvents()

    def handleDelete1dShortFolder(self):
        cnt = 0
        for TickerFolder in self.TickerFolders:
            cnt +=1
            TempInfPath = self.DataBasePath + '/' + TickerFolder + '/' + TickerFolder +'_1d'
            CompleteFileName = ZBaseFunc.GetCompleteFileName(TempInfPath)
            if CompleteFileName == None:
                try:
                    shutil.rmtree(self.DataBasePath + '/' + TickerFolder )
                    ZBaseFunc.Log2LogBox('Delete short 1d ' + TickerFolder + ' Folder successed')
                except:
                    ZBaseFunc.Log2LogBox('Delete short 1d '+ TickerFolder+' Folder Failed')

            self.DataCleanUI.DataCleanProgressBar.setValue(cnt / self.Mnt * 100)
            self.GlobalApp.processEvents()
        pass
    def handleDeleteInfoShortFolder(self):
        cnt = 0
        for TickerFolder in self.TickerFolders:
            cnt +=1
            TempInfPath = self.DataBasePath + '/' + TickerFolder + '/' + TickerFolder +'_inf'
            CompleteFileName = ZBaseFunc.GetCompleteFileName(TempInfPath)
            if CompleteFileName == None:
                try:
                    shutil.rmtree(self.DataBasePath + '/' + TickerFolder )
                    ZBaseFunc.Log2LogBox('Delete short info '+ TickerFolder+' Folder successed')
                except:
                    ZBaseFunc.Log2LogBox('Delete short info '+ TickerFolder+' Folder Failed')

            self.DataCleanUI.DataCleanProgressBar.setValue(cnt / self.Mnt * 100)
            self.GlobalApp.processEvents()
        pass
    def handlePickup1dShort(self):
        cnt = 0
        Short1dTickerList = []
        for TickerFolder in self.TickerFolders:
            cnt +=1
            TempInfPath = self.DataBasePath + '/' + TickerFolder + '/' + TickerFolder +'_1d'
            CompleteFileName = ZBaseFunc.GetCompleteFileName(TempInfPath)
            if CompleteFileName == None:
                Short1dTickerList.append(TickerFolder)

            self.DataCleanUI.DataCleanProgressBar.setValue(cnt / self.Mnt * 100)
            self.GlobalApp.processEvents()
        self.DCFavorEditorFavorUI.handleFavorEditor(SelectList=Short1dTickerList,NewClass='Short1dayTickers')
        pass
    def handlePickupInfoShort(self):
        cnt = 0
        Short1dTickerList = []
        for TickerFolder in self.TickerFolders:
            cnt +=1
            TempInfPath = self.DataBasePath + '/' + TickerFolder + '/' + TickerFolder +'_inf'
            CompleteFileName = ZBaseFunc.GetCompleteFileName(TempInfPath)
            if CompleteFileName == None:
                Short1dTickerList.append(TickerFolder)

            self.DataCleanUI.DataCleanProgressBar.setValue(cnt / self.Mnt * 100)
            self.GlobalApp.processEvents()
        self.DCFavorEditorFavorUI.handleFavorEditor(SelectList=Short1dTickerList,NewClass='ShortInfoTickers')