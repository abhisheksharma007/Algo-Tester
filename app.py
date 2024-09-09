import streamlit as st
from datetime import datetime
from data_fetcher import fetch_data
from backtest_runner import run_backtest
from strategies import STRATEGIES

# Streamlit UI
st.title('Algorithm Backtesting App with Custom Strategy')

# Input parameters
ticker = st.text_input('Ticker Symbol', 'TCS')
market = st.selectbox('Market', ['NSE', 'BSE'], index=0)
start_date = st.date_input('Start Date', datetime(2020, 1, 1))
end_date = st.date_input('End Date', datetime.today())
initial_investment = st.number_input('Initial Investment (INR)', value=10000, step=100)
stop_loss_percentage = st.number_input('Stop Loss Percentage (%)', value=10, step=1) / 100

# Strategy selection
strategy_name = st.selectbox('Select Strategy', list(STRATEGIES.keys()), index=0)

# Strategy-specific parameters
strategy_params = {}
if strategy_name == 'SMA Crossover':
    short_window = st.number_input('Short Window', value=40)
    long_window = st.number_input('Long Window', value=100)
    strategy_params = {'short_window': short_window, 'long_window': long_window}
elif strategy_name == 'RSI':
    period = st.number_input('RSI Period', value=14)
    threshold = st.number_input('RSI Threshold', value=30)
    strategy_params = {'period': period, 'threshold': threshold}
elif strategy_name == 'MACD':
    short_window = st.number_input('MACD Short Window', value=12)
    long_window = st.number_input('MACD Long Window', value=26)
    signal_window = st.number_input('MACD Signal Window', value=9)
    strategy_params = {'short_window': short_window, 'long_window': long_window, 'signal_window': signal_window}

if st.button('Run Backtest'):
    # Fetch data
    data = fetch_data(ticker, market, start_date, end_date)

    if data.empty:
        st.error('No data found for the provided ticker and date range.')
    else:
        # Run backtest with custom strategy
        final_value, trades = run_backtest(data, initial_investment, stop_loss_percentage, strategy_name, strategy_params)

        # Output the results
        st.write(f"Final Portfolio Value: ₹{final_value:,.2f}")

        # Display trades
