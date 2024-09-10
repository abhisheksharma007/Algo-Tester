import pandas as pd
from strategies import get_strategy
import ipdb
import traceback

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
    
    try:
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
            if isinstance(date, pd.Series):
                date = date.iloc[0]
            date = date.strftime("%Y-%m-%d")
            
            spot_price = float(data.loc[date, 'Close'])

            if signal['positions'] == 1.0:  # Buy signal
                entry_price = spot_price
                position = portfolio.at[date, 'cash'] / entry_price
                trailing_stop_price = entry_price  # Initialize trailing stop price
                portfolio.at[date, 'holdings'] = position
                portfolio.at[date, 'cash'] = 0.0
                trades.append({'date': date, 'type': 'buy', 'price': entry_price, 'holdings': portfolio.at[date, 'holdings'], 'cash': portfolio.at[date, 'cash']})
            
            elif signal['positions'] == -1.0:  # Sell signal
                if position > 0:
                    exit_price = spot_price
                    profit_loss = (exit_price - entry_price) * position
                    portfolio.at[date, 'cash'] = position * exit_price
                    portfolio.at[date, 'holdings'] = 0.0
                    portfolio.at[date, 'total'] = portfolio.at[date, 'cash'] + portfolio.at[date, 'holdings']
                    trades.append({'date': date, 'type': 'sell', 'price': exit_price, 'profit_loss': profit_loss, 'holdings': portfolio.at[date, 'holdings'], 'cash': portfolio.at[date, 'cash']})
                    position = 0

            # Trailing stop loss logic
            if position > 0:
                if spot_price > trailing_stop_price:
                    trailing_stop_price = spot_price * (1 - stop_loss_percentage)
                elif spot_price < trailing_stop_price:
                    exit_price = spot_price
                    profit_loss = (exit_price - entry_price) * position
                    portfolio.at[date, 'cash'] = position * exit_price
                    portfolio.at[date, 'holdings'] = 0.0
                    portfolio.at[date, 'total'] = portfolio.at[date, 'cash'] + portfolio.at[date, 'holdings']
                    trades.append({'date': date, 'type': 'sell', 'price': exit_price, 'profit_loss': profit_loss, 'holdings': portfolio.at[date, 'holdings'], 'cash': portfolio.at[date, 'cash']})
                    position = 0


        final_value = portfolio['total'].iloc[-1]
        return final_value, trades
    except:
        print(traceback.format_exc())
