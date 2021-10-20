from yql.api import YQL
import datetime, quandl

ndq = quandl.get("NASDAQOMX/COMP-NASDAQ",
              trim_start='2018-03-01',
              trim_end='2018-04-03')

print(ndq.head(4))

ticker = ['^IXIC', '^DJI']
for t in ticker:
    try:
        yql = YQL(t, '2020-01-01', '2020-01-30')
        print("Ticker: {0}".format(t))
        for item in yql:
            print(item.get('date'), item.get('price'))
    except:
        print('Failed to Get Reply from Yahoo API')
