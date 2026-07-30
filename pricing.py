import math
from scipy.stats import norm

def d1_d2(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + (sigma ** 2)/2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return d1, d2

def call_price(S, K, T, r, sigma):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    a = S * norm.cdf(d1)
    b = K * math.exp(-r * T) * norm.cdf(d2)
    C = a - b
    return C

def put_price(S, K, T, r, sigma):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    a = K * math.exp(-r * T) * norm.cdf(-d2)
    b = S * norm.cdf(-d1)
    P = a - b
    return P

def delta_call(S, K, T, r, sigma):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    delta = norm.cdf(d1)
    return delta

def delta_put(S, K, T, r, sigma):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    delta = norm.cdf(d1) - 1
    return delta

def gamma(S, K, T, r, sigma):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    a = norm.pdf(d1)
    b = S * sigma * math.sqrt(T)
    G = a / b
    return G

def vega(S, K, T, r, sigma):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    v = S * norm.pdf(d1) * math.sqrt(T)
    scaled_v = v / 100
    return scaled_v

def theta_call(S, K, T, r, sigma):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    a = (S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T))
    b = r * K * math.exp(-r * T) * norm.cdf(d2)
    theta = -a - b
    return theta

def theta_put(S, K, T, r, sigma):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    a = (S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T))
    b = r * K * math.exp(-r * T) * norm.cdf(-d2)
    theta = -a + b
    return theta

def payoff_data(S, K, premium, option_type = 'call', range_pct = 0.5, steps = 50):
    prices =[]
    profits = []
    low = S * (1 - range_pct)
    high = S * (1 + range_pct)
    step_size = (high - low) / steps

    for i in range(steps + 1):
        price = low + i * step_size
        if option_type == 'call':
            payoff = max(price - K, 0)
        else:
            payoff = max(K - price, 0)
        profit = payoff - premium
        prices.append(round(price, 2))
        profits.append(round(profit, 2))

    return prices, profits

