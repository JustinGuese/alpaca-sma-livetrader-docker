import yfinance as yf
import os
import numpy as np
import alpaca_trade_api as tradeapi


ALPACAUSER = os.environ["ALPACAUSER"]
ALPACAPW = os.environ["ALPACAPW"]
#
STOCK = os.environ["STOCK"]
FastSMA = int(os.environ["FastSMA"])
SlowSMA = int(os.environ["SlowSMA"])
MoneyDivide = int(os.environ["MoneyDivide"])

smallestWindow = np.min([FastSMA,SlowSMA])

data =  yf.download([STOCK],period="14d",interval="60m")
# SMA
data["FastSMA"] = data["Close"].rolling(window=FastSMA).mean()
data["SlowSMA"] = data["Close"].rolling(window=SlowSMA).mean()


previous_15 = data['FastSMA'].shift(1)
previous_45 = data['SlowSMA'].shift(1)
crossingup = ((data['FastSMA'] <= data['SlowSMA']) & (previous_15 >= previous_45))
crossingdown = ((data['FastSMA'] >= data['SlowSMA']) & (previous_15 <= previous_45))

data.loc[crossingup,"signal"] = "up"
data.loc[crossingdown,"signal"] = "down"


def longBuy(STOCK,qty):
    api.submit_order(
        symbol=STOCK,
        qty=qty,
        side='buy',
        type='market',
        time_in_force='gtc'
    )

def longSell(STOCK,qty):
    api.submit_order(
        symbol=STOCK,
        qty=qty,
        side='sell',
        type='market',
        time_in_force='gtc'
    )

if data["signal"][-1] == data["signal"][-1]: # pytrixxx for nan
    api = tradeapi.REST(ALPACAUSER,ALPACAPW,'https://paper-api.alpaca.markets')
    account = api.get_account()
    buyingpower = float(account.buying_power) / MoneyDivide
    crntPrice = data["Close"][-1]
    howmany = int(buyingpower/crntPrice)
    # portfolio
    portfolio = api.list_positions()
    print("portfolio")
    PositionsInStock = 0
    for position in portfolio:
        print("{} shares of {}".format(position.qty, position.symbol))
        if str(position.symbol) == STOCK:
            PositionsInStock = int(position.qty)

    if data["signal"][-1] == "up":
        # buy
        if PositionsInStock == 0:
            print("BUY %s %d!"%(STOCK,howmany))
            longBuy(STOCK,howmany)
        else:
            print("Buy, but still have positions...")
    elif data["signal"][-1] == "down":
        #sell
        if PositionsInStock > 0:
            print("SELL %s %d!"%(STOCK,PositionsInStock))
            longSell(STOCK,PositionsInStock)
        else:
            print("Sell, but no positions...")
    else:
        raise Exception("Not possible value: ",data["signal"][-1])
else:
    print("no cross")
            
#print(data.tail(20))