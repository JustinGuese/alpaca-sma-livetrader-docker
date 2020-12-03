import yfinance as yf
import backtrader as bt
import csv
import numpy as np
import os


STOCK = os.environ["STOCK"]
stocks = [STOCK]
data = yf.download(stocks,period="90d",interval="60m")

# https://backtest-rookies.com/2017/08/22/backtrader-multiple-data-feeds-indicators/
class SmaCross(bt.Strategy):

    params = (
        ('pfast', 5),
        ('pslow',15),
        ('allowshorts',0),
        ('printLog',False)
    )

    def __init__(self):
      self.crosses = dict()
      for d in self.datas:
          # d._name should be stock name
          sma1, sma2 = bt.ind.SMA(d.close,period=self.p.pfast), bt.ind.SMA(d.close,period=self.p.pslow)
          ind = bt.ind.CrossOver(sma1, sma2)
          ind.plotinfo.plotname = '%s_SMA'%d._name
          self.crosses.update({d._name:ind})

    def next(self):
      for i, d in enumerate(self.datas):
          dt, dn = self.datetime.date(), d._name
          # print(dn,self.crosses[d._name][0])
          pos = self.getposition(d).size
          if not pos:  # no market / no orders
              if self.crosses[d._name][0] == 1:
                  self.buy(data=d)
              elif self.crosses[d._name][0] == -1 and self.p.allowshorts == 1:
                  self.sell(data=d)
          else:
              if self.crosses[d._name][0] == 1:
                  self.close(data=d)
                  self.buy(data=d)
              elif self.crosses[d._name][0] == -1:
                  self.close(data=d)
                  self.sell(data=d)

    def notify_trade(self, trade):
        dt = self.data.datetime.date()
        if trade.isclosed and self.p.printLog:
            print('{} {} Closed: PnL Gross {}, Net {}'.format(
                                                dt,
                                                trade.data._name,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))

def sqn_eval(nr):
  if nr <= 1.9:
    return "below average"
  elif nr <= 2.4:
    return "average"
  elif nr <= 2.9:
    return "good"
  elif nr <= 5.:
    return "excellent"
  elif nr <= 6.9:
    return "superb"
  elif nr > 6.9:
    return "HOLY GRAIL - $$$"
  else:
    return "ERROR"


def run_once(pfast,pslow,startcash=10000):
  cerebro = bt.Cerebro(optreturn=True,maxcpus=None,cheat_on_open=True) # cheat on open bc i can instantly buy if signal appears
  startcash = startcash   
  # Set our desired cash start
  cerebro.broker.setcash(startcash)
  for stock in stocks:
    cerebro.adddata(bt.feeds.PandasData(dataname=data,name=stock))

  # strategy
  cerebro.addstrategy(SmaCross, pfast=pfast,pslow=pslow) # not used bc opt strategy

  # cerebro.optstrategy(SmaCross, pfast=pfast,pslow=pslow) # https://backtest-rookies.com/2017/06/26/optimize-strategies-backtrader/

  # add analyzer
  cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio') #  timeframe=bt.TimeFrame.Months
  cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown') #  timeframe=bt.TimeFrame.Months
  cerebro.addanalyzer(bt.analyzers.Returns, _name='Returns') #  timeframe=bt.TimeFrame.Months
  cerebro.addanalyzer(bt.analyzers.SQN, _name='SQN') #  timeframe=bt.TimeFrame.Months


  # sizer
  cerebro.addsizer(bt.sizers.PercentSizer, percents=33)

  results = cerebro.run()
  return results,cerebro,startcash

def run_opt(pfast,pslow,startcash=10000):
  cerebro = bt.Cerebro(optreturn=True,maxcpus=1,cheat_on_open=True) # i can instantly buy
  startcash = startcash   
  # Set our desired cash start
  cerebro.broker.setcash(startcash)
  for stock in stocks:
    cerebro.adddata(bt.feeds.PandasData(dataname=data,name=stock))

  # strategy
  # cerebro.addstrategy(SmaCross) # not used bc opt strategy
  cerebro.optstrategy(SmaCross, pfast=pfast,pslow=pslow) # https://backtest-rookies.com/2017/06/26/optimize-strategies-backtrader/

  # add analyzer
  cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio') #  timeframe=bt.TimeFrame.Months
  cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown') #  timeframe=bt.TimeFrame.Months
  cerebro.addanalyzer(bt.analyzers.Returns, _name='Returns') #  timeframe=bt.TimeFrame.Months
  cerebro.addanalyzer(bt.analyzers.SQN, _name='SQN') #  timeframe=bt.TimeFrame.Months


  # sizer
  cerebro.addsizer(bt.sizers.PercentSizer, percents=33)

  results = cerebro.run()
  return results,cerebro,startcash



