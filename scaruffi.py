from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import sys
import collections
import datetime
import math
import copy

ASSET = ['USO', 'CAD=X']

api_key = sys.argv[1]

def volatility_of_asset(asset):
    ts = TimeSeries(key=api_key, indexing_type='date')
    data, meta_data = ts.get_daily(symbol=asset,outputsize='full')

    volatilities = collections.defaultdict(list)

    for date in data.keys():
        close_ = float(data[date]['4. close'])
        open_= float(data[date]['1. open'])
        volatilities[date[:7]].append(math.log(close_) / math.log(open_) - 1)

    def stddev(xs):
        mean = sum(xs) / len(xs)
        return math.sqrt(sum(math.pow(x - mean, 2) for x in xs) / (len(xs) - 1))

    for month in volatilities.keys():
        if month == '2018-06':
            volatilities[month] = 0.0
            continue
        volatilities[month] = stddev(volatilities[month])

    vols = []
    for month in sorted(volatilities.keys()):
        vols.append(volatilities[month])
    return vols

def logreturns(asset):
    ts = TimeSeries(key=api_key, indexing_type='date')
    data, meta_data = ts.get_daily(symbol=asset,outputsize='full')

    for date in data.keys():
        close_ = float(data[date]['4. close'])
        open_= float(data[date]['1. open'])
        returns[date] = math.log(close_) / math.log(open_) - 1

    rets = []
    for day in sorted(returns.keys()):
        rets.append(returns[day])
    return rets

def closes(asset):
    ts = TimeSeries(key=api_key, indexing_type='date')
    data, meta_data = ts.get_daily(symbol=asset,outputsize='full')
    clos = collections.defaultdict(list)

    for date in data.keys():
        close_ = float(data[date]['4. close'])
        clos[date] = close_

    clss = []
    for day in sorted(clos.keys()):
        clss.append(clos[day])
    return clss

if len(ASSET) == 1:
    a = ASSET[0]
    vs = logreturns(a)

    plt.plot(vs[:-1], vs[1:], 'go')
    plt.show()
elif len(ASSET) == 2:
    a1 = ASSET[0]
    a2 = ASSET[1]
    vs1 = closes(a1)
    vs2 = closes(a2)
    l = min(len(vs1),len(vs2))
    vs1 = vs1[-l:]
    vs2 = vs2[-l:]
    print(vs1)
    print(vs2)

    plt.plot(vs1, vs2, 'go')
    plt.xlabel(a1)
    plt.ylabel(a2)
    plt.show()


