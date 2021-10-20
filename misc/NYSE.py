import Zfinance as zf

NYSE=zf.StockExchange('NYSE')
NYSE.DownloadStockHistoryPrice()
NYSE.DownloadStockCurrentPrice()