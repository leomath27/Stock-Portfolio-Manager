import pickle
import yfinance as yf
import mplfinance as mpf
import datetime as dt
import sys
import json
import re

try:
    with open('portfolio.pkl', 'rb') as f:
        portfolio = pickle.load(f)
except FileNotFoundError:
    portfolio = {}

def save_portfolio():
    with open('portfolio.pkl', 'wb') as f:
        pickle.dump(portfolio, f)

def download_stock_data(ticker, start=None, end=None):
    return yf.download(ticker, start=start, end=end if end else dt.datetime.now())

def add_to_portfolio():
    ticker = input("What stock do you want to add: ").upper()
    try:
        amount = int(input("How many shares do you want to add: "))
    except ValueError:
        print("Please enter a valid number of shares.")
        return

    portfolio[ticker] = portfolio.get(ticker, 0) + amount
    save_portfolio()

def remove_from_portfolio():
    ticker = input("What stock do you want to sell: ").upper()
    try:
        amount = int(input("How many shares do you want to sell: "))
    except ValueError:
        print("Please enter a valid number of shares.")
        return

    if ticker in portfolio and amount <= portfolio[ticker]:
        portfolio[ticker] -= amount
        if portfolio[ticker] == 0:
            del portfolio[ticker]
        save_portfolio()
    else:
        print(f"You don't have enough shares of {ticker}.")

def show_portfolio():
    for ticker, shares in portfolio.items():
        print(f"You own {shares} shares of {ticker}")

def portfolio_worth():
    total_value = 0
    for ticker in portfolio:
        data = download_stock_data(ticker, period='1d')
        price = data['Close'].iloc[-1]
        total_value += price * portfolio[ticker]
    print(f"Your portfolio is worth ${total_value:.2f} USD")

def portfolio_gains():
    starting_date = input("Enter a trading date for comparison (YYYY-MM-DD): ")
    try:
        dt.datetime.strptime(starting_date, '%Y-%m-%d')
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    sum_now, sum_then = 0, 0
    try:
        for ticker in portfolio:
            data = download_stock_data(ticker, start=starting_date)
            price_now = data['Close'].iloc[-1]
            price_then = data.loc[data.index == starting_date]['Close'].values[0]
            sum_now += price_now * portfolio[ticker]
            sum_then += price_then * portfolio[ticker]

        print(f"Relative Gains: {((sum_now - sum_then) / sum_then) * 100:.2f}%")
        print(f"Absolute Gains: ${sum_now - sum_then:.2f} USD")
    except IndexError:
        print("There was no trading on this day!")

def plot_chart():
    ticker = input('Choose a ticker symbol: ').upper()
    starting_string = input("Enter a starting date (DD/MM/YYYY): ")

    try:
        start = dt.datetime.strptime(starting_string, "%d/%m/%Y")
    except ValueError:
        print("Invalid date format. Please use DD/MM/YYYY.")
        return

    data = download_stock_data(ticker, start=start)

    colors = mpf.make_marketcolors(up='#00ff00', down='#ff0000', wick='inherit', edge='inherit', volume='inherit')
    style = mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=colors)

    mpf.plot(data, type='candle', volume=True, style=style)

def bye():
    print('Goodbye')
    sys.exit(0)

mappings = {
    'plot_chart': plot_chart,
    'add_to_portfolio': add_to_portfolio,
    'remove_from_portfolio': remove_from_portfolio,
    'show_portfolio': show_portfolio,
    'portfolio_worth': portfolio_worth,
    'portfolio_gains': portfolio_gains,
    'bye': bye
}

def load_intents():
    with open('intents.json', 'r') as f:
        return json.load(f)

def get_intent(user_input, intents):
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            if re.search(pattern.lower(), user_input.lower()):
                return intent['tag']
    return None

intents = load_intents()

while True:
    print("\nOptions:")
    for key in mappings:
        print(f"- {key}")
    user_input = input("What would you like to do? ").strip()

    intent = get_intent(user_input, intents)
    if intent in mappings:
        mappings[intent]()
    else:
        print("I'm sorry, I didn't understand that. Please try again.")
