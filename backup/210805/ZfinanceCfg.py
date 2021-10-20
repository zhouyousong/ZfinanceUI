from enum import Enum

api_key = '0LM5UNHJWFGBDIAMHJAUPAKVXBUVQPZU@AMER.OAUTHAP'
token_path = 'C:\CAIC\99_个人资料\\04_tda\\token'
redirect_uri = 'https://localhost'

account_id = 123456789
	
# put path to chromedriver here
chromedriver_path='C:\CAIC\99_个人资料\\04_tda\chromedriver.exe'

EXTENDLEN = 100
PROXYEN   = '127.0.0.1:7890'
#PROXYEN = None
PeriodDict={
    'PeriodStr' : ["1 Day", "5 Days", '30 Days', '90 Days', '180 Days', '1 Years',
                 '2 Years', "5 Years", '10 Years' ,'MAX'],
    'PeriodStrPara' : ["1d", "5d", '1mo', '3mo', '6mo', '1y',
                 '2y', "5y", '10y', 'max'],
    'Period2Days': [1, 4, 20, 80, 160, 340,
                      700, 1700, 3500,  -1]
}

class TableColor(Enum):
    Green   = 1
    Yellow  = 2
    Red     = 3
