"""
Strategy generation and management.
"""

from typing import Dict, List
import pandas as pd
import numpy as np
from utils.assistant import Assistant
from .position_sizing import PositionSizer
from utils.rule_implementations import RULE_IMPLEMENTATIONS

class StrategyAgent(Assistant):
    def __init__(self):
        super().__init__(
            name="Strategy Agent",
            description="Trading strategy generator",
            instructions="Generate and manage trading strategies"
        )
        self.position_sizer = PositionSizer()
    
    def generate_complete_strategy(self, strategy_spec: Dict) -> Dict:
        """Generate complete strategy code based on specification."""
        if strategy_spec['type'] == 'combined':
            return self._generate_combined_strategy_code(strategy_spec)
        else:
            raise ValueError(f"Unknown strategy type: {strategy_spec['type']}")
    
    def _generate_combined_strategy_code(self, strategy_spec: Dict) -> Dict:
        """Generate code for a combined strategy using multiple rules."""
        categories = strategy_spec['categories']
        
        # Generate the strategy calculation code
        return {
            'signal_code': self._generate_signal_code(categories),
            'sizing_code': self._generate_position_sizing_code(strategy_spec['position_sizing'])
        }
    
    def _generate_signal_code(self, categories: Dict) -> str:
        """Generate code for calculating combined signals from all rules."""
        code = """
def calculate_signals(data):
    import pandas as pd
    import numpy as np
    from utils.rule_implementations import RULE_IMPLEMENTATIONS
    
    # Initialize final signal
    final_signal = pd.Series(0, index=data.index)
    total_weight = 0
    
    # Calculate signals for each category and rule
"""
        
        # Add code for each category
        for category_key, config in categories.items():
            category_weight = config['weight']
            rules = config['rules']
            
            code += f"""
    # {category_key.title()} signals
    category_signal = pd.Series(0, index=data.index)
    category_weight = {category_weight}
    total_weight += category_weight
"""
            
            # Add code for each rule in the category
            for rule in rules:
                rule_type = rule['type']
                rule_params = rule['parameters']
                rule_weight = rule_params.get('weight', 1.0)
                
                # Remove weight from parameters passed to rule implementation
                calc_params = {k: v for k, v in rule_params.items() if k != 'weight'}
                
                code += f"""
    # Calculate {rule_type} signal
    rule_signal = RULE_IMPLEMENTATIONS['{rule_type}'](data, {calc_params})
    category_signal += rule_signal * {rule_weight}
"""
            
            code += """
    # Normalize category signal
    category_signal = np.sign(category_signal)  # Convert to -1, 0, 1
    final_signal += category_signal * category_weight
"""
        
        code += """
    # Normalize final signal
    if total_weight > 0:
        final_signal = final_signal / total_weight
    
    return final_signal
"""
        
        return code
    
    def _generate_position_sizing_code(self, position_sizing: Dict) -> str:
        """Generate code for position sizing calculations."""
        method = position_sizing['method']
        params = position_sizing['params']
        
        if method == "volatility_targeting":
            return f"""
def calculate_position_sizes(data, signals):
    # Calculate volatility
    returns = data['Close'].pct_change()
    vol = returns.rolling({params['lookback']}).std() * np.sqrt(252)
    
    # Calculate position sizes
    target_vol = {params['target_vol']}
    max_size = {params['max_size']}
    
    # Position size = target vol / current vol
    position_sizes = signals * (target_vol / vol)
    
    # Apply maximum position size
    position_sizes = position_sizes.clip(-max_size, max_size)
    
    return position_sizes
"""
        elif method == "fixed_percentage":
            return f"""
def calculate_position_sizes(data, signals):
    # Fixed percentage position sizing
    position_size = {params['position_size']}
    
    # Apply the fixed size to signals
    position_sizes = signals * position_size
    
    return position_sizes
"""
        elif method == "equal_risk":
            return f"""
def calculate_position_sizes(data, signals):
    # Calculate ATR
    tr = pd.DataFrame()
    tr['h-l'] = data['High'] - data['Low']
    tr['h-pc'] = abs(data['High'] - data['Close'].shift(1))
    tr['l-pc'] = abs(data['Low'] - data['Close'].shift(1))
    atr = tr.max(axis=1).rolling({params['atr_periods']}).mean()
    
    # Calculate position sizes based on risk per trade
    risk_amount = {params['risk_per_trade']}
    position_sizes = signals * (risk_amount / (atr / data['Close']))
    
    return position_sizes
"""
        elif method == "inverse_volatility":
            return f"""
def calculate_position_sizes(data, signals):
    # Calculate volatility
    returns = data['Close'].pct_change()
    vol = returns.rolling({params['lookback']}).std() * np.sqrt(252)
    
    # Calculate inverse volatility position sizes
    position_sizes = signals * (1 / vol)
    
    # Normalize and apply maximum size
    max_size = {params['max_size']}
    position_sizes = position_sizes / vol.mean()  # Normalize to average volatility
    position_sizes = position_sizes.clip(-max_size, max_size)
    
    return position_sizes
"""
        elif method == "kelly_criterion":
            return f"""
def calculate_position_sizes(data, signals):
    # Kelly Criterion parameters
    win_rate = {params['win_rate']}
    profit_ratio = {params['profit_ratio']}
    max_size = {params['max_size']}
    
    # Kelly fraction = (bp - q)/b where:
    # b = profit ratio
    # p = win rate
    # q = loss rate (1-p)
    kelly_fraction = (profit_ratio * win_rate - (1 - win_rate)) / profit_ratio
    
    # Use half-kelly for safety and apply maximum size
    position_sizes = signals * min(kelly_fraction * 0.5, max_size)
    
    return position_sizes
"""
        else:
            raise ValueError(f"Unknown position sizing method: {method}") 