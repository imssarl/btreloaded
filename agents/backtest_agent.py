from typing import Dict, List
import pandas as pd
import numpy as np
from utils.assistant import Assistant
from .position_sizing import PositionSizer
from utils.rule_implementations import RULE_IMPLEMENTATIONS

class BacktestAgent(Assistant):
    def __init__(self):
        super().__init__(
            name="Backtest Agent",
            description="Strategy backtesting engine",
            instructions="Execute trading strategies and generate results"
        )
    
    def run_backtest(self, data: Dict[str, pd.DataFrame], strategy_spec: Dict) -> Dict:
        try:
            symbol = list(data.keys())[0]
            df = data[symbol]
            
            # Execute strategy
            signals = self._execute_strategy(df, strategy_spec['signal_code'])
            print(f"Generated signals shape: {signals.shape}")
            
            positions = self._apply_position_sizing(df, signals, strategy_spec['sizing_code'])
            print(f"Generated positions shape: {positions.shape}")
            
            trades = self._generate_trades(df, positions)
            print(f"Generated trades shape: {trades.shape}")
            
            equity_curve = self._calculate_equity_curve(df, positions)
            print(f"Generated equity curve shape: {equity_curve.shape}")
            
            # Ensure equity_curve is a Series with datetime index
            if isinstance(equity_curve, pd.DataFrame):
                equity_curve = equity_curve.iloc[:, 0]
            equity_curve.index = pd.to_datetime(equity_curve.index)
            
            # Ensure trades DataFrame has required columns
            if len(trades) > 0:
                required_columns = ['pnl', 'hold_time']
                for col in required_columns:
                    if col not in trades.columns:
                        print(f"Warning: Missing column {col} in trades DataFrame")
            
            return {
                'status': 'success',
                'trades': trades,
                'equity_curve': equity_curve,
                'positions': positions
            }
        except Exception as e:
            print(f"Backtest error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _execute_strategy(self, data: pd.DataFrame, signal_code: str) -> pd.DataFrame:
        print("\nExecuting Strategy:")
        print(f"Data shape: {data.shape}")
        print(f"Data columns: {data.columns.tolist()}")
        print(f"Signal code:\n{signal_code}")
        
        namespace = {
            'pd': pd,
            'np': np,
            'data': data,
            'RULE_IMPLEMENTATIONS': RULE_IMPLEMENTATIONS
        }
        
        # Execute the strategy code in the namespace
        exec(signal_code, globals(), namespace)
        signals = namespace['calculate_signals'](data)
        
        print(f"Generated signals shape: {signals.shape}")
        print(f"Signals head:\n{signals.head()}")
        return signals
    
    def _apply_position_sizing(self, data: pd.DataFrame, signals: pd.DataFrame, sizing_code: str) -> pd.DataFrame:
        # Create a namespace with required modules and data
        namespace = {
            'pd': pd,
            'np': np,
            'data': data,
            'signals': signals,
            'PositionSizer': PositionSizer  # Add this
        }
        
        # Execute the sizing code in the namespace
        exec(sizing_code, globals(), namespace)
        
        # Call the calculate_position_sizes function from the namespace
        return namespace['calculate_position_sizes'](data, signals)
    
    def _generate_trades(self, data: pd.DataFrame, positions: pd.Series) -> pd.DataFrame:
        trades = []
        current_position = 0
        entry_price = None
        entry_date = None
        
        for date, position in positions.items():
            if position != current_position:
                # Calculate PnL if closing or modifying position
                if current_position != 0:
                    price = data.loc[date, 'Close']
                    pnl = (price - entry_price) * current_position
                    hold_time = (date - entry_date).days
                else:
                    pnl = 0.0
                    hold_time = 0
                
                trade = {
                    'date': date,
                    'price': data.loc[date, 'Close'],
                    'size': position - current_position,
                    'direction': 'BUY' if position > current_position else 'SELL',
                    'position': position,
                    'pnl': pnl,
                    'hold_time': hold_time
                }
                trades.append(trade)
                
                # Update entry price and date for new position
                if position != 0:
                    entry_price = data.loc[date, 'Close']
                    entry_date = date
                current_position = position
        
        trades_df = pd.DataFrame(trades)
        if len(trades_df) > 0:
            trades_df.set_index('date', inplace=True)
        return trades_df
    
    def _calculate_equity_curve(self, data: pd.DataFrame, positions: pd.Series) -> pd.Series:
        print("\nCalculating Equity Curve:")
        print(f"Initial data shape: {data.shape}")
        print(f"Positions shape: {positions.shape}")
        
        equity = pd.Series(1.0, index=data.index)
        
        if len(positions) == 0:
            print("Warning: No positions to calculate equity curve")
            return equity
        
        returns = data['Close'].pct_change(fill_method=None).fillna(0)  # Fill NaN with 0 for first day
        for date in data.index[1:]:
            prev_date = data.index[data.index.get_loc(date)-1]
            if pd.isna(positions.loc[date]) or pd.isna(returns.loc[date]):
                equity.loc[date] = equity.loc[prev_date]  # Keep previous value if NaN
            else:
                equity.loc[date] = equity.loc[prev_date] * (1 + positions.loc[date] * returns.loc[date])
        
        print(f"Final equity curve shape: {equity.shape}")
        print(f"Equity curve head:\n{equity.head()}")
        return equity 