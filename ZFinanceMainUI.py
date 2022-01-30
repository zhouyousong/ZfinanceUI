from PySide2.QtWidgets import QApplication, QMessageBox,QFileDialog
from PySide2.QtUiTools import QUiLoader
import ZfinanceUI_Download
import Zfinance
import ZFavorEditor
import ZBaseFunc
import ZFunAna
import ZBackTestAndMonitor

SortList=['Sector','Ind','State']

class Stats:

    def __init__(self):

        self.MainUI = QUiLoader().load('UIDesign\Zfinance.ui')


ZTimer = Zfinance.Logtime("Start")
app = QApplication([])
ZTimer.Dtime('app')
stats = Stats()
ZTimer.Dtime('stats')
GlobalMainUI = stats.MainUI
stats.MainUI.show()
FavorEditorUI = ZFavorEditor.FavorEditorUIProc()
ZBaseFunc.InitLogBox(GlobalMainUI)

DownloadUI          = ZfinanceUI_Download.DownloadUIProc(GlobalMainUI,app,FavorEditorUI)
FunAnaUI            = ZFunAna.FunAnaProc(GlobalMainUI,app)
BackTestAndMonitorUI    = ZBackTestAndMonitor.BackTestAndMonitorProc(GlobalMainUI,app)



app.exec_()
