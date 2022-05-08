#在列表中显示元素
#删除项目

from PySide2.QtUiTools  import QUiLoader
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import QCursor
from PySide2.QtCharts import QtCharts
from PySide2 import QtWidgets
import numpy,keyboard
import pyecharts.options as opts
from pyecharts.charts import Bar3D

import Zplot
import ZfinanceCfg
import os


import pandas as pd
import ZBaseFunc,ZfinanceCfg,ZFavorEditor
class FunAnaProc:
    def __init__(self,GlobalUI,APP):
        self.GlobalAPP = APP
        self.GlobalMainUI = GlobalUI
        self.SortListDict = dict()
        self.SortListvsCnt = []
        self.SortListvsCnt_IntelRecomd = []
        self.SortListvsCnt_Orginal = []
        self.TickersInfoDataBase = ZBaseFunc.GetTickersInfo()

        self.GlobalMainUI.PreviewLevelNum.setMaximum(10)
        self.GlobalMainUI.PreviewLevelNum.setMinimum(1)

        self.GlobalMainUI.PreviewDensity.setMaximum(20)
        self.GlobalMainUI.PreviewDensity.setMinimum(1)

        self.GlobalMainUI.PreviewPeriod.setMaximum(9)
        self.GlobalMainUI.PreviewPeriod.setMinimum(0)

        self.GlobalMainUI.ValueRatio_PieChart.setContentsMargins(0, 0, 0, 0)
        self.ValueRatio_PieChartLay = QtWidgets.QVBoxLayout(self.GlobalMainUI.ValueRatio_PieChart)
        self.ValueRatio_PieChartLay.setContentsMargins(0, 0, 0, 0)

        self.GlobalMainUI.RaiseRatio_BarChart.setContentsMargins(0, 0, 0, 0)
        self.RaiseRatio_BarChartLay = QtWidgets.QVBoxLayout(self.GlobalMainUI.RaiseRatio_BarChart)
        self.RaiseRatio_BarChartLay.setContentsMargins(0, 0, 0, 0)

        self.GlobalMainUI.MarketCapTrend_LineChart.setContentsMargins(0, 0, 0, 0)
        self.MarketCapTrend_LineChartLay = QtWidgets.QVBoxLayout(self.GlobalMainUI.MarketCapTrend_LineChart)
        self.MarketCapTrend_LineChartLay.setContentsMargins(0, 0, 0, 0)


        self.GlobalMainUI.PreGroup.clicked.connect(self.HandlePreGroup)
        #self.GlobalMainUI.StartSortingAnalyse.clicked.connect(self.HandleStartSortingAnalyse)
        self.GlobalMainUI.FunAnaFilterInput.textChanged.connect(self.HandleInputChanged)

        self.GlobalMainUI.ColumeList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.GlobalMainUI.ColumeList.customContextMenuRequested[QPoint].connect(self.ColumeListMenu)
        self.GlobalMainUI.ColumeList.clicked.connect(self.HandleExplanSorts)


        self.GlobalMainUI.SortingResultTree.setColumnCount(1)
        self.GlobalMainUI.SortingResultTree.setHeaderLabels(['Cluster'],)
        self.GlobalMainUI.SortingResultTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.GlobalMainUI.SortingResultTree.customContextMenuRequested[QPoint].connect(self.SortingResultMenu)
        self.GlobalMainUI.SortingResultTree.clicked.connect(self.HandlePreview)

        self.GlobalMainUI.CompareGroupTree.setColumnCount(len(['Cluster','IPO']))
        self.GlobalMainUI.CompareGroupTree.setHeaderLabels(['Cluster','IPO'])
        self.GlobalMainUI.CompareGroupTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.GlobalMainUI.CompareGroupTree.customContextMenuRequested[QPoint].connect(self.handleCompareClusterMenu)
        #self.GlobalMainUI.CompareGroupTree.clicked.connect(self.HandlePreview)

        self.GlobalMainUI.PreviewLevelNum.sliderReleased.connect(self.HandlePreviewLevelNum)
        self.GlobalMainUI.PreviewLevelNum.valueChanged.connect(self.HandlePreviewLevelNumLabel)
        self.GlobalMainUI.PreviewDensity.sliderReleased.connect(self.HandlePreviewDensity)
        self.GlobalMainUI.PreviewDensity.valueChanged.connect(self.HandlePreviewDensityLabel)
        self.GlobalMainUI.PreviewPeriod.sliderReleased.connect(self.HandlePreviewPeriod)
        self.GlobalMainUI.PreviewPeriod.valueChanged.connect(self.HandlePreviewPeriodLabel)


        self.GlobalMainUI.IntelRecom.clicked.connect(self.HandleIntelligentRecommendation)

        try:
            Temp= pd.read_csv('Data\\03_IntermediateData\TickersInfo.csv',sep=',',index_col='symbol',low_memory=False)
            InfoDataBase = Temp[~numpy.isnan(Temp['sharesOutstanding'])]
            ZBaseFunc.SetTickersInfo(IN=InfoDataBase)
        except:
            ZBaseFunc.Log2LogBox("TickersInfo.csv missing")
        self.ValueRatioPreviewFlag = True
        self.RaiseRatioPreviewFlag = True
        self.MarketCapTrendPreviewFlag = True

        self.GlobalMainUI.PreProcess.clicked.connect(self.HandlePreProcess)

        self.PreProcessUI = QUiLoader().load('UIDesign\PreProcess.ui')
       # self.PreProcessUI.LoadExist.clicked.connect(self.HandleLoadExist)
        self.PreProcessUI.ReloadNew.clicked.connect(self.HandleReloadNew)

        self.DCFavorEditorFavorUI = ZFavorEditor.FavorEditorUIProc()

        self.GlobalAPP = APP
