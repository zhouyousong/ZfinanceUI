from PySide2.QtWidgets import QApplication, QMessageBox,QFileDialog
from PySide2.QtUiTools import QUiLoader
import ZfinanceUI_Download

import time

SortList=['Sector','Ind','State']

class Stats:

    def __init__(self):
        # 从文件中加载UI定义

        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.MainUI = QUiLoader().load('UIDesign\Zfinance.ui')

#        self.MainUI.SymbolsDownloadConfig.clicked.connect(self.HandleDownloadConfig)

        self.MainUI.SortCombox.addItems(SortList)


    # def HandleDownloadConfig(self):
    #   #  info = self.ui.SymbolsDownloadLog.toPlainText()
    #     self.MainUI.SymbolsDownloadLog.setText('sfddsf')
    #     DownloadCfgUI.show()
    #
    #     DownloadCfgUI.CancelDownload.clicked.connect(self.CloseDownloadCfgUI)
    #     DownloadCfgUI.ConfirmDownload.clicked.connect(self.HandleConfirmDownload)
    #     DownloadCfgUI.OpenDLConfig.clicked.connect(self.HandleOpenDLConfig)
    #     DownloadCfgUI.SaveDLConfig.clicked.connect(self.HandleSaveDLConfig)
    #
    # def HandleConfirmDownload(self):
    #     print('download thread')
    #
    # def HandleOpenDLConfig(self):
    #     ConfigFilePathName = QFileDialog.getOpenFileName(None, "选择配置文件")
    #     print(ConfigFilePathName)
    #
    # def HandleSaveDLConfig(self):
    #     ConfigFilePathName ,ok2= QFileDialog.getSaveFileName(None, "配置文件保存")
    #     print(ConfigFilePathName)
    #
    # def CloseDownloadCfgUI(self):
    #     DownloadCfgUI.close()


app = QApplication([])

stats = Stats()
GlobalMainUI = stats.MainUI
DownloadUI = ZfinanceUI_Download.DownloadUIProc(GlobalMainUI)




stats.MainUI.show()
app.exec_()