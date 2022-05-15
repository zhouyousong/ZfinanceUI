# ZfinanceUI  
2022.5.15：新增使用说明，http://www.zhouyousong.cn/2022/05/09/zfinance%e4%bd%bf%e7%94%a8%e6%89%8b%e5%86%8c/  

闲暇时间写了个美股数据下载，行业行情分析，交易策略回测，实时策略监控开源工具  

做这个项目之初因为我自己买美股，我是希望能用它来赚钱，但是快一年了，我一直沉浸在python编程学习的快乐之中，同时也因为有一些阶段性成果而有成就感，所以希望找到志同道合之人，能一起完善，一起学习，如果你也炒美股，希望能有一天能用他赚钱  

我之前也不会python，后来慢慢通过做这个程序，学会了pyqt 写UI，学会了panda numpy等常用库，这个过程掌握了不少计算机技巧，比如最近又了解了多进程和多线程在python里的区别，搞定了多进程并行计算，把回测的速度加快了3倍  
    
目前实现的功能我罗列一下  
1，多线程股票数据下载  
----可选择不同的股票市场（nasdaq，纽交所）  
----可设置自选组  
----可选不同的时间间隙数据和财务报表数据下载  
----可选下载多长时间的数据  
----可设置下载线程数量  
----需要配置VPN（yahoo数据源，去年11月开始限制了国内访问）  
----可更新股票列表  
 
2，行业行情分析  
----美股每支股票列表里面有很多属性例如行业，城市，国家等，可按照这些行业分类（可交集）  
----可将分类出来的股票集进行市值和，平均市值等计算，例如可以计算【加州】的所有【科技行业】的市值和  
----可以对分类出来的简单绘图  

3，策略回测  
----可设置自选股票  
----目前有我写的一个策略，可以修改这个策略参数组进行回测，回测结果表格化显示  
----可按照规律自动生成一系列参数组，然后一组一组自动跑，第二天起来看哪一组参数效果比较好，这样就不用盯着来试参数了  
----特点：可配置多个CPU并行计算加速  

这是目前已经实现的，当然还有很多UI逻辑bug，所以需要有人一起来玩儿  
一些效果截图  
![图片](https://user-images.githubusercontent.com/88005595/164954716-26dfc709-46c3-4a12-94c6-6aaddb200654.png)  
![图片](https://user-images.githubusercontent.com/88005595/164954721-3acab923-c739-421f-8af0-11d9a3ebfa2e.png)  
![图片](https://user-images.githubusercontent.com/88005595/164954737-3e6e771a-3cbc-448c-8c85-bf44751e1970.png)  
![图片](https://user-images.githubusercontent.com/88005595/164954732-88898728-b52e-40b4-ba60-1ee458917202.png)  

回测的效果图  
![图片](https://user-images.githubusercontent.com/88005595/164957423-ac222ef5-1fd2-4dfc-aa15-c865bf739a29.png)  

分析效果图
如：港股里通讯行业58支股票总市值的走势，以及平均市值，毛利润总和等  
![图片](https://user-images.githubusercontent.com/88005595/167413608-8298d35b-779c-4860-b321-b5b4c9cd58ab.png)
如：港股北京上市股票的总市值和平均市值  
![图片](https://user-images.githubusercontent.com/88005595/167413877-dab257ee-fc1a-428c-a8f3-f1b80a9dd8c2.png)
如：港股按城市域排序，杭州平均市值最高  
![图片](https://user-images.githubusercontent.com/88005595/167414012-012f0e02-8959-4481-9300-41277f99e9ff.png)

总之大家可以自己想想怎么组合，比如港股里北京的做通讯的.....然后看看能不能挖掘出逆势的板块

安装方法  
我是用pycharm的，所以我也并没有验证过纯python的环境运行如何  
我是用python3.9的解释器，库的安装如下  
Install below  
pip install yfinance==0.1.62  （一定要这个版本） 
![图片](https://user-images.githubusercontent.com/88005595/164975122-02acbd23-3b51-403d-b67d-c37e613d9314.png)

pip install keyboard  
pip install pyecharts  
![图片](https://user-images.githubusercontent.com/88005595/164975109-16e45c07-75e1-4cd4-a9c4-c667f375e839.png)

pip install plotly  
pip install PySide2  
![图片](https://user-images.githubusercontent.com/88005595/164975137-c816fbba-8d93-4283-a4d6-5480a801f6bd.png)

pip install pyqt5  
![图片](https://user-images.githubusercontent.com/88005595/164975150-225362af-ebfb-4590-9f26-d3e9e47721c4.png)

另外TA_lib 似乎不能在线安装，所以我已经上传离线安装包了（注意，我上传得是对应python3.9 64位版本，也可以到 https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib 下载自己环境对应得版本）  
pip install .\misc\TA_Lib-0.4.21-cp39-cp39-win_amd64.whl  
![图片](https://user-images.githubusercontent.com/88005595/164975132-59369293-0ff8-4635-ba04-e7b0214a846b.png)

增加了A股和港股的数据拉取，解决了一些小问题  
![图片](https://user-images.githubusercontent.com/88005595/167295569-2dad3566-782b-4aeb-b017-5b0e6c6c4c46.png)

也新增如下库，用于拉取列表，顺便推荐一下efinance，不需要翻墙就可以拿数据，但是由于我已经用yfinance做好了，所以就没重写  
pip install efinance  

如何是纯python环境不含ide的环境运行，注意下运行方法，需要cmd先进到在zfinance的文件夹路径下，再用你的python路径，指向ZfinanceMainUi.py去打开，如下图所示  
![图片](https://user-images.githubusercontent.com/88005595/167413171-78ce8720-b1f4-4013-ba34-6afb726ebc5a.png)


注意几个问题  
yahoo财经去年（2021年）退出中国，所以必须vpn代理才能访问  

使用方法慢慢编写释放，欢迎大家一起参与  
如果想加群可添加我wx：zhou-yousong  
