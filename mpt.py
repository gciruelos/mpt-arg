from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import sys
import collections
import datetime
import math
import copy

api_key = sys.argv[1]
# no: BYMA.BA, CVH.BA, HARG.BA, LOMA.BA, TXAR.BA
assets = ['AGRO.BA', 'ALUA.BA', 'APBR.BA', 'BMA.BA', 'BYMA.BA', 'CEPU.BA',
          'COME.BA', 'CRES.BA', 'CVH.BA', 'DGCU2.BA', 'EDN.BA', 'FRAN.BA',
          'GGAL.BA', 'HARG.BA', 'LOMA.BA', 'METR.BA', 'MIRG.BA', 'PAMP.BA',
          'PGR.BA', 'SUPV.BA', 'TECO2.BA', 'TGNO4.BA', 'TGSU2.BA', 'TRAN.BA',
          'TS.BA', 'TXAR.BA', 'VALO.BA', 'YPFD.BA']
fst_date = datetime.datetime.strptime('2013-06-01', '%Y-%m-%d')
RISKFREE_RATE = 30.25 / 100

prices = collections.defaultdict(dict)
diffs = collections.defaultdict(dict)

means = {}
covariances = collections.defaultdict(dict)

for asset in assets:
    ts = TimeSeries(key=api_key, indexing_type='date')
    data, meta_data = ts.get_daily(symbol=asset,outputsize='full')
    # print(data)
    # print(meta_data)
    for date in data.keys():
        d = datetime.datetime.strptime(date, '%Y-%m-%d')
        if d >= fst_date:
            prices[asset][d] = float(data[date]['4. close'])
    #plt.plot(prices[asset].keys(), [prices[asset][date] for date in prices[asset].keys()])
    #plt.title('Times Series for the '+asset+' stock (1 day)')
    #plt.show()

for asset in assets:
    asset_prices = prices[asset]
    for date in asset_prices.keys():
        next_year = date + datetime.timedelta(days=365)
        if next_year in asset_prices and asset_prices[date] > 0 and asset_prices[next_year] > 0:
            diffs[asset][next_year] = asset_prices[next_year] / asset_prices[date] - 1

assets = list(filter(lambda a: len(diffs[a]) > 0, assets))
print(assets)

for asset in assets:
    accumulator = 0.0
    for diff in diffs[asset].values():
        accumulator += diff
    means[asset] = accumulator / len(diffs[asset])

for asset1 in assets:
    for asset2 in assets:
        accumulator = 0.0
        n_sample = 0
        for date in diffs[asset1].keys():
            if date in diffs[asset2]:
                accumulator += (diffs[asset1][date] - means[asset1]) * (diffs[asset2][date] - means[asset2])
                n_sample += 1
        covariances[asset1][asset2] = accumulator / (n_sample - 1)
print(means)
print(covariances)


# Tagency portfolio:
# argmax_w  (mu' * w - r_f) / sqrt(w' Sigma w)
#   where: w are the weights,
#          r_f is the risk-free rate,
#          Sigma is the covariance matrix, and
#          ' means transpose.

print('computing tangency portfolio...')

# slow.
def risk_adjusted_return(w, rf, means, covars, assets):
    numerator = sum(w[a] * means[a] for a in assets)
    denominator = abs(sum(sum(w[a2] * covars[a1][a2] * w[a1] for a2 in assets) for a1 in assets))
    if not denominator > 0:
        print(denominator, w, covars)
    return (numerator - rf) / math.sqrt(denominator), numerator, denominator

def next_step(w, rf, means, covars, assets, epsilon = 0.00001):
    best_step = copy.copy(w)
    best_rar, best_numerator, best_denominator = risk_adjusted_return(best_step, rf, means, covars, assets)
    for i in assets:
        for j in assets:
            w[i] += epsilon
            w[j] -= epsilon
            rar, num, denom = risk_adjusted_return(w, rf, means, covars, assets)
            if rar > best_rar:
                best_step = copy.copy(w)
                best_rar = rar
                best_numerator = num
                best_denominator = denom
            w[i] -= epsilon
            w[j] += epsilon
    return best_step, best_rar, best_numerator, best_denominator

guess = {k : 1./len(assets) for k in assets}
numerators = []
denominators = []
for _ in range(10000):
    guess, rar, numerator, denominator = next_step(guess, RISKFREE_RATE, means, covariances, assets, 0.001)
    numerators.append(numerator)
    denominators.append(denominator)
for _ in range(10000):
    guess, rar, numerator, denominator = next_step(guess, RISKFREE_RATE, means, covariances, assets, 0.00001)
    numerators.append(numerator)
    denominators.append(denominator)
for _ in range(10000):
    guess, rar, numerator, denominator = next_step(guess, RISKFREE_RATE, means, covariances, assets, 0.0000001)
    numerators.append(numerator)
    denominators.append(denominator)

print(guess, rar, numerator, denominator)

plt.plot(denominators, numerators, 'bo')
plt.plot([0, denominator], [RISKFREE_RATE, numerator], 'g-')
plt.title('risk vs. returns')
plt.show()









