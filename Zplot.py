import os

import plotly,ZBaseFunc
import pandas as pd
import plotly.offline as of
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
import plotly.subplots as sp
# import dash_core_components as dcc
# import dash_html_components as html
# import dash
import pyecharts.options as opts
from pyecharts.charts import Bar3D,Bar,Grid, Line, Scatter,Page,Kline
from pyecharts.options.global_options import ThemeType
from pyecharts import options as opts
from pyecharts.faker import Faker
import webbrowser
from pyecharts import options as opts
import webbrowser
import ZfinanceCfg


# ZBar
#     |--DownloadHistoryData 一个dataframe，多个Y列对一个X列，染色，按照Y数据拆分多个图，
#     |--DownloadCurrentData 多个dataframe，多个Y列对一个X列，染色，按照Y数据拆分多个图

class ZBar:
    def OnDFBarPlot(dfx,TitleName = 'No Name ??',Lenth = None,):
        df = dfx['Dataframe']
        colordef = dfx['StageColor']
        Yaixs = dfx['CompVals']
        if Lenth == None:
            newdf = pd.DataFrame()
            for i in Yaixs:
                temp = df.loc[:,['Date','Time',i]]
                temp.rename(columns={i: 'CompareValue'}, inplace=True)
                temp['ValueName'] = i
                newdf = newdf.append(temp)

        else:
            print('y')

        df = newdf
        barchart = px.bar(
            data_frame=df,
            x='Date',
            y='CompareValue',
            color="Time",               # differentiate color of marks
            opacity=0.8,                  # set opacity of markers (from 0 to 1)
            orientation="v",              # 'v','h': orientation of the marks
            barmode='group',           # in 'overlay' mode, bars are top of one another.
                                          # in 'group' mode, bars are placed beside each other.
                                          # in 'relative' mode, bars are stacked above (+) or below (-) zero.
            #----------------------------------------------------------------------------------------------
             facet_row='ValueName',          # assign marks to subplots in the vertical direction
            # facet_col='caste',          # assigns marks to subplots in the horizontal direction
            # facet_col_wrap=2,           # maximum number of subplot columns. Do not set facet_row!
            facet_row_spacing =0.3,
            # color_discrete_sequence=["pink","yellow"],               # set specific marker colors. Color-colum data cannot be numeric
            color_discrete_map=colordef,  # map your chosen colors
            # color_continuous_scale=px.colors.diverging.Picnic,       # set marker colors. When color colum is numeric data
            # color_continuous_midpoint=100,                           # set desired midpoint. When colors=diverging
            # range_color=[1,10000],                                   # set your own continuous color scale
            #----------------------------------------------------------------------------------------------
            # text='CompareValue',            # values appear in figure as text labels
            # hover_name='under_trial',   # values appear in bold in the hover tooltip
            # hover_data=['detenues'],    # values appear as extra data in the hover tooltip
            # custom_data=['others'],     # invisible values that are extra data to be used in Dash callbacks or widgets

            labels={"CompareValue":"",
            "Time":"Stage"},           # map the labels of the figure
            title=TitleName, # figure title
            width=1400,                   # figure width in pixels
            height=600,                   # figure height in pixels
            template='gridon',            # 'ggplot2', 'seaborn', 'simple_white', 'plotly',
                                          # 'plotly_white', 'plotly_dark', 'presentation',
                                          # 'xgridoff', 'ygridoff', 'gridon', 'none'

            # animation_frame='year',     # assign marks to animation frames
            # # animation_group=,         # use only when df has multiple rows with same object
            # # range_x=[5,50],           # set range of x-axis
            # range_y=[0,9000],           # set range of x-axis
            # category_orders={'year':    # force a specific ordering of values per column
            # [2013,2012,2011,2010,2009,2008,2007,2006,2005,2004,2003,2002,2001]},

        )

        # barchart.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
        # barchart.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500
        #barchart.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        barchart.update_layout(hovermode = False,uniformtext_minsize=8, uniformtext_mode='hide')

        barchart.layout.bargap =0.2
