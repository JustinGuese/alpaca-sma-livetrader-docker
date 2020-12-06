import yfinance as yf
import os
import numpy as np
import alpaca_trade_api as tradeapi
from elasticsearch import Elasticsearch
from datetime import datetime

es = Elasticsearch()

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

def error2Elastic(msg):
    body  = {
        "error": str(msg),
        "timestamp" : datetime.utcnow(),
    }
    es.index(index="smalivetrader-errorlog",body=body)

def log2Elastic(stock,qty,side,price):
    body  = {
        "stock": str(stock),
        "timestamp" : datetime.utcnow(),
        "qty" : int(qty),
        "side" : str(side),
        "price" : float(price)
    }
    es.index(index="smalivetrader-trades",body=body)


def longBuy(STOCK,qty,price):
    try:
        api.submit_order(
            symbol=STOCK,
            qty=qty,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        log2Elastic(STOCK,qty,"longBuy",price)
    except Exception as e:
        error2Elastic(e)
    # try 2 save 2 elastic

def longSell(STOCK,qty,price):
    try:
        api.submit_order(
            symbol=STOCK,
            qty=qty,
            side='sell',
            type='market',
            time_in_force='gtc'
        )
        log2Elastic(STOCK,qty,"longSell",price)
    except Exception as e:
        error2Elastic(e)


crntPrice = data["Close"][-1]

if data["signal"][-1] == data["signal"][-1]: # pytrixxx for nan
    api = tradeapi.REST(ALPACAUSER,ALPACAPW,'https://paper-api.alpaca.markets')
    account = api.get_account()
    buyingpower = float(account.buying_power) / MoneyDivide
    howmany = int(buyingpower/crntPrice)
    # portfolio
    portfolio = api.list_positions()
    print("portfolio")
    PositionsInStock = 0
    for position in portfolio:
        print("{} shares of {}".format(position.qty, position.symbol))
        if str(position.symbol) == STOCK:
            PositionsInStock = int(position.qty)

    if data["signal"][-1] == "up" or data["signal"][-2] == "down": # like it can happen that we miss a spot
        # buy
        if PositionsInStock == 0:
            print("BUY %s %d!"%(STOCK,howmany))
            longBuy(STOCK,howmany,crntPrice)
        else:
            print("Buy, but still have positions...")
    elif data["signal"][-1] == "down" or data["signal"][-2] == "down":
        #sell
        if PositionsInStock > 0:
            print("SELL %s %d!"%(STOCK,PositionsInStock))
            longSell(STOCK,PositionsInStock,crntPrice)
        else:
            print("Sell, but no positions...")
    else:
        raise Exception("Not possible value: ",data["signal"][-1])
else:
    print("no cross")
    log2Elastic(STOCK,0,"nocross",crntPrice)
            
#print(data.tail(20))