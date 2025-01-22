from typing import Dict, List
import pandas as pd
import yfinance as yf
import numpy as np
from utils.assistant import Assistant

class DataAgent(Assistant):
    def __init__(self):
        super().__init__(
            name="Data Agent",
            description="Financial data retrieval and preprocessing agent",
            instructions="Fetch and preprocess financial data"
        )
    
    def fetch_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch historical data for a given symbol using Yahoo Finance periods
        
        Args:
            symbol: Stock symbol
            period: Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            if len(df) == 0:
                return f"No data found for symbol {symbol}"
            return self.preprocess_data(df)
        except Exception as e:
            return f"Error fetching data: {str(e)}"
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the data"""
        df = df.ffill()
        df['Returns'] = df['Close'].pct_change(fill_method=None)
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        return df 