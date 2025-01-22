"""
Implementation of trading rules for each category.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def calculate_zscore_momentum(data: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
    """Calculate z-score momentum signal."""
    lookback = params['lookback']
    threshold = params['threshold']
    
    # Calculate returns
    returns = data['Close'].pct_change(lookback)
    
    # Calculate z-score
    zscore = (returns - returns.rolling(lookback).mean()) / returns.rolling(lookback).std()
    
    # Generate signal (-1 for short, 0 for neutral, 1 for long)
    signal = pd.Series(0, index=data.index)
    signal[zscore > threshold] = 1
    signal[zscore < -threshold] = -1
    
    return signal

def calculate_roc(data: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
    """Calculate rate of change signal."""
    lookback = params['lookback']
    threshold = params['threshold']
    
    # Calculate rate of change
    roc = data['Close'].pct_change(lookback) * 100
    
    # Generate signal
    signal = pd.Series(0, index=data.index)
    signal[roc > threshold] = 1
    signal[roc < -threshold] = -1
    
    return signal

def calculate_channel_breakout(data: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
    """Calculate channel breakout signal."""
    lookback = params['lookback']
    channel_width = params['channel_width']
    
    # Calculate upper and lower channels
    rolling_high = data['High'].rolling(lookback).max()
    rolling_low = data['Low'].rolling(lookback).min()
    channel_mid = (rolling_high + rolling_low) / 2
    channel_range = rolling_high - rolling_low
    
    upper_channel = channel_mid + (channel_width * channel_range / 2)
    lower_channel = channel_mid - (channel_width * channel_range / 2)
    
    # Generate signal
    signal = pd.Series(0, index=data.index)
    signal[data['Close'] > upper_channel] = 1
    signal[data['Close'] < lower_channel] = -1
    
    return signal

def calculate_support_resistance(data: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
    """Calculate support/resistance breakout signal."""
    lookback = params['lookback']
    threshold = params['threshold']
    
    # Calculate support and resistance levels
    rolling_high = data['High'].rolling(lookback).max()
    rolling_low = data['Low'].rolling(lookback).min()
    
    # Calculate percentage distance from levels
    dist_from_high = (rolling_high - data['Close']) / data['Close']
    dist_from_low = (data['Close'] - rolling_low) / data['Close']
    
    # Generate signal
    signal = pd.Series(0, index=data.index)
    signal[dist_from_high < threshold/100] = 1  # Breaking resistance
    signal[dist_from_low < threshold/100] = -1  # Breaking support
    
    return signal

def calculate_sma_crossover(data: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
    """Calculate SMA crossover signal."""
    fast_period = params['fast_period']
    slow_period = params['slow_period']
    
    # Calculate SMAs
    fast_sma = data['Close'].rolling(fast_period).mean()
    slow_sma = data['Close'].rolling(slow_period).mean()
    
    # Generate signal
    signal = pd.Series(0, index=data.index)
    signal[fast_sma > slow_sma] = 1
    signal[fast_sma < slow_sma] = -1
    
    return signal

def calculate_ema_crossover(data: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
    """Calculate EMA crossover signal."""
    fast_period = params['fast_period']
    slow_period = params['slow_period']
    
    # Calculate EMAs
    fast_ema = data['Close'].ewm(span=fast_period, adjust=False).mean()
    slow_ema = data['Close'].ewm(span=slow_period, adjust=False).mean()
    
    # Generate signal
    signal = pd.Series(0, index=data.index)
    signal[fast_ema > slow_ema] = 1
    signal[fast_ema < slow_ema] = -1
    
    return signal

def calculate_atr_breakout(data: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
    """Calculate ATR breakout signal."""
    lookback = params['lookback']
    multiplier = params['multiplier']
    
    # Calculate ATR
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(lookback).mean()
    
    # Calculate bands
    middle = data['Close'].rolling(lookback).mean()
    upper = middle + (multiplier * atr)
    lower = middle - (multiplier * atr)
    
    # Generate signal
    signal = pd.Series(0, index=data.index)
    signal[data['Close'] > upper] = 1
    signal[data['Close'] < lower] = -1
    
    return signal

def calculate_volatility_regime(data: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
    """Calculate volatility regime signal."""
    lookback = params['lookback']
    threshold = params['threshold']
    
    # Calculate historical volatility
    returns = data['Close'].pct_change()
    vol = returns.rolling(lookback).std() * np.sqrt(252)  # Annualized
    
    # Calculate average volatility
    avg_vol = vol.rolling(lookback).mean()
    
    # Generate signal
    signal = pd.Series(0, index=data.index)
    signal[vol < avg_vol / threshold] = 1  # Low volatility regime
    signal[vol > avg_vol * threshold] = -1  # High volatility regime
    
    return signal

# Map rule types to their implementation functions
RULE_IMPLEMENTATIONS = {
    'zscore': calculate_zscore_momentum,
    'roc': calculate_roc,
    'channel': calculate_channel_breakout,
    'support_resistance': calculate_support_resistance,
    'sma_crossover': calculate_sma_crossover,
    'ema_crossover': calculate_ema_crossover,
    'atr_breakout': calculate_atr_breakout,
    'volatility_regime': calculate_volatility_regime
} 