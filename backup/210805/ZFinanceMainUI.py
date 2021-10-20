from PySide2.QtWidgets import QApplication, QMessageBox,QFileDialog
from PySide2.QtUiTools import QUiLoader
import ZfinanceUI_Download
import Zfinance
import ZFavorEditor

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

ZTimer = Zfinance.Logtime("Start")
app = QApplication([])
ZTimer.Dtime('app')
stats = Stats()
ZTimer.Dtime('stats')
GlobalMainUI = stats.MainUI
FavorEditorUI = ZFavorEditor.FavorEditorUIProc()
DownloadUI = ZfinanceUI_Download.DownloadUIProc(GlobalMainUI,app,FavorEditorUI)

ZTimer.Dtime('dui')
stats.MainUI.show()
ZTimer.Dtime('show')
app.exec_()
