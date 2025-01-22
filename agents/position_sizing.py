from typing import Dict, List
import pandas as pd
import numpy as np

class PositionSizer:
    def __init__(self):
        self.sizing_methods = {
            "fixed_percent": self.fixed_percent_sizing,
            "volatility_targeting": self.volatility_targeting_sizing,
            "equal_risk": self.equal_risk_sizing,
            "inverse_volatility": self.inverse_volatility_weights,
            "kelly_criterion": self.kelly_sizing
        }
    
    def fixed_percent_sizing(self, data: pd.DataFrame, params: Dict) -> pd.Series:
        """Fixed percentage of portfolio per position"""
        position_size = params.get('position_size', 0.01)  # Default 1%
        return pd.Series(position_size, index=data.index)
    
    def volatility_targeting_sizing(self, data: pd.DataFrame, params: Dict) -> pd.Series:
        """Target a specific volatility level for position sizing"""
        target_vol = params.get('target_vol', 0.20)  # Target 20% annual vol
        lookback = params.get('lookback', 60)
        
        # Calculate asset volatility
        returns = data['Close'].pct_change(fill_method=None)
        vol = returns.rolling(lookback).std() * np.sqrt(252)
        
        # Size position inversely to volatility
        position_sizes = target_vol / vol
        
        # Apply maximum position size constraint
        max_size = params.get('max_size', 0.30)
        return position_sizes.clip(upper=max_size)
    
    def equal_risk_sizing(self, data: pd.DataFrame, params: Dict) -> pd.Series:
        """Size positions to contribute equal risk"""
        risk_per_trade = params.get('risk_per_trade', 0.01)  # 1% risk per trade
        atr_periods = params.get('atr_periods', 14)
        
        # Calculate ATR
        tr = pd.DataFrame()
        tr['h-l'] = data['High'] - data['Low']
        tr['h-pc'] = abs(data['High'] - data['Close'].shift(1))
        tr['l-pc'] = abs(data['Low'] - data['Close'].shift(1))
        atr = tr.max(axis=1).rolling(atr_periods).mean()
        
        # Position size = Risk Amount / (ATR * Price)
        position_sizes = risk_per_trade / (atr / data['Close'])
        
        return position_sizes
    
    def inverse_volatility_weights(self, assets_data: Dict[str, pd.DataFrame], params: Dict) -> Dict[str, pd.Series]:
        """Calculate position weights based on inverse volatility"""
        lookback = params.get('lookback', 60)
        
        # Calculate volatilities for each asset
        vols = {}
        for symbol, data in assets_data.items():
            returns = data['Close'].pct_change(fill_method=None)
            vols[symbol] = returns.rolling(lookback).std() * np.sqrt(252)
        
        # Calculate inverse volatility weights
        inv_vols = pd.DataFrame(vols)
        weights = 1 / inv_vols
        weights = weights.div(weights.sum(axis=1), axis=0)
        
        return {symbol: weights[symbol] for symbol in assets_data.keys()}
    
    def kelly_sizing(self, data: pd.DataFrame, params: Dict) -> pd.Series:
        """Kelly Criterion position sizing"""
        win_rate = params.get('win_rate', 0.5)
        profit_ratio = params.get('profit_ratio', 2.0)  # Avg Win / Avg Loss
        
        # Kelly fraction = (bp - q)/b where:
        # b = profit ratio
        # p = win rate
        # q = loss rate (1-p)
        kelly_fraction = (profit_ratio * win_rate - (1 - win_rate)) / profit_ratio
        
        # Usually use half-kelly for safety
        return pd.Series(kelly_fraction * 0.5, index=data.index) 