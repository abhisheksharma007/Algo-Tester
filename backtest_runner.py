import pandas as pd
from strategies import get_strategy

def run_backtest(data, initial_investment, stop_loss_percentage, strategy_name, strategy_params):
    """
    Run backtest using the selected strategy.
    :param data: Historical data
    :param initial_investment: Initial amount of money for trading
    :param stop_loss_percentage: Percentage for stop loss
    :param strategy_name: Name of the selected strategy
    :param strategy_params: Parameters for the selected strategy
    :return: final_value, trades
    """
    # Get strategy function
    strategy_func = get_strategy(strategy_name)
    
    # Apply the selected strategy
    signals = strategy_func(data, **strategy_params)

    # Initialize portfolio variables
    portfolio = pd.DataFrame(index=data.index)
    portfolio['holdings'] = 0.0
    portfolio['cash'] = initial_investment
    portfolio['total'] = initial_investment

    position = 0
    entry_price = 0
    trades = []
    trailing_stop_price = 0

    for date, signal in signals.iterrows():
        if signal['positions'] == 1.0:  # Buy signal
            position = portfolio['cash'] / data.loc[date, 'Close']
            entry_price = data.loc[date, 'Close']
            trailing_stop_price = entry_price  # Initialize trailing stop price
            portfolio.at[date, 'holdings'] = position
            portfolio.at[date, 'cash'] = 0.0
            trades.append({'date': date, 'type': 'buy', 'price': entry_price})
        
        elif signal['positions'] == -1.0:  # Sell signal
            if position > 0:
                exit_price = data.loc[date, 'Close']
                profit_loss = (exit_price - entry_price) * position
                portfolio.at[date, 'cash'] = position * exit_price
                portfolio.at[date, 'holdings'] = 0.0
                portfolio.at[date, 'total'] = portfolio.at[date, 'cash'] + portfolio.at[date, 'holdings']
                trades.append({'date': date, 'type': 'sell', 'price': exit_price, 'profit_loss': profit_loss})
                position = 0

        # Trailing stop loss logic
        if position > 0:
            if data.loc[date, 'Close'] > trailing_stop_price:
                trailing_stop_price = data.loc[date, 'Close'] * (1 - stop_loss_percentage)
            elif data.loc[date, 'Close'] < trailing_stop_price:
                exit_price = data.loc[date, 'Close']
                profit_loss = (exit_price - entry_price) * position
                portfolio.at[date, 'cash'] = position * exit_price
                portfolio.at[date, 'holdings'] = 0.0
                portfolio.at[date, 'total'] = portfolio.at[date, 'cash'] + portfolio.at[date, 'holdings']
                trades.append({'date': date, 'type': 'sell', 'price': exit_price, 'profit_loss': profit_loss})
                position = 0

    final_value = portfolio['total'].iloc[-1]
    return final_value, trades
