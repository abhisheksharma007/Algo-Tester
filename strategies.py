# strategies/macd.py
import pandas as pd

def macd_strategy(data, short_window=12, long_window=26, signal_window=9):
    signals = pd.DataFrame(index=data.index)
    signals['ema_short'] = data['Close'].ewm(span=short_window, min_periods=1, adjust=False).mean()
    signals['ema_long'] = data['Close'].ewm(span=long_window, min_periods=1, adjust=False).mean()
    signals['macd'] = signals['ema_short'] - signals['ema_long']
    signals['signal_line'] = signals['macd'].ewm(span=signal_window, min_periods=1, adjust=False).mean()
    signals['signal'] = (signals['macd'] > signals['signal_line']).astype(float)
    signals['positions'] = signals['signal'].diff()
    return signals

def rsi_strategy(data, period=14, threshold=30):
    signals = pd.DataFrame(index=data.index)
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period, min_periods=1).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period, min_periods=1).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    signals['signal'] = (rsi < threshold).astype(float)
    signals['positions'] = signals['signal'].diff()
    return signals

def sma_crossover(data, short_window=40, long_window=100):
    signals = pd.DataFrame(index=data.index)
    signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()
    signals['signal'] = 0.0
    signals['signal'][short_window:] = (signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:]).astype(float)
    signals['positions'] = signals['signal'].diff()
    return signals



STRATEGIES = {
    'MACD' : macd_strategy,
    'RSI' : rsi_strategy,
    'SMA Crossover' : sma_crossover,
}

def get_strategy(name):
    """
    Get the strategy function by name.
    """
    if name not in STRATEGIES.keys():
        raise ValueError(f"Strategy {name} not found.")
    return STRATEGIES[name]