def single_analytics(results,cerebro,startcash,printout=False):

  ## Analyzers
  # sharpe ratio
  sharper = results[0].analyzers.SharpeRatio.get_analysis()["sharperatio"]
  
  # drawdown
  maxdrawdown = results[0].analyzers.DrawDown.get_analysis().max.drawdown
  avgdrawdown = results[0].analyzers.DrawDown.get_analysis().drawdown
  # returns
  annualreturnpct = results[0].analyzers.Returns.get_analysis()["rnorm100"]
  monthlyreturnpct = annualreturnpct / 12
  # SQN SystemQualityNumber - https://www.backtrader.com/docu/analyzers-reference/
  sqn, nrtrades = results[0].analyzers.SQN.get_analysis()["sqn"],results[0].analyzers.SQN.get_analysis()["trades"]
  #Print out the final result
  if printout:
    print("\n\n\n")
    print('Sharpe Ratio: ', sharper)
    print("Avg Drawdown: %.2f pct, Max Drawdown: %.2f pct"%(avgdrawdown,maxdrawdown))
    print("Yearly return %.2f pct, Monthly return %.2f pct"%(annualreturnpct,monthlyreturnpct))
    print("SQN: %d, nr of trades: %d"%(sqn,nrtrades))
    print("SQN Evaluation: %s"%sqn_eval(sqn))
  return sharper,sqn,nrtrades,avgdrawdown,maxdrawdown,annualreturnpct,monthlyreturnpct

def multiple_analytics(results,cerebro, startcash, showHowMany=10):
  # Generate results list
  final_results_list = []
  for run in results:
        sharper,sqn,nrtrades,avgdrawdown,maxdrawdown,annualreturnpct,monthlyreturnpct = single_analytics(run,cerebro,startcash)
        pslow = run[0].params.pslow
        pfast = run[0].params.pfast
        if None in [sharper,sqn,nrtrades,avgdrawdown,maxdrawdown,annualreturnpct,monthlyreturnpct]:
          # if one metric failed
          final_results_list.append([pfast,pslow,0,sqn,nrtrades,avgdrawdown,maxdrawdown,annualreturnpct,monthlyreturnpct])
        else:
          
          final_results_list.append([pfast,pslow,sharper,sqn,nrtrades,avgdrawdown,maxdrawdown,annualreturnpct,monthlyreturnpct])

  #Sort Results List
  by_PnL = sorted(final_results_list, key=lambda x: x[7], reverse=True)
  by_Sharpe = sorted(final_results_list, key=lambda x: x[2], reverse=True)
  by_SQN = sorted(final_results_list, key=lambda x: x[3], reverse=True)

  #Print results
  print('\n\nResults: Ordered by Profit:')
  for result in by_PnL[:showHowMany]:
      print('pfast: {}, pslow: {},  Annual Ret: {}, nrtrades: {} - Evaluation: {}'.format(result[0], result[1], result[7],result[4],sqn_eval(result[3])))
  print('\n\nResults: Ordered by Sharpe Ratio:')
  for result in by_Sharpe[:showHowMany]:
      print('pfast: {}, pslow: {},  Annual Ret: {}, Sharpe Ratio: {}'.format(result[0], result[1],result[7],  result[2]))
  print('\n\nResults: Ordered by SQN:')
  for result in by_SQN[:showHowMany]:
      print('pfast: {}, pslow: {}, Annual Ret: {}, SQN: {} nrtrades: {} - Evaluation: {}'.format(result[0], result[1], result[7], result[3],result[4],sqn_eval(result[3])))
  return by_PnL,by_Sharpe,by_SQN

rang = np.array(range(1,20))
rangsl = rang * 3
rangsr = rang * 2
rangsl = np.concatenate([rangsl,rangsr])
results,cerebro,startcash = run_opt(rang,rangsl)
by_PnL,by_Sharpe,by_SQN = multiple_analytics(results,cerebro, startcash)

bestpfast,bestpslow = by_SQN[0][0],by_SQN[0][1]
result,cerebro,startcash = run_once(bestpfast,bestpslow)
sharper,sqn,nrtrades,avgdrawdown,maxdrawdown,annualreturnpct,monthlyreturnpct = single_analytics(result,cerebro,startcash,printout=True)
data = [[STOCK,bestpfast,bestpslow,sqn,annualreturnpct]]
columns = ["stock","smafast","smaslow","sqn","annualreturnpct"]

with open('output/%s.csv'%STOCK,'wb') as result_file:
    wr = csv.writer(result_file, dialect='excel')
    wr.writerows(data)