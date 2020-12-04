import alpaca_trade_api as tradeapi
import os

ALPACAUSER = os.environ["ALPACAUSER"]
ALPACAPW = os.environ["ALPACAPW"]

api = tradeapi.REST(ALPACAUSER,ALPACAPW,'https://paper-api.alpaca.markets')
portfolio = api.list_positions()
print("portfolio")
for position in portfolio:
    print("{} shares of {}".format(position.qty, position.symbol))