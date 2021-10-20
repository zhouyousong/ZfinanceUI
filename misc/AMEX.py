import Zfinance as zf

AMEX=zf.StockExchange('AMEX')
AMEX.DownloadStockHistoryPrice()
AMEX.DownloadStockCurrentPrice()

