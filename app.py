from flask import Flask, render_template, request
from pricing import *
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        S = float(request.form.get('stock_price'))
        K = float(request.form.get('strike_price'))
        T = float(request.form.get('expiry_time')) / 365
        r = float(request.form.get('interest_rate'))
        sigma = float(request.form.get('volatility'))

        results = {
            'call_price': call_price(S, K, T, r, sigma),
            'put_price': put_price(S, K, T, r, sigma),
            'delta_call': delta_call(S, K, T, r, sigma),
            'delta_put': delta_put(S, K, T, r, sigma),
            'gamma': gamma(S, K, T, r, sigma),
            'vega': vega(S, K, T, r, sigma),
            'theta_call': theta_call(S, K, T, r, sigma) / 365,
            'theta_put': theta_put(S, K, T, r, sigma) / 365,
        }

        call_prices, call_profits = payoff_data(S, K, results['call_price'], option_type = 'call')
        put_prices, put_profits = payoff_data(S, K, results['put_price'], option_type = 'put')

        results['call_prices'] = call_prices
        results['put_prices'] = put_prices
        results['call_profits'] = call_profits
        results['put_profits'] = put_profits

    return render_template('index.html', results = results)

@app.route('/compare', methods = ['GET', 'POST'])
def compare():
    comparison = None
    error = None
    if request.method == 'POST':
        symbol = request.form.get('ticker').upper()
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period="1d")['Close'].iloc[-1]

            today = datetime.today()
            nearest_expiry = None
            for date_str in ticker.options:
                expiry_date = datetime.strptime(date_str, "%Y-%m-%d")
                if (expiry_date - today).days >= 7:
                    nearest_expiry = date_str
                    break

            chain = ticker.option_chain(nearest_expiry)
            calls = chain.calls

            near = calls[(calls['strike'] > current_price * 0.95) & (calls['strike'] < current_price * 1.05)]

            near = near.copy()
            near['diff'] = abs(near['strike'] - current_price)
            closest = near.loc[near['diff'].idxmin()]

            expiry_date = datetime.strptime(nearest_expiry, "%Y-%m-%d")
            days_to_expiry = (expiry_date - today).days
            T = days_to_expiry / 365

            K = closest['strike']
            sigma = closest['impliedVolatility']
            market_price = closest['lastPrice']

            r = 0.05

            my_price = call_price(current_price, K, T, r, sigma)

            comparison = {
                'symbol': symbol,
                'current_price': round(current_price, 2),
                'strike': K,
                'expiry': nearest_expiry,
                'my_price': round(my_price, 2),
                'market_price': market_price,
                'difference': round(my_price - market_price, 2),
            }
        except Exception as e:
            error = f"Couldn't find data for '{symbol}'. Please check the ticker symbol as try again."
    
    return render_template('compare.html', comparison = comparison, error = error)

if __name__ == '__main__':
    app.run(debug = True)