#-------------------------------------------------------------------------------
        pio.show(barchart)


    def OnDFsBarPlot(dfxs=[{},{}],TitleName = 'No Name ??',Yaixs=[],Lenth = None,):
        newdf = pd.DataFrame()
        for dfx in dfxs:
            df = dfx['Dataframe']
            CompVals = dfx['CompVals']
            TickerName = dfx['TickerName']
            colordef = dfx['StageColor']
            for i in CompVals:
                temp = df.loc[:,['Date','Time',i]]
                temp.rename(columns={i: 'CompareValue'}, inplace=True)
                temp['ValueName'] = TickerName+i
                newdf = newdf.append(temp)


        df = newdf
        barchart = px.bar(
            data_frame=df,
            x='Date',
            y='CompareValue',
            color="Time",               # differentiate color of marks
            opacity=0.8,                  # set opacity of markers (from 0 to 1)
            orientation="v",              # 'v','h': orientation of the marks
            barmode='group',           # in 'overlay' mode, bars are top of one another.
                                          # in 'group' mode, bars are placed beside each other.
                                          # in 'relative' mode, bars are stacked above (+) or below (-) zero.
            #----------------------------------------------------------------------------------------------
             facet_row='ValueName',          # assign marks to subplots in the vertical direction
            facet_row_spacing =0.2,
            color_discrete_map=colordef,  # map your chosen colors

            labels={"CompareValue":"",
            "Time":"Stage"},           # map the labels of the figure
            title=TitleName, # figure title
            width=1600,                   # figure width in pixels
            height=800,                   # figure height in pixels
            template='gridon',            # 'ggplot2', 'seaborn', 'simple_white', 'plotly',

        )

        barchart.update_layout(hovermode = False,uniformtext_minsize=8, uniformtext_mode='hide')

        barchart.layout.bargap =0.2
#-------------------------------------------------------------------------------
        pio.show(barchart)

def ZBar3D(PlotItem = dict()):
    XAxisList = []
    YAxisList = []
    ZBar3d=dict()
    for key,value in PlotItem.items():
        max = 0
        for i in value:
            if not i[0] in XAxisList:
                XAxisList.append(i[0])
            if not i[1] in YAxisList:
                YAxisList.append(i[1])
            if i[2] > max:
                max = i[2]
        ZBar3d[key+'_max'] = max
    ZBar3d
    screenwidth = '1600px'
    screenheight = '480px'
    page = Page()
    for key,value in PlotItem.items():

        ZBar3d[key]  = (
            Bar3D(init_opts=opts.InitOpts(width=screenwidth, height=screenheight))
                .add(
                series_name=key,
                shading="lambert",
                data=PlotItem[key],
                xaxis3d_opts=opts.Axis3DOpts(type_='category', data=XAxisList,interval=0),
                yaxis3d_opts=opts.Axis3DOpts(type_='category', data=YAxisList,interval=0),
                zaxis3d_opts=opts.Axis3DOpts(type_='value'),
                grid3d_opts=opts.Grid3DOpts(width=len(XAxisList)*8, height=100, depth=len(YAxisList)*8),

            )
                .set_global_opts(
                #datazoom_opts=opts.DataZoomOpts(type_='inside'),
                title_opts=opts.TitleOpts(title=key, pos_right="5%"),
                visualmap_opts=opts.VisualMapOpts(
                    max_=ZBar3d[key+'_max'],
                    range_color=[
                        '#ffffbf',
                        '#313695',
                        '#4575b4',
                        '#74add1',
                        '#abd9e9',
                        '#e0f3f8',
                        '#fee090',
                        '#fdae61',
                        '#f46d43',
                        '#d73027',
                        '#a50026',
                    ],
                )
            )
        )

        page.add(ZBar3d[key])
    page.render("page_default_layout.html")

    webbrowser.open(os.getcwd()+'\page_default_layout.html')