#        self.HandlePreGroup()

    def HandlePreProcess(self):
        self.PreProcessUI.show()
        self.PreProcessUI.PreProcessProgressBar.setValue(0)

    def HandleReloadNew(self):
        global  GlobalAPP
        ZBaseFunc.Log2LogBox('Reload Ticker info Start')
        DataBasePath = os.getcwd() + '\\Data\\01_TickerDatabase'

        InfoDataBase = pd.DataFrame()
        try:
            TickerFolders = os.listdir(DataBasePath)
        except:
            QMessageBox.information(None, "警告", "没有下载好的数据，请先去“数据下载”模块进行数据下载", QMessageBox.Yes,
                                    QMessageBox.Yes)
            os.mkdir(DataBasePath)
            TickerFolders = []
        Mnt = len(TickerFolders)
        if Mnt == 0:
            QMessageBox.information(None, "警告", "没有下载好的数据，请先去“数据下载”模块进行数据下载", QMessageBox.Yes,QMessageBox.Yes)
            self.PreProcessUI.close()
            return
        cnt = 0
        TemplastProgress = 0
        for TickerFolder in TickerFolders:
            cnt += 1
            TempInfPath = DataBasePath+'/'+TickerFolder+'/'+TickerFolder+'_inf.csv'
            FileName = ZBaseFunc.GetCompleteFileName('Data/01_TickerDatabase/' + TickerFolder + '/' + TickerFolder + '_1d')
            if FileName == None:
                StartDate = ''
            else:
                Tempdf = pd.read_csv('Data/01_TickerDatabase/' + TickerFolder + '/' + FileName, sep=',', index_col='DateTime')
                StartDate = Tempdf.index[0]
            try:
                TempInfo = pd.read_csv(TempInfPath,sep=',',index_col='symbol')
                TempInfo['DownloadStartDate'] = StartDate
                InfoDataBase = InfoDataBase.append(TempInfo)
            except:
                pass
            if (cnt/Mnt - TemplastProgress >=0.005):
                TemplastProgress = cnt/Mnt
                self.PreProcessUI.PreProcessProgressBar.setValue(TemplastProgress*100)
                self.GlobalAPP.processEvents()
        InfoDataBase.to_csv('Data\\03_IntermediateData\\TickersInfo.csv',sep=',',index_label='symbol')
        InfoDataBase = InfoDataBase[~numpy.isnan(InfoDataBase['sharesOutstanding'])]
        ZBaseFunc.SetTickersInfo(InfoDataBase)

        ZBaseFunc.SetTickersInfo(IN=InfoDataBase)

        ZBaseFunc.Log2LogBox('Reload Ticker info Finished')
        return

    def HandleIntelligentRecommendation(self):
        if self.GlobalMainUI.IntelRecom.isChecked():
            self.SortListvsCnt = self.SortListvsCnt_IntelRecomd
        else:
            self.SortListvsCnt = self.SortListvsCnt_Orginal
        slm = QStringListModel()
        slm.setStringList(self.SortListvsCnt)
        self.GlobalMainUI.ColumeList.setModel(slm)


    def HandlePreviewLevelNumLabel(self):
        self.GlobalMainUI.LevelLabel.setText('分级: '+ str(self.GlobalMainUI.PreviewLevelNum.value()))
    def HandlePreviewDensityLabel(self):
        self.GlobalMainUI.DensityLabel.setText('颗粒度: '+str(self.GlobalMainUI.PreviewDensity.value()))
    def HandlePreviewPeriodLabel(self):
        if ZfinanceCfg.PreviewPeriodList[self.GlobalMainUI.PreviewPeriod.value()] == -1:
            self.GlobalMainUI.PeriodLabel.setText('周期: Max')
        else:
            self.GlobalMainUI.PeriodLabel.setText('周期: '+str(int(ZfinanceCfg.PreviewPeriodList[self.GlobalMainUI.PreviewPeriod.value()]/5))+' wks')

    def HandlePreviewLevelNum(self):
        self.GlobalMainUI.LevelLabel.setText('分级: '+ str(self.GlobalMainUI.PreviewLevelNum.value()))
        if(self.GlobalMainUI.SortingResultTree.currentItem() != None):
            self.HandlePreview()
    def HandlePreviewDensity(self):
        self.GlobalMainUI.DensityLabel.setText('颗粒度: '+str(self.GlobalMainUI.PreviewDensity.value()))
        if(self.GlobalMainUI.SortingResultTree.currentItem() != None):
            self.HandlePreview()
    def HandlePreviewPeriod(self):
        if ZfinanceCfg.PreviewPeriodList[self.GlobalMainUI.PreviewPeriod.value()] == -1:
            self.GlobalMainUI.PeriodLabel.setText('周期: Max')
        else:
            self.GlobalMainUI.PeriodLabel.setText('周期: '+str(int(ZfinanceCfg.PreviewPeriodList[self.GlobalMainUI.PreviewPeriod.value()]/5))+' wks')

        if(self.GlobalMainUI.SortingResultTree.currentItem() != None):
            self.HandlePreview()


    def HandleRatioPreview(self,TempDataframe=pd.DataFrame()):#Pie
        ZBaseFunc.Log2LogBox('start Draw')
        RootDir = 'Data/01_TickerDatabase/'
        LevelNum = self.GlobalMainUI.PreviewLevelNum.value()
        EarlyDaysNum = ZfinanceCfg.PreviewPeriodList[self.GlobalMainUI.PreviewPeriod.value()]
        LastLevelNum = 0
        if len(TempDataframe)<=LevelNum:
            LevelNum = len(TempDataframe)
            PerLevelNum = 1
        else:
            PerLevelNum = int(len(TempDataframe)/LevelNum)
            if(PerLevelNum == 0):
                LevelNum = 1
                PerLevelNum = len(TempDataframe)
            else:
                LastLevelNum = int(len(TempDataframe)-PerLevelNum*LevelNum)
                if(LastLevelNum != 0):
                    LevelNum +=1

        Temp = TempDataframe.sort_values('marketCap', ascending=False)

        TickerListSortByMartetvalue = Temp.index.tolist()
        TickerLevelGroup = dict()
        if (LastLevelNum != 0):
            for i in range(LevelNum-1):
                templist=[]
                for j in range(PerLevelNum):
                    templist.append(TickerListSortByMartetvalue.pop(0))
                TickerLevelGroup['Level'+str(i+1)] = templist
            TickerLevelGroup['LevelLast'] = TickerListSortByMartetvalue
        else:
            for i in range(LevelNum):
                templist=[]
                for j in range(PerLevelNum):
                    templist.append(TickerListSortByMartetvalue.pop(0))
                TickerLevelGroup['Level'+str(i+1)] = templist
        TickerLevelGroupMarketCap=dict()
        TotalSum_Now = 0
        TotalSum_Early = 0
        TempCnt = 0
        ProcessCntSum = len(Temp.index)
        ##############################################加载到内存########################
        LevelDataframeDict = dict()
        MinLastDay = 99999999
        for Key, Value in TickerLevelGroup.items():
            TempLevelDF = pd.DataFrame()
            MaxLen = 0
            for i in Value:
                FileName_1d = ZBaseFunc.GetCompleteFileName(RootDir+'/'+i+'/'+i+'_1d_')
                if(FileName_1d == None):
                    continue

                TempDF = pd.read_csv(RootDir+'/'+i+'/'+FileName_1d,index_col='DateTime')
                LastDay = int(FileName_1d.split('_')[3])
                if(LastDay<MinLastDay):
                    MinLastDay = LastDay
                    LastDayIndex = TempDF.index[-1]
                if(len(TempDF)>MaxLen):
                    TempLevelDF = TempLevelDF.reindex(TempDF.index.tolist())
                    MaxLen = len(TempDF)
                TempLevelDF[i+'_Close'] = TempDF['Close']
                TempCnt+=1
                self.GlobalMainUI.FunAnaGroupProgressBar.setValue(TempCnt / ProcessCntSum * 100)
                self.GlobalAPP.processEvents()
            LevelDataframeDict[Key] = TempLevelDF

        self.GlobalMainUI.FunAnaGroupProgressBar.setValue(100)
        self.GlobalAPP.processEvents()

        TempDFlist=[]
        for Key, Value in LevelDataframeDict.items():
            Sum_Now = 0
            Sum_Early = 0
            for i in TickerLevelGroup[Key]:
                Shareamount= TempDataframe.loc[i, 'sharesOutstanding']
                try:
                    TempClosePrice = Value[i+'_Close']
                except:
                    continue

                TempClosePrice.dropna(inplace=True)
                MarketCap_Now = TempClosePrice.iloc[-1] * Shareamount
                if (len(TempClosePrice) <= EarlyDaysNum-1) or EarlyDaysNum == -1:
                    MarketCap_Early = TempClosePrice.iloc[0] * Shareamount
                else:
                    MarketCap_Early = TempClosePrice.iloc[-EarlyDaysNum] * Shareamount


                Sum_Now = Sum_Now + MarketCap_Now
                Sum_Early = Sum_Early + MarketCap_Early
            TickerLevelGroupMarketCap[Key] = [Sum_Now, Sum_Early]
            TotalSum_Now = TotalSum_Now + Sum_Now
            TotalSum_Early = TotalSum_Early + Sum_Early
            TempDFlist.append(Value)

        TempGroupDataframe = pd.concat(TempDFlist,axis=1)
        TempGroupDataframe = TempGroupDataframe[:LastDayIndex]
        Density = self.GlobalMainUI.PreviewDensity.value()
        TempIndex = []
        TempGroupDataframe = TempGroupDataframe.iloc[-(EarlyDaysNum+1):-1]
        for i in range(0,len(TempGroupDataframe),Density):
            TempIndex.append(i)
        TempGroupDataframe = pd.DataFrame(TempGroupDataframe.iloc[TempIndex]).fillna(0)
        TempGroupDataframe_MC = pd.DataFrame()
        for i in TempGroupDataframe.columns.values.tolist():
            Ticker = i.split('_')[0]
            TempGroupDataframe_MC[Ticker+'_MarketCap'] = TempGroupDataframe[Ticker+'_Close']*TempDataframe.loc[Ticker, 'sharesOutstanding']/1000000000
        TempGroupDataframe_MC['MarketCap_sum'] = TempGroupDataframe_MC.apply(lambda x: x.sum(), axis=1)

        Lines = dict()
        self.MarkerCapRatioPreview(TickerLevelGroupMarketCap,TotalSum_Now)
        self.RaiseRatioPreview(TickerLevelGroupMarketCap)
        Lines['sum'] = TempGroupDataframe_MC['MarketCap_sum'].tolist()
        self.MarketcapSumTrendPreview(Lines)

        ZBaseFunc.Log2LogBox('end Draw')
    def MarkerCapRatioPreview(self, TickerLevelGroupMarketCap=dict(),TotalSum_Now = None):

        if self.ValueRatioPreviewFlag == False:
            self.ValueRatio_PieChartLay.removeWidget(self.ValueRatio_PieChartView)
        pieseries = QtCharts.QPieSeries()

        for Key, Value in TickerLevelGroupMarketCap.items():
            pieseries.append(Key,Value[0]/TotalSum_Now)

        pieseries.setPieSize(2.5)
        chart = QtCharts.QChart()
        chart.setTitle("MarketCap Ratio")
        chart.addSeries(pieseries)
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        chart.legend().hide()
        #############################################
        self.ValueRatio_PieChartView = QtCharts.QChartView(chart, self.GlobalMainUI)
        self.ValueRatio_PieChartView.setContentsMargins(0, 0, 0, 0)
        self.ValueRatio_PieChartLay.addWidget(self.ValueRatio_PieChartView)
        self.ValueRatio_PieChartView.setGeometry(0, 0, self.GlobalMainUI.width(), self.GlobalMainUI.height())

        self.ValueRatioPreviewFlag = False

    def RaiseRatioPreview(self, TickerLevelGroupMarketCap=dict()):

        if self.RaiseRatioPreviewFlag == False:
            self.RaiseRatio_BarChartLay.removeWidget(self.RaiseRatio_BarChartView)

        # we want to create percent bar series
        barseries = QtCharts.QBarSeries()
        Max = 0
        for Key, Value in TickerLevelGroupMarketCap.items():
            TempLevel = QtCharts.QBarSet(Key)
            RaiseRate = Value[0]/Value[1]
            TempLevel.append(RaiseRate)
            barseries.append(TempLevel)
            if (RaiseRate>Max):
                Max = RaiseRate

        chart = QtCharts.QChart()
        chart.addSeries(barseries)
        chart.setTitle("Raise Ratio")
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        # chart.setTheme(QtCharts.QChart.ChartThemeDark)

        axisX = QtCharts.QValueAxis()
        axisX.setRange(-0.25, 0.25)
        chart.setAxisX(axisX, barseries)

        axisY = QtCharts.QValueAxis()
        axisY.setRange(0, int(Max)+1)
        chart.setAxisY(axisY, barseries)
        #chart.removeAxis(axisY)
        chart.removeAxis(axisX)

        #        chart.createDefaultAxes()
        chart.legend().setVisible(False)

        # create chartview and add the chart in the chartview
        self.RaiseRatio_BarChartView = QtCharts.QChartView(chart, self.GlobalMainUI)
        self.RaiseRatio_BarChartView.setContentsMargins(0, 0, 0, 0)
        self.RaiseRatio_BarChartLay.addWidget(self.RaiseRatio_BarChartView)
        self.RaiseRatio_BarChartView.setGeometry(0, 0, self.GlobalMainUI.width(), self.GlobalMainUI.height())

        self.RaiseRatioPreviewFlag = False
    def MarketcapSumTrendPreview(self,Lines=dict()):#Line
        if self.MarketCapTrendPreviewFlag == False:
            self.MarketCapTrend_LineChartLay.removeWidget(self.MarketCapTrend_LineChartView)
        MaxMarketcapSum = max(Lines['sum'])
        MinMarketcapSum = min(Lines['sum'])
        MarketcapSumLen = len(Lines['sum'])
        chart = QtCharts.QChart()
        Lineseries = QtCharts.QLineSeries()

        chart.addSeries(Lineseries)

        dtaxisX = QtCharts.QValueAxis()
        vlaxisY = QtCharts.QValueAxis()
        #设置坐标轴显示范围
        dtaxisX.setMin(0)
        dtaxisX.setMax(MarketcapSumLen)
        vlaxisY.setMin(MinMarketcapSum)
        vlaxisY.setMax(MaxMarketcapSum)
        chart.setTitle("MarketCap : B$")
        # self.dtaxisX.setTickCount(6)
        # self.vlaxisY.setTickCount(11)

        #设置网格不显示
        vlaxisY.setGridLineVisible(True)
        #把坐标轴添加到chart中
        chart.addAxis(dtaxisX,Qt.AlignBottom)
        chart.addAxis(vlaxisY,Qt.AlignLeft)
        #把曲线关联到坐标轴
        Lineseries.attachAxis(dtaxisX)
        Lineseries.attachAxis(vlaxisY)
        chart.removeAxis(dtaxisX)
        #self.chart.removeAxis(self.vlaxisY)
        chart.legend().hide()
        #self.setChart(self.chart)

        x = 0
        for i in Lines['sum']:
            Lineseries.append(x ,i)
            x += 1

        self.MarketCapTrend_LineChartView = QtCharts.QChartView(chart, self.GlobalMainUI)
        self.MarketCapTrend_LineChartView.setContentsMargins(0, 0, 0, 0)
        self.MarketCapTrend_LineChartLay.addWidget(self.MarketCapTrend_LineChartView)
        self.MarketCapTrend_LineChartView.setGeometry(0, 0, self.GlobalMainUI.width(), self.GlobalMainUI.height())

        self.MarketCapTrendPreviewFlag = False
        return
    def HandlePreview(self):

        TempDataframe = self.TickersInfoDataBase
        TempLink = self.GlobalMainUI.SortingResultTree.currentItem()
        if TempLink.parent() == None:
            return
        LinkCol = [TempLink.text(0)]
        while TempLink.parent() != None:
            TempLink = TempLink.parent()
            LinkCol.insert(0, TempLink.text(0))
        print(LinkCol)
        t = 0
        for i in range(len(LinkCol) - 2):
            t += 1
            Cluster = LinkCol[i].split(':')[1]
            ClusterMember = LinkCol[i + 1].split('[')[0]
            TempDataframe = TempDataframe[TempDataframe[Cluster].isin([ClusterMember])]
        Cluster = LinkCol[t].split(':')[1]
        ClusterMember = self.GlobalMainUI.SortingResultTree.currentItem().text(0).split('[')[0]
        TempDataframe = TempDataframe[TempDataframe[Cluster].isin([ClusterMember])]

        TickerList = []
        for i in TempDataframe.index.tolist():
            TickerList.append(i+':'+str(TempDataframe.loc[i,'shortName']))
        if TickerList == []:
            return
        Temp = QStringListModel()
        Temp.setStringList(TickerList)
        self.GlobalMainUI.GroupList.setModel(Temp)

        if self.GlobalMainUI.RatioPreview.isChecked() :
            self.HandleRatioPreview(TempDataframe)

    def HandlePreGroup(self):

        self.TickersInfoDataBase = ZBaseFunc.GetTickersInfo()
        if self.TickersInfoDataBase ==None:
            QMessageBox.information(None, "警告", "没有找到预处理好的数据，请先“导入数据”", QMessageBox.Yes,
                                    QMessageBox.Yes)
            return
        SortList = self.TickersInfoDataBase.columns.values.tolist()
        TotalTickerNum = len(self.TickersInfoDataBase)
        ProcessCntSum = len(SortList)*2
        SortListDict=dict()
        TempCnt = 0
        for Sort_i in SortList:
            SortListDict[Sort_i] = len(self.TickersInfoDataBase.groupby(Sort_i).count())
            TempCnt += 1
            self.GlobalMainUI.FunAnaGroupProgressBar.setValue(TempCnt/ProcessCntSum*100)
            self.GlobalAPP.processEvents()
            SortListvsNum= sorted(SortListDict.items(), key=lambda item: item[1], reverse=False)

        self.SortListvsCnt_Orginal=[]
        self.SortListvsCnt_IntelRecomd = []
        SortListvsCnt_ReC = []
        SortListvsCnt_ReO = []

        for SortListDict_i in SortListvsNum:
            ClusterGroupNum = SortListDict_i[1]
            ClusterAvailableDataNum = len(self.TickersInfoDataBase[SortListDict_i[0]].dropna())
            self.SortListDict[SortListDict_i[0]] = self.TickersInfoDataBase.groupby(SortListDict_i[0]).count().index.tolist()
            Sign = 'X'
            if ClusterAvailableDataNum  >0.75*TotalTickerNum and \
                ClusterGroupNum <0.3 *TotalTickerNum and\
                ClusterGroupNum>=6 and \
                type(self.TickersInfoDataBase[SortListDict_i[0]].iloc[0]) == type('numpy.float64(0)'):

                Sign = 'C'
                SortListvsCnt_ReC.append('[' + str(SortListDict_i[1]) + '/' + str(
                    len(self.TickersInfoDataBase[SortListDict_i[0]].dropna())) + '/' + Sign + ']:' + SortListDict_i[0])

            if ClusterAvailableDataNum >0.9*TotalTickerNum and \
                    ClusterGroupNum >0.6*TotalTickerNum and \
                    type(self.TickersInfoDataBase[SortListDict_i[0]].iloc[0]) != type('numpy.float64(0)'):
                Sign = 'O'
                SortListvsCnt_ReO.append('[' + str(SortListDict_i[1]) + '/' + str(
                    len(self.TickersInfoDataBase[SortListDict_i[0]].dropna())) + '/' + Sign + ']:' + SortListDict_i[0])
            self.SortListvsCnt_Orginal.append('['+str(SortListDict_i[1])+'/'+str(len(self.TickersInfoDataBase[SortListDict_i[0]].dropna()))  +'/'+Sign+']:'+SortListDict_i[0])
            TempCnt += 1
            self.GlobalMainUI.FunAnaGroupProgressBar.setValue(TempCnt / ProcessCntSum * 100)
            self.GlobalAPP.processEvents()
        self.SortListvsCnt_IntelRecomd = SortListvsCnt_ReC+SortListvsCnt_ReO

        if self.GlobalMainUI.IntelRecom.isChecked():
            self.SortListvsCnt = self.SortListvsCnt_IntelRecomd
        else:
            self.SortListvsCnt = self.SortListvsCnt_Orginal
        slm = QStringListModel()
        slm.setStringList(self.SortListvsCnt)
        self.GlobalMainUI.ColumeList.setModel(slm)


    def HandleInputChanged(self):

        VagueText = self.GlobalMainUI.FunAnaFilterInput.text()

        slm = QStringListModel()
        self.FliteredList=list(filter(lambda x: VagueText in x, self.SortListvsCnt))
        slm.setStringList(self.FliteredList)
        self.GlobalMainUI.ColumeList.setModel(slm)


    def HandleExplanSorts(self,index):
        self.GlobalMainUI.ColumeList.selectionModel().selectedIndexes()[0].data()
        SelectedCol = self.GlobalMainUI.ColumeList.selectionModel().selectedIndexes()[0].data().split(':')[1]

        Temp = QStringListModel()
        Temp.setStringList(str(x) for x in self.SortListDict[SelectedCol])
        self.GlobalMainUI.GroupList.setModel(Temp)
        print(index)

    def EventRank(self,Tree = None):
        TempCol = Tree.currentColumn()

        cursor = QTreeWidgetItemIterator(Tree)
        while cursor.value():
            TempStr = ZBaseFunc.SortTrick(cursor.value().text(TempCol))
            cursor.value().setText(TempCol,TempStr)
            cursor = cursor.__iadd__(1)

        Tree.setSortingEnabled(True)
        Tree.sortByColumn(Tree.currentColumn(),)

        Tree.setSortingEnabled(False)
        cursor = QTreeWidgetItemIterator(Tree)
        while cursor.value():
            TempStr = cursor.value().text(TempCol)
            try:
                TempStr = TempStr.split('*')[1]
            except:
                try:
                    TempStr = '-'+TempStr.split('-')[1]
                except:
                    pass
            cursor.value().setText(TempCol,TempStr)
            cursor = cursor.__iadd__(1)

    def EventDeleteZero(self):
        cursor = QTreeWidgetItemIterator(self.GlobalMainUI.SortingResultTree)
        DeleteList = []
        while cursor.value():
            if('[0]' in cursor.value().text(0) ):
                DeleteList.insert(0,cursor.value())
            cursor = cursor.__iadd__(1)
        for i in DeleteList:
            i.parent().removeChild(i)

        print(self.GlobalMainUI.SortingResultTree.currentColumn())

    def EventDeleteOp(self):
        if self.GlobalMainUI.SortingResultTree.currentColumn() == 0:
            return
        HeaderLabel = []
        for i in range(self.GlobalMainUI.SortingResultTree.columnCount()):
            HeaderLabel.append(self.GlobalMainUI.SortingResultTree.headerItem().text(i))
        HeaderLabel.pop(self.GlobalMainUI.SortingResultTree.currentColumn())
        self.GlobalMainUI.SortingResultTree.setColumnCount(len(HeaderLabel))
        self.GlobalMainUI.SortingResultTree.setHeaderLabels((HeaderLabel))
        print(self.GlobalMainUI.SortingResultTree.currentColumn())
    def EventDeleteFatherLevel(self):
        print(self.GlobalMainUI.SortingResultTree.currentItem().text(0))
    def EventDeleteThisItem(self,Tree = None):

        currNode = Tree.currentItem()
        TempParent = currNode.parent()
        if TempParent == None:
            Tree.takeTopLevelItem(Tree.indexOfTopLevelItem(currNode))
        else:
            TempParent.removeChild(currNode)

    def EventAddToCompare(self):
        IterationNode = currNode = self.GlobalMainUI.SortingResultTree.currentItem()
        TempParent = currNode.parent()

        if TempParent != None:
            TempStr = []
            while IterationNode.parent() !=None:
                TempStr.insert(0,IterationNode.text(0))
                IterationNode = IterationNode.parent()
            CompareClusterName = IterationNode.text(0).split(':')[1]
            for i in TempStr:
                CompareClusterName = CompareClusterName+':'+i.split('[')[0]

            root = QTreeWidgetItem(self.GlobalMainUI.CompareGroupTree)
            root.setText(0, CompareClusterName)
            for i in range(2,self.GlobalMainUI.CompareGroupTree.columnCount()):
                root.setCheckState(i, Qt.Checked)
            model = self.GlobalMainUI.GroupList.model()
            ProcessCntSum = model.rowCount()

            TempCnt = 0
            for row  in range(model.rowCount()):
                index  = model.index(row, 0)
                item = model.data(index, Qt.DisplayRole)
                Ticker = item.split(':')[0]

                StartDate = self.TickersInfoDataBase.loc[Ticker, 'DownloadStartDate'].replace('-','')
                child = QTreeWidgetItem(root)
                child.setText(0, Ticker)
                child.setText(1, StartDate)
                TempCnt += 1
                self.GlobalMainUI.FunAnaGroupProgressBar.setValue(TempCnt / ProcessCntSum * 100)
                self.GlobalAPP.processEvents()

        pass
    def EventAddToFavorList(self):
        IterationNode = currNode = self.GlobalMainUI.SortingResultTree.currentItem()
        TempParent = currNode.parent()

        if TempParent != None:
            TempStr = []
            while IterationNode.parent() !=None:
                TempStr.insert(0,IterationNode.text(0))
                IterationNode = IterationNode.parent()
            NewAddFavorName = IterationNode.text(0).split(':')[1]
            for i in TempStr:
                NewAddFavorName = NewAddFavorName+':'+i.split('[')[0]
            model = self.GlobalMainUI.GroupList.model()
            TempList = []
            for row  in range(model.rowCount()):
                index  = model.index(row, 0)
                item = model.data(index, Qt.DisplayRole)
                TempList.append(item.split(':')[0])
        self.DCFavorEditorFavorUI.handleFavorEditor(SelectList=TempList, NewClass=NewAddFavorName)

        pass

    def handleCompareClusterMenu(self):
        popMenu = QMenu()
        if self.GlobalMainUI.CompareGroupTree.currentColumn() == 0:
            DeleteThisItem = popMenu.addAction('删除该项')
            DeleteThisItem.triggered.connect(lambda :self.EventDeleteThisItem(self.GlobalMainUI.CompareGroupTree))
            LoadRawData = popMenu.addAction('加载所有列数据')
            LoadRawData.triggered.connect(self.EventLoadRawData)
        elif self.GlobalMainUI.CompareGroupTree.currentColumn() == 1:
            Rank = popMenu.addAction('上市时间排序')
            Rank.triggered.connect(lambda :self.EventRank(self.GlobalMainUI.CompareGroupTree))
            # OutputInPlotly = popMenu.addAction('出图')
            # OutputInPlotly.triggered.connect(self.HandleOutputInPlotly)
        else:
            DeleteEmptyTicker = popMenu.addAction('删除本列为空的Ticker')
