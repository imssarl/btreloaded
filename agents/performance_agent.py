from typing import Dict, List
import pandas as pd
import numpy as np
from utils.assistant import Assistant
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class PerformanceAgent(Assistant):
    def __init__(self):
        super().__init__(
            name="Performance Agent",
            description="Performance analysis and reporting",
            instructions="Analyze trading performance and generate reports"
        )
    
    def analyze_performance(self, equity_curve: pd.Series, trades: pd.DataFrame) -> Dict:
        """Generate comprehensive performance analysis"""
        print(f"Analyzing performance:")
        print(f"Equity curve shape: {equity_curve.shape}")
        print(f"Trades shape: {trades.shape}")
        print(f"Trades columns: {trades.columns.tolist() if not trades.empty else 'No trades'}")
        
        metrics = self.calculate_metrics(equity_curve)
        print(f"Calculated metrics: {metrics}")
        
        trade_stats = self.analyze_trades(trades)
        print(f"Calculated trade stats: {trade_stats}")
        
        charts = self.generate_charts(equity_curve)
        print("Generated charts")
        
        return {
            "metrics": metrics,
            "trade_stats": trade_stats,
            "charts": charts
        }
    
    def calculate_metrics(self, equity_curve: pd.Series) -> Dict:
        """Calculate performance metrics with proper error handling"""
        try:
            returns = equity_curve.pct_change(fill_method=None).dropna()
            
            # Basic return calculations
            total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0] - 1) * 100
            annual_return = returns.mean() * 252 * 100
            volatility = returns.std() * np.sqrt(252) * 100
            
            # Risk-adjusted metrics
            sharpe_ratio = annual_return / volatility if volatility != 0 else 0
            max_drawdown = ((equity_curve / equity_curve.expanding().max() - 1).min()) * 100
            calmar_ratio = abs(annual_return / max_drawdown) if max_drawdown != 0 else 0
            sortino = self.calculate_sortino(returns)
            
            metrics = {
                "Total Return (%)": round(total_return, 2),
                "Annual Return (%)": round(annual_return, 2),
                "Volatility (%)": round(volatility, 2),
                "Sharpe Ratio": round(sharpe_ratio, 2),
                "Max Drawdown (%)": round(max_drawdown, 2),
                "Calmar Ratio": round(calmar_ratio, 2),
                "Sortino Ratio": round(sortino, 2)
            }
            return metrics
        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
            return {
                "Total Return (%)": 0,
                "Annual Return (%)": 0,
                "Volatility (%)": 0,
                "Sharpe Ratio": 0,
                "Max Drawdown (%)": 0,
                "Calmar Ratio": 0,
                "Sortino Ratio": 0
            }
    
    def analyze_trades(self, trades: pd.DataFrame) -> Dict:
        """Analyze individual trades"""
        if len(trades) == 0:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "profit_factor": 0,
                "avg_hold_time": 0
            }
        
        try:
            winning_trades = trades[trades['pnl'] > 0]
            losing_trades = trades[trades['pnl'] < 0]
            
            # Add debug prints
            print(f"\nTrade Analysis Debug:")
            print(f"Total trades: {len(trades)}")
            print(f"Winning trades: {len(winning_trades)}")
            print(f"Losing trades: {len(losing_trades)}")
            
            stats = {
                "total_trades": len(trades),
                "win_rate": len(winning_trades) / len(trades) * 100 if len(trades) > 0 else 0,
                "avg_win": winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0,
                "avg_loss": losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0,
                "profit_factor": abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 and losing_trades['pnl'].sum() != 0 else float('inf'),
                "avg_hold_time": trades['hold_time'].mean()
            }
            return stats
        except Exception as e:
            print(f"Error analyzing trades: {str(e)}")
            return {
                "total_trades": len(trades),
                "win_rate": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "profit_factor": 0,
                "avg_hold_time": 0
            }
    
    def generate_charts(self, equity_curve: pd.Series) -> go.Figure:
        """Generate enhanced performance visualizations"""
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Equity Curve', 'Drawdown', 'Monthly Returns'),
            vertical_spacing=0.12,
            row_heights=[0.5, 0.25, 0.25]
        )
        
        # Equity curve
        fig.add_trace(
            go.Scatter(
                x=equity_curve.index,
                y=equity_curve,
                name='Equity',
                line=dict(color='#00b3b3', width=2)
            ),
            row=1, col=1
        )
        
        # Drawdown
        drawdown = equity_curve / equity_curve.expanding().max() - 1
        fig.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown * 100,
                name='Drawdown',
                fill='tonexty',
                line=dict(color='#ff3333', width=1)
            ),
            row=2, col=1
        )
        
        # Monthly returns
        monthly_returns = equity_curve.resample('ME').last().pct_change(fill_method=None) * 100
        fig.add_trace(
            go.Bar(
                x=monthly_returns.index,
                y=monthly_returns,
                name='Monthly Returns',
                marker_color=monthly_returns.apply(lambda x: '#00b3b3' if x >= 0 else '#ff3333')
            ),
            row=3, col=1
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=True,
            template='plotly_dark',
            title_text="Strategy Performance",
            title_x=0.5,
            title_font_size=20
        )
        
        # Update y-axes labels
        fig.update_yaxes(title_text="Value ($)", row=1, col=1)
        fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
        fig.update_yaxes(title_text="Return (%)", row=3, col=1)
        
        return fig

    def calculate_sortino(self, returns: pd.Series) -> float:
        """Calculate Sortino ratio (using 0% as minimum acceptable return)"""
        if len(returns) == 0:
            return 0.0
        
        # Calculate downside returns (returns below 0)
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf')  # No downside volatility
        
        # Calculate downside deviation (annualized)
        downside_std = np.sqrt(252) * np.sqrt(np.mean(downside_returns**2))
        
        # Calculate annualized return
        annualized_return = returns.mean() * 252
        
        return annualized_return / downside_std 