t = 0
def DrawCharts(Symbol,TimeStamp,KlineData,Volume,KAMAData,TrendVal,RSIData,ActionList,
               FlPL,StdPL,FixPL,SP500PL ):
    global t
    MarkPointList=list()
    for Action in ActionList:
        MarkPointList.append(opts.MarkPointItem(name="自定义标记点", coord=[TimeStamp.index(Action['TimeStamp']),
                                                                      Action['Value']],value=Action['Action'],
                                                    itemstyle_opts=opts.ItemStyleOpts(color=Action['Color'])))
    kline_data = KlineData
    kline = (
        Kline()
            .add_xaxis(xaxis_data=TimeStamp)
            .add_yaxis(
            series_name=Symbol,
            y_axis=kline_data,
            itemstyle_opts=opts.ItemStyleOpts(color="#00da3c", color0="#ec0000"),
            markpoint_opts=opts.MarkPointOpts(
                data=MarkPointList
            ),
        )
            .set_global_opts(
            legend_opts=opts.LegendOpts(
                is_show=False, pos_bottom=10, pos_left="center",
            ),
        )
    )
    #########################趋势线分割##############################
    AEMATrend = KAMAData['KAMA_[' + str(ZfinanceCfg.KAMATP[5]) + ']'].tolist()
    LineOffset = 0.005*(AEMATrend[0]+AEMATrend[-1])/2
    TrendUp  = ['-' for i in range(len(AEMATrend))]
    TrendDn  = ['-' for i in range(len(AEMATrend))]
    TrendNo  = ['-' for i in range(len(AEMATrend))]

    flag = 0
    RSIData_14=RSIData['RSI_[14]'].tolist()
    for i in range(len(AEMATrend)):
        if TrendVal[i] < -ZfinanceCfg.TrendGate:
            TrendDn[i] = AEMATrend[i]-LineOffset
            if flag != 1:
                TrendDn[i-1] = AEMATrend[i-1]-LineOffset
            flag = 1
        elif TrendVal[i] < ZfinanceCfg.TrendGate:
            TrendNo[i] = AEMATrend[i]-LineOffset
            if flag != 0:
                TrendNo[i-1] = AEMATrend[i-1]-LineOffset
            flag = 0
        else:
            TrendUp[i] = AEMATrend[i]-LineOffset
            if flag != -1:
                TrendUp[i-1] = AEMATrend[i-1]-LineOffset
            flag = -1
    ################################################################
    KAMAline = (
        Line()
            .add_xaxis(xaxis_data=TimeStamp)
            .add_yaxis(
            series_name="AdativeEMA"+str(ZfinanceCfg.KAMATP[0]),
            y_axis=KAMAData['KAMA_[' + str(ZfinanceCfg.KAMATP[0]) + ']'].tolist(),
            is_smooth=False,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=1),
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=False
        )
            .add_yaxis(
            series_name="AdativeEMA"+str(ZfinanceCfg.KAMATP[1]),
            y_axis=KAMAData['KAMA_[' + str(ZfinanceCfg.KAMATP[1]) + ']'].tolist(),
            is_smooth=False,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=1),
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=False
        )
            .add_yaxis(
            series_name="AdativeEMA"+str(ZfinanceCfg.KAMATP[2]),
            y_axis=KAMAData['KAMA_[' + str(ZfinanceCfg.KAMATP[2]) + ']'].tolist(),
            is_smooth=False,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=1),
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=False
        )
            .add_yaxis(
            series_name="AdativeEMA"+str(ZfinanceCfg.KAMATP[3]),
            y_axis=KAMAData['KAMA_[' + str(ZfinanceCfg.KAMATP[3]) + ']'].tolist(),
            is_smooth=False,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=1),
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=False
        )
            .add_yaxis(
            series_name="AdativeEMA"+str(ZfinanceCfg.KAMATP[4]),
            y_axis=KAMAData['KAMA_[' + str(ZfinanceCfg.KAMATP[4]) + ']'].tolist(),
            is_smooth=False,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=1),
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=False
        )
            .add_yaxis(
            series_name="AdativeEMA"+str(ZfinanceCfg.KAMATP[5]),
            y_axis=KAMAData['KAMA_[' + str(ZfinanceCfg.KAMATP[5]) + ']'].tolist(),
            is_smooth=False,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=1),
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=False
        )
            .add_yaxis(
            y_axis=TrendUp,
            series_name="TrendUp",
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=1),
            is_symbol_show=False,
            is_smooth=False,
            is_hover_animation=False,
            label_opts=opts.LabelOpts(is_show=False),
        )
            .add_yaxis(
            y_axis=TrendNo,
            series_name="TrendNo",
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=1),
            is_symbol_show=False,
            is_smooth=False,
            is_hover_animation=False,
            label_opts=opts.LabelOpts(is_show=False),
        )
            .add_yaxis(
            y_axis=TrendDn,
            series_name="TrendDn",
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=1),
            is_symbol_show=False,
            is_smooth=False,
            is_hover_animation=False,
            label_opts=opts.LabelOpts(is_show=False),
        )
            .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
    )
    ################################################################
    OverSellValue = 20
    OverBuyValue  = 80
    OverSellRSI = ['-' for i in range(len(RSIData))]
    RegularRSI  = ['-' for i in range(len(RSIData))]
    OverBuyRSI  = ['-' for i in range(len(RSIData))]
    flag = 0
    RSIData_14=RSIData['RSI_[14]'].tolist()
    for i in range(len(RSIData)):
        if RSIData_14[i] > OverBuyValue:
            OverBuyRSI[i] = RSIData_14[i]
            if flag == 0:
                OverBuyRSI[i-1] = RSIData_14[i-1]
            flag = 1
        elif RSIData_14[i] > OverSellValue:
            RegularRSI[i] = RSIData_14[i]
            if flag != 0:
                RegularRSI[i-1] = RSIData_14[i-1]
            flag = 0
        else:
            OverSellRSI[i] = RSIData_14[i]
            if flag == 0:
                OverSellRSI[i-1] = RSIData_14[i-1]
            flag = -1
    ################################################################
    RSIline = (
        Line()
            .add_xaxis(xaxis_data=TimeStamp)
            .add_yaxis(
                y_axis=OverBuyRSI,
                series_name="OverBuyRSI_14",
                linestyle_opts=opts.LineStyleOpts(width=1, opacity=1),
                is_symbol_show=False,
                #itemstyle_opts=opts.ItemStyleOpts(color="#ec0000"),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(y=OverBuyValue, name="OverBuy")]
                ),
            )
            .add_yaxis(
                y_axis=RegularRSI,
                series_name="RegularRSI_14",
                is_smooth=False,
                is_hover_animation=False,
                linestyle_opts=opts.LineStyleOpts(width=1, opacity=1),
                label_opts=opts.LabelOpts(is_show=False),
                is_symbol_show=False,
                #itemstyle_opts=opts.ItemStyleOpts(color="pink"),
            )
            .add_yaxis(
                y_axis=OverSellRSI,
                series_name="OverSellRSI_14",
                linestyle_opts=opts.LineStyleOpts(width=1, opacity=1),
                is_symbol_show=False,
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(y=OverSellValue, name="OverSell")]
                ),
            )
            .add_yaxis(
            y_axis=RSIData['RSI_[21]'].tolist(),
            series_name="RSI_21",
            is_smooth=False,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=1),
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False),
        )
            .add_yaxis(
            y_axis=RSIData['RSI_[50]'].tolist(),
            series_name="RSI_50",
            is_smooth=False,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=1),
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False),
        )
    )

    VolumeBar = (
        Bar()
            .add_xaxis(xaxis_data=TimeStamp)
            .add_yaxis(
            series_name="Volume",
            y_axis=Volume,
            xaxis_index=1,
            yaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
        )
    )
    PLBar = (
        Bar()
            .add_xaxis(xaxis_data=TimeStamp)
            .add_yaxis(
            series_name="Float P/L",
            y_axis=FlPL,
            yaxis_index=0,
            label_opts=opts.LabelOpts(is_show=False),
            )
            .add_yaxis(
            series_name="Standard P/L",
            y_axis=StdPL,
            yaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
            )
            .add_yaxis(
            series_name="Fixed P/L",
            y_axis=FixPL,
            yaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
            )
            .add_yaxis(
            series_name="SP500 P/L",
            y_axis=SP500PL,
            yaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
            )
       .set_global_opts(
            yaxis_opts=opts.AxisOpts(
                type_="value",
                position="left",
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        )
    )
    # Kline And Line
    overlap_kline_line = kline.overlap(KAMAline)

    # Grid Overlap + Bar
    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width="1900px",
            height="900px",
            animation_opts=opts.AnimationOpts(animation=False),
            theme=ThemeType.CHALK
        )
    )
    grid_chart.add(
        overlap_kline_line.set_global_opts(
            title_opts=opts.TitleOpts(pos_top="2%", title="Kline&KAMA"),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False,
                    type_="inside",
                    xaxis_index=[0, 1 ,2, 3],
                    range_start=50,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    xaxis_index=[0, 1, 2, 3],
                    type_="slider",
                    pos_top="97%",
                    range_start=98,
                    range_end=100,
                ),
            ],
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="cross",
                background_color="rgba(245, 245, 245, 0.8)",
                border_width=1,
                border_color="#ccc",
                textstyle_opts=opts.TextStyleOpts(color="#000"),
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_show=False,
                dimension=2,
                series_index=5,
                pos_top="10",
                pos_right="10",
                is_piecewise=True,
                pieces=[
                    {"value": 1, "color": "red"},
                    {"value": -1, "color": "green"},
                ],
            ),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True,
                link=[{"xAxisIndex": "all"}],
                label=opts.LabelOpts(background_color="#777"),
            ),
            brush_opts=opts.BrushOpts(
                x_axis_index="all",
                brush_link="all",
                out_of_brush={"colorAlpha": 0.1},
                brush_type="lineX",
            ),
            legend_opts=opts.LegendOpts(pos_top="2%"),
        ),
        grid_opts=opts.GridOpts(
            pos_left="4%", pos_right="8%", pos_top="7%",height="40%"
        ),

    )
    grid_chart.add(
        VolumeBar.set_global_opts(title_opts = opts.TitleOpts(pos_top="50%", title="Volume"),
                                  legend_opts=opts.LegendOpts(pos_top="50%"),),
        grid_opts=opts.GridOpts(
            pos_left="4%", pos_right="8%", pos_top="53%", height="7%"
        ),


    )
    grid_chart.add(
        RSIline.set_global_opts(title_opts = opts.TitleOpts(pos_top="63%", title="RSI14"),
                                legend_opts=opts.LegendOpts(pos_top="63%"),),
        grid_opts=opts.GridOpts(
            pos_left="4%", pos_right="8%", pos_top="66%", height="9%"
        ),

    ),
    grid_chart.add(
        PLBar.set_global_opts(title_opts = opts.TitleOpts(pos_top="78%", title="Profit&Loss"),
                              legend_opts=opts.LegendOpts(pos_top="78%"),),
        grid_opts=opts.GridOpts(
            pos_left="4%", pos_right="8%", pos_top="82%", height="12%"
        ),
    )
    grid_chart.render(Symbol+"_Kline_RSI_PL.html")
    webbrowser.open(os.getcwd()+"\\"+Symbol+"_Kline_RSI_PL.html")


