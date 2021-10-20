from tda import auth, client
import time
import datetime
#from tda.orders import EquityOrderBuilder, Duration, Session
import json
import ZfinanceCfg
import datetime
#账户：364245117@qq.com
#密码:大密
# authenticate
try:
    c = auth.client_from_token_file(ZfinanceCfg.token_path, ZfinanceCfg.api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path=ZfinanceCfg.chromedriver_path) as driver:
        c = auth.client_from_login_flow(
            driver, ZfinanceCfg.api_key, ZfinanceCfg.redirect_uri, ZfinanceCfg.token_path)

# get price history for a symbol
r = c.get_price_history('AAPL',
        period_type=client.Client.PriceHistory.PeriodType.MONTH,
        period=client.Client.PriceHistory.Period.SIX_MONTHS,
        frequency_type=client.Client.PriceHistory.FrequencyType.MINUTE,
        frequency=client.Client.PriceHistory.Frequency.EVERY_FIVE_MINUTES)

lists = r.json()
x = lists['candles']
print('r = ')
print(len(x))
for i in x:
    print("%s  price = %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i['datetime']/1000)),i['close']))
print('-----------------')
print(json.dumps(r.json(), indent=4))
# get a stock quote
response = c.get_quote('AAPL')

print(response.json())

# get stock fundamental data
response = c.search_instruments(['AAPL', 'BA'], c.Instrument.Projection.FUNDAMENTAL)

print(json.dumps(response.json(), indent=4))

# get option chain
response = c.get_option_chain('AAPL')

print(json.dumps(response.json(), indent=4))

# get all call options
response = c.get_option_chain('AAPL', contract_type=c.Options.ContractType.CALL)

print(json.dumps(response.json(), indent=4))

# get call options for a specific strike
response = c.get_option_chain('AAPL', contract_type=c.Options.ContractType.CALL, strike=300)

print(json.dumps(response.json(), indent=4))

# get call options for a specific strike and date range
start_date = datetime.datetime.strptime('2021-04-24', '%Y-%m-%d').date()
end_date = datetime.datetime.strptime('2021-05-01', '%Y-%m-%d').date()

response = c.get_option_chain('AAPL', contract_type=c.Options.ContractType.CALL, strike=300, from_date=start_date, to_date=end_date)

print(json.dumps(response.json(), indent=4))

# limit order of 5 shares of redfin stock at 18 dollars a share
#builder = EquityOrderBuilder('RDFN', 5)
#builder.set_instruction(EquityOrderBuilder.Instruction.BUY)
#builder.set_order_type(EquityOrderBuilder.OrderType.LIMIT)
#builder.set_price(18)
#builder.set_duration(Duration.GOOD_TILL_CANCEL)
#builder.set_session(Session.NORMAL)

#response = c.place_order(config.account_id, builder.build())

print(response)