#            DeleteEmptyTicker.triggered.connect(self.EventDeleteEmptyTicker)
            Rank = popMenu.addAction('从大到小排序')
            Rank.triggered.connect(lambda: self.EventRank(self.GlobalMainUI.CompareGroupTree))
        #   DeleteEmptyTicker.triggered.connect(self.EventDeleteEmptyTicker)


        popMenu.exec_(QCursor.pos())
        pass
    def SortingResultMenu(self, point):

        self.HandlePreview()
        popMenu = QMenu()
        if self.GlobalMainUI.SortingResultTree.currentColumn() == 0:
            DeleteThisItem = popMenu.addAction('删除该项')
            DeleteThisItem.triggered.connect(lambda :self.EventDeleteThisItem(self.GlobalMainUI.SortingResultTree))
            DeleteZero = popMenu.addAction('删除0项')
            DeleteZero.triggered.connect(self.EventDeleteZero)
            AnaCalc = popMenu.addAction('分析计算')
            AnaCalc.triggered.connect(self.HandleStartSortingAnalyse)
            AddToCompare = popMenu.addAction('添加到比较')
            AddToCompare.triggered.connect(self.EventAddToCompare)
            AddToFavorList = popMenu.addAction('添加到喜好列表')
            AddToFavorList.triggered.connect(self.EventAddToFavorList)
        else:
            Rank = popMenu.addAction("从大小排序")
            Rank.triggered.connect(lambda :self.EventRank(self.GlobalMainUI.SortingResultTree))
            DeleteOp = popMenu.addAction('删除算子')
            DeleteOp.triggered.connect(self.EventDeleteOp)
            DrawInWebbrowser = popMenu.addAction('浏览器出图')
            DrawInWebbrowser.triggered.connect(self.EventDrawInWebbrowser)

        popMenu.exec_(QCursor.pos())

    def EventDrawInWebbrowser(self):
        ChildCnt = self.GlobalMainUI.SortingResultTree.currentItem().childCount()
        if ChildCnt == 0:
            ZBaseFunc.Log2LogBox('iChildCnt = 0')
            return
        ResultList = []
        PlotItem={'Count':[]}
        for i in range(1, self.GlobalMainUI.SortingResultTree.columnCount()):
            ItemStr = self.GlobalMainUI.SortingResultTree.headerItem().text(i).replace('\n', ' ')
            PlotItem[ItemStr]=[]

        for i in range(ChildCnt):
            iChild = self.GlobalMainUI.SortingResultTree.currentItem().child(i)
            iChildCnt = iChild.childCount()
            XaxisLabel = iChild.text(0).split('[')[0]
            for j in range(iChildCnt):
                jChild = iChild.child(j)
                YaxisLabel = jChild.text(0).split('[')[0]
                for k in range(0,self.GlobalMainUI.SortingResultTree.columnCount()):
                    if k == 0:
                        TempVal = int(iChild.child(j).text(0).split('[')[1].split(']')[0])
                        ItemStr = 'Count'
                    else:
                        TempVal = float(iChild.child(j).text(k))
                        ItemStr = self.GlobalMainUI.SortingResultTree.headerItem().text(k).replace('\n',' ')
                    PlotItem[ItemStr].append([XaxisLabel,YaxisLabel,TempVal])


        Zplot.ZBar3D(PlotItem)

        return
        XAxisList = []
        YAxisList = []
        for i in ResultList:
            if not i[0] in XAxisList:
                XAxisList.append(i[0])
            if not i[1] in YAxisList:
                YAxisList.append(i[1])

        Bar1 = (
            Bar3D(init_opts=opts.InitOpts(width='960px', height='720px'))
                .add(
                series_name='bbb',
                data=ResultList,
                xaxis3d_opts=opts.Axis3DOpts(type_='category', data=XAxisList),
                yaxis3d_opts=opts.Axis3DOpts(type_='category', data=YAxisList),
                zaxis3d_opts=opts.Axis3DOpts(type_='value'),
                grid3d_opts=opts.Grid3DOpts(width=len(XAxisList)*6, height=100, depth=len(YAxisList)*6),

            )
                .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(
                    max_=1000000000000,
                    range_color=[
                        '#313695',
                        '#4575b4',
                        '#74add1',
                        '#abd9e9',
                        '#e0f3f8',
                        '#ffffbf',
                        '#fee090',
                        '#fdae61',
                        '#f46d43',
                        '#d73027',
                        '#a50026',
                    ],
                )
            )
        )
        Bar2 =(
            Bar3D(init_opts=opts.InitOpts(width='960px', height='720px'))
                .add(
                series_name='aaa',
                data=ResultList,

                xaxis3d_opts=opts.Axis3DOpts(type_='category', data=XAxisList),
                yaxis3d_opts=opts.Axis3DOpts(type_='category', data=YAxisList),
                zaxis3d_opts=opts.Axis3DOpts(type_='value'),
                grid3d_opts=opts.Grid3DOpts(width=len(XAxisList) * 6, height=100, depth=len(YAxisList) * 6),
            )
                .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(
                    max_=1000000000000,
                    range_color=[
                        '#313695',
                        '#4575b4',
                        '#74add1',
                        '#abd9e9',
                        '#e0f3f8',
                        '#ffffbf',
                        '#fee090',
                        '#fdae61',
                        '#f46d43',
                        '#d73027',
                        '#a50026',
                    ],
                )
            )
        )
        from pyecharts.charts import Bar, Geo, Grid,Page
        page = Page()
        page.add(
            Bar1(),
            Bar2(),
        )
        page.render("page_default_layout.html")





    def ColumeListMenu(self, point):

        popMenu = QMenu()
        try:
            self.record = self.GlobalMainUI.ColumeList.selectionModel().selectedIndexes()[0]
        except:
            pass
        SelectedColNumInfo = self.record.data().split(':')[0]
        SelectedColNumKey = self.record.data().split(':')[1]

        if keyboard.is_pressed('ctrl'):
            Compare_SUM           = popMenu.addAction("求总值")
            Compare_AVG           = popMenu.addAction('求平均值')
            Compare_SUMvsxShare   = popMenu.addAction('求总股本积和')
            Compare_AVGvsxShare   = popMenu.addAction('求总股本积平均')
            Compare_SUMperShare   = popMenu.addAction('每股平摊总值')
            Compare_AVGperShare   = popMenu.addAction('每股平摊均值')
            Compare_SUM.triggered.connect(lambda :self.AddCompareValue('∑X\n'+SelectedColNumKey))
            Compare_AVG.triggered.connect(lambda :self.AddCompareValue('(∑X)/n\n'+SelectedColNumKey))
            Compare_SUMvsxShare.triggered.connect(lambda :self.AddCompareValue('∑(Share*X)\n'+SelectedColNumKey))
            Compare_AVGvsxShare.triggered.connect(lambda :self.AddCompareValue('∑(Share*X)/n\n'+SelectedColNumKey))
            Compare_SUMperShare.triggered.connect(lambda :self.AddCompareValue('∑(X/Share)\n'+SelectedColNumKey))
            Compare_AVGperShare.triggered.connect(lambda :self.AddCompareValue('∑(X/Share)/n\n'+SelectedColNumKey))

        else:
            if SelectedColNumInfo.split('/')[2] =='O]':
                Operator = popMenu.addMenu('添加算子')
                AddOpSum = Operator.addAction('求和')
                AddOpAverage = Operator.addAction('求均值')
                AddCluster = popMenu.addAction("添加分类项")
            else:
                AddCluster = popMenu.addAction("添加分类项")
                Operator = popMenu.addMenu('添加算子')
                AddOpSum = Operator.addAction('求和')
                AddOpAverage = Operator.addAction('求均值')
            AddCluster.triggered.connect(self.EventAddCluster)
            AddOpSum.triggered.connect(self.EventAddOpSum)
            AddOpAverage.triggered.connect(self.EventAddOpAverage)

        popMenu.exec_(QCursor.pos())
        return

    def EventLoadRawData(self):
        cursor = QTreeWidgetItemIterator(self.GlobalMainUI.CompareGroupTree)
        while cursor.value():
            TempChild = cursor.value()
            if TempChild.parent() != None:
                for i in range(2,self.GlobalMainUI.CompareGroupTree.columnCount()):
                    ColIndex = self.GlobalMainUI.CompareGroupTree.headerItem().text(i).split('\n')[1]
                    Value = self.TickersInfoDataBase.loc[TempChild.text(0),ColIndex]
                    TempChild.setText(i, str(Value))
            cursor = cursor.__iadd__(1)


        pass
    def EventAddCluster(self):

        SelectedCol = self.GlobalMainUI.ColumeList.selectionModel().selectedIndexes()[0].data().split(':')[1]
        TempDataframe = self.TickersInfoDataBase
        if(self.GlobalMainUI.SortingResultTree.currentIndex().parent().row() == -1):
            root = QTreeWidgetItem(self.GlobalMainUI.SortingResultTree)
            for i in self.SortListDict[SelectedCol]:
                Num = len(TempDataframe[TempDataframe[SelectedCol].isin([i])])
                Temp=str(i)+'['+str(Num)+']'
                child = QTreeWidgetItem(root)
                child.setText(0, Temp)
            root.setText(0, 'INFO:'+SelectedCol)
        else:
            if self.GlobalMainUI.SortingResultTree.currentItem().childCount() != 0:
                return
            TempLink = self.GlobalMainUI.SortingResultTree.currentItem()
            LinkCol = [TempLink.text(0)]
            while TempLink.parent() != None:
                TempLink = TempLink.parent()
                LinkCol.insert(0,TempLink.text(0))
            t= 0
            for i in range(len(LinkCol)-2):
                t+=1
                Cluster = LinkCol[i].split(':')[1]
                ClusterMember = LinkCol[i+1].split('[')[0]
                TempDataframe = TempDataframe[TempDataframe[Cluster].isin([ClusterMember])]
            Cluster = LinkCol[t].split(':')[1]

            cursor = QTreeWidgetItemIterator(self.GlobalMainUI.SortingResultTree.currentItem().parent())
            ChildCnt = cursor.value().childCount()
            cursor = cursor.__iadd__(1)

            TempCnt = 0
            ProcessCntSum = ChildCnt
            for i in range(ChildCnt):
                TempRoot = cursor.value()
                TempRootName = TempRoot.text(0)+':'+SelectedCol
                ClusterMember =TempRoot.text(0).split('[')[0]
                TempDataframex = TempDataframe[TempDataframe[Cluster].isin([ClusterMember])]
                TempRoot.setText(0,TempRootName)
                cursor = cursor.__iadd__(1)
                for j in self.SortListDict[SelectedCol]:
                    Num = len(TempDataframex[TempDataframex[SelectedCol].isin([j])])
                    Temp = str(j) + '[' + str(Num) + ']'
                    child = QTreeWidgetItem(TempRoot)
                    child.setText(0, Temp)
                TempCnt+=1
                self.GlobalMainUI.FunAnaGroupProgressBar.setValue(TempCnt / ProcessCntSum * 100)
                self.GlobalAPP.processEvents()

            print('not root')

        pass

    def AddCompareValue(self,SelectedCluster = None):
        HeaderLabel = []
        Temp = SelectedCluster
        for i in range(self.GlobalMainUI.CompareGroupTree.columnCount()):
            HeaderLabel.append(self.GlobalMainUI.CompareGroupTree.headerItem().text(i))
            if self.GlobalMainUI.CompareGroupTree.headerItem().text(i) == Temp:
                return
        HeaderLabel.append(Temp)
        self.GlobalMainUI.CompareGroupTree.setColumnCount(len(HeaderLabel))
        self.GlobalMainUI.CompareGroupTree.setHeaderLabels((HeaderLabel))

        cursor = QTreeWidgetItemIterator(self.GlobalMainUI.CompareGroupTree)
        while cursor.value():
            if cursor.value().parent() == None:
                cursor.value().setCheckState(i+1, Qt.Checked)
            cursor = cursor.__iadd__(1)




    def EventAddOpSum(self):
        HeaderLabel = []
        SelectedCluster = self.GlobalMainUI.ColumeList.selectionModel().selectedIndexes()[0].data().split(':')[1]
        Temp = SelectedCluster + '\n--SUM'
        for i in range(self.GlobalMainUI.SortingResultTree.columnCount()):
            HeaderLabel.append(self.GlobalMainUI.SortingResultTree.headerItem().text(i))
            if self.GlobalMainUI.SortingResultTree.headerItem().text(i) == Temp:
                return
        HeaderLabel.append(Temp)
        self.GlobalMainUI.SortingResultTree.setColumnCount(len(HeaderLabel))
        self.GlobalMainUI.SortingResultTree.setHeaderLabels((HeaderLabel))

    def EventAddOpAverage(self):
        HeaderLabel = []
        SelectedCluster = self.GlobalMainUI.ColumeList.selectionModel().selectedIndexes()[0].data().split(':')[1]
        Temp = SelectedCluster + '\n--AVG'
        for i in range(self.GlobalMainUI.SortingResultTree.columnCount()):
            HeaderLabel.append(self.GlobalMainUI.SortingResultTree.headerItem().text(i))
            if self.GlobalMainUI.SortingResultTree.headerItem().text(i) == Temp:
                return
        HeaderLabel.append(Temp)
        self.GlobalMainUI.SortingResultTree.setColumnCount(len(HeaderLabel))
        self.GlobalMainUI.SortingResultTree.setHeaderLabels((HeaderLabel))
        pass
    def HandleStartSortingAnalyse(self):
        OperatorList = []
        self.GlobalMainUI.SortingResultTree.setSortingEnabled(False)
        for i in range(1,self.GlobalMainUI.SortingResultTree.columnCount()):
            OperatorList.append({'col':self.GlobalMainUI.SortingResultTree.headerItem().text(i).split('\n--')[0],
                                'Op':self.GlobalMainUI.SortingResultTree.headerItem().text(i).split('\n--')[1]})
        cursor = QTreeWidgetItemIterator(self.GlobalMainUI.SortingResultTree)
        ProcessCntSum = 0
        rootcnt = 0

        while cursor.value():
            cursor = cursor.__iadd__(1)
            ProcessCntSum +=1

        cursor = QTreeWidgetItemIterator(self.GlobalMainUI.SortingResultTree)
        ProcessCnt = 0
        while cursor.value():
            Temp = cursor.value()
            TempDataframe = self.TickersInfoDataBase
            TempChild = Temp
            if(Temp.parent() != None):
                while Temp.parent() != None:
                    Cluster = Temp.parent().text(0).split(':')[1]
                    ClusterMember = Temp.text(0).split('[')[0]
                    TempDataframe = TempDataframe[TempDataframe[Cluster].isin([ClusterMember])]
                    Temp = Temp.parent()
            Tempcnt = 1
            for i in OperatorList:
                if(i['Op'] == 'SUM'):
                    TempResult = round(TempDataframe[i['col']].sum(),4)
                if (i['Op'] == 'AVG'):
                    if len(TempDataframe) == 0:
                        TempResult = 'NA'
                    else:
                        TempResult = round(TempDataframe[i['col']].sum()/len(TempDataframe),4)
                TempChild.setText(Tempcnt,str(TempResult))
                Tempcnt+=1
            cursor = cursor.__iadd__(1)
            ProcessCnt +=1
            self.GlobalMainUI.FunAnaGroupProgressBar.setValue(ProcessCnt / ProcessCntSum * 100)
            self.GlobalAPP.processEvents()
        return

    def HandleShowSortInPlotly(self):
        return