import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Sample historical data (dates, underlying stock prices)
data = {
    'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
    'Stock_Price': [100, 102, 105, 107, 110]
}

# Convert to DataFrame
df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Define a simple strategy
def generate_trade_signals(df, buy_threshold, sell_threshold):
    signals = pd.DataFrame(index=df.index)
    signals['Stock_Price'] = df['Stock_Price']
    signals['Buy_Signal'] = (df['Stock_Price'].diff() > buy_threshold).astype(int)
    signals['Sell_Signal'] = (df['Stock_Price'].diff() < -sell_threshold).astype(int)
    return signals

# Simulate trades based on signals
def simulate_trades(signals, strike_price, premium):
    trades = []
    position = 0
    buy_price = 0

    for i, row in signals.iterrows():
        if row['Buy_Signal'] and position == 0:
            position = 1
            buy_price = row['Stock_Price']
        elif row['Sell_Signal'] and position == 1:
            position = 0
            sell_price = row['Stock_Price']
            payoff = max(sell_price - strike_price, 0) - premium
            profit = payoff - (sell_price - buy_price)
            trades.append((buy_price, sell_price, payoff, profit))
    
    return trades

# Evaluate performance
def evaluate_performance(trades):
    if not trades:
        return {'Total_Profit': 0, 'Total_Trades': 0}

    total_profit = sum(trade[3] for trade in trades)
    total_trades = len(trades)

    return {'Total_Profit': total_profit, 'Total_Trades': total_trades}

# Example parameters
buy_threshold = 2
sell_threshold = 2
strike_price = 105
premium = 2

# Generate trade signals
signals = generate_trade_signals(df, buy_threshold, sell_threshold)

# Simulate trades
trades = simulate_trades(signals, strike_price, premium)

# Evaluate performance
performance = evaluate_performance(trades)
print(f"Total Profit: {performance['Total_Profit']}")
print(f"Total Trades: {performance['Total_Trades']}")

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(df.index, df['Stock_Price'], marker='o', linestyle='-', color='b', label='Stock Price')
plt.scatter(signals.index[signals['Buy_Signal'] == 1], df['Stock_Price'][signals['Buy_Signal'] == 1], color='g', marker='^', label='Buy Signal')
plt.scatter(signals.index[signals['Sell_Signal'] == 1], df['Stock_Price'][signals['Sell_Signal'] == 1], color='r', marker='v', label='Sell Signal')
plt.title('Stock Price and Trade Signals')
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.legend()
plt.show()
