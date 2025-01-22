"""
Strategy rules configuration and management.
"""

STRATEGY_CATEGORIES = {
    "momentum": {
        "name": "Momentum",
        "description": "Rules based on price momentum and trend strength",
        "rules": {
            "zscore": {
                "name": "Z-Score Momentum",
                "parameters": {
                    "lookback": {"type": "int", "min": 5, "max": 252, "default": 30},
                    "threshold": {"type": "float", "min": 0.0, "max": 3.0, "default": 1.0},
                    "weight": {"type": "float", "min": 0.0, "max": 1.0, "default": 1.0}
                }
            },
            "roc": {
                "name": "Rate of Change",
                "parameters": {
                    "lookback": {"type": "int", "min": 1, "max": 252, "default": 20},
                    "threshold": {"type": "float", "min": 0.0, "max": 10.0, "default": 2.0},
                    "weight": {"type": "float", "min": 0.0, "max": 1.0, "default": 1.0}
                }
            }
        }
    },
    "breakout": {
        "name": "Breakout",
        "description": "Rules based on price breaking key levels",
        "rules": {
            "channel": {
                "name": "Channel Breakout",
                "parameters": {
                    "lookback": {"type": "int", "min": 5, "max": 252, "default": 20},
                    "channel_width": {"type": "float", "min": 0.5, "max": 3.0, "default": 2.0},
                    "weight": {"type": "float", "min": 0.0, "max": 1.0, "default": 1.0}
                }
            },
            "support_resistance": {
                "name": "Support/Resistance",
                "parameters": {
                    "lookback": {"type": "int", "min": 5, "max": 252, "default": 50},
                    "threshold": {"type": "float", "min": 0.0, "max": 5.0, "default": 1.0},
                    "weight": {"type": "float", "min": 0.0, "max": 1.0, "default": 1.0}
                }
            }
        }
    },
    "crossover": {
        "name": "Moving Average Crossovers",
        "description": "Rules based on moving average crossovers",
        "rules": {
            "sma_crossover": {
                "name": "SMA Crossover",
                "parameters": {
                    "fast_period": {"type": "int", "min": 1, "max": 200, "default": 10},
                    "slow_period": {"type": "int", "min": 2, "max": 200, "default": 30},
                    "weight": {"type": "float", "min": 0.0, "max": 1.0, "default": 1.0}
                }
            },
            "ema_crossover": {
                "name": "EMA Crossover",
                "parameters": {
                    "fast_period": {"type": "int", "min": 1, "max": 200, "default": 12},
                    "slow_period": {"type": "int", "min": 2, "max": 200, "default": 26},
                    "weight": {"type": "float", "min": 0.0, "max": 1.0, "default": 1.0}
                }
            }
        }
    },
    "volatility": {
        "name": "Volatility",
        "description": "Rules based on market volatility",
        "rules": {
            "atr_breakout": {
                "name": "ATR Breakout",
                "parameters": {
                    "lookback": {"type": "int", "min": 5, "max": 252, "default": 14},
                    "multiplier": {"type": "float", "min": 0.5, "max": 5.0, "default": 2.0},
                    "weight": {"type": "float", "min": 0.0, "max": 1.0, "default": 1.0}
                }
            },
            "volatility_regime": {
                "name": "Volatility Regime",
                "parameters": {
                    "lookback": {"type": "int", "min": 5, "max": 252, "default": 20},
                    "threshold": {"type": "float", "min": 0.5, "max": 3.0, "default": 1.5},
                    "weight": {"type": "float", "min": 0.0, "max": 1.0, "default": 1.0}
                }
            }
        }
    }
}

class StrategyRule:
    def __init__(self, category, rule_type, parameters):
        self.category = category
        self.rule_type = rule_type
        self.parameters = parameters
        
    def calculate_signal(self, data):
        """Calculate the signal for this rule based on the data."""
        # Implementation will vary based on rule type
        pass

class StrategyRuleManager:
    def __init__(self):
        self.active_rules = {}  # Dictionary to store active rules by category
        self.category_weights = {}  # Dictionary to store category weights
    
    def add_rule(self, category, rule_type, parameters):
        """Add a new rule to a category."""
        if category not in self.active_rules:
            self.active_rules[category] = []
        
        rule = StrategyRule(category, rule_type, parameters)
        self.active_rules[category].append(rule)
    
    def remove_rule(self, category, index):
        """Remove a rule from a category by index."""
        if category in self.active_rules and 0 <= index < len(self.active_rules[category]):
            self.active_rules[category].pop(index)
    
    def set_category_weight(self, category, weight):
        """Set the weight for a category."""
        self.category_weights[category] = weight
    
    def get_rules_config(self):
        """Get the current configuration of all rules."""
        config = {}
        for category in self.active_rules:
            config[category] = {
                'weight': self.category_weights.get(category, 1.0),
                'rules': [
                    {
                        'type': rule.rule_type,
                        'parameters': rule.parameters
                    }
                    for rule in self.active_rules[category]
                ]
            }
        return config 