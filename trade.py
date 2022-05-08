import yfinance
import pandas
import efinance as ef

x = ef.stock.get_realtime_quotes("港股")
x.to_csv('美股_Info.csv', sep=',',index_label='symbol')
print(x)


SYM = yfinance.Ticker('300585.ss')
TickerCurrentInfo = SYM.get_info(proxy='http://127.0.0.1:7890')
print(TickerCurrentInfo)