"""
Strategy rules configuration and management.
"""

STRATEGY_CATEGORIES = {
    "entry": {
        "name": "Entry Rules",
        "description": "Rules for entering positions",
        "subcategories": {
            "momentum": {
                "name": "Momentum",
                "description": "Rules based on price momentum and trends",
                "rules": {
                    "roc": {
                        "name": "Rate of Change",
                        "description": "Enter based on price rate of change",
                        "parameters": {
                            "lookback": {
                                "type": "int",
                                "min": 1,
                                "max": 100,
                                "default": 30,
                                "description": "Lookback period for ROC calculation"
                            },
                            "threshold": {
                                "type": "float",
                                "min": 0.0,
                                "max": 5.0,
                                "default": 1.0,
                                "description": "ROC threshold for signal generation"
                            }
                        }
                    }
                }
            },
            "breakout": {
                "name": "Breakout",
                "description": "Rules based on price breakouts",
                "rules": {
                    "channel": {
                        "name": "Channel Breakout",
                        "description": "Enter on breakouts from price channels",
                        "parameters": {
                            "lookback": {
                                "type": "int",
                                "min": 5,
                                "max": 100,
                                "default": 20,
                                "description": "Lookback period for channel calculation"
                            },
                            "channel_width": {
                                "type": "float",
                                "min": 1.0,
                                "max": 3.0,
                                "default": 1.5,
                                "description": "Channel width multiplier"
                            }
                        }
                    }
                }
            },
            "moving_average": {
                "name": "Moving Average",
                "description": "Rules based on moving averages",
                "rules": {
                    "crossover": {
                        "name": "MA Crossover",
                        "description": "Enter on moving average crossovers",
                        "parameters": {
                            "fast_period": {
                                "type": "int",
                                "min": 5,
                                "max": 50,
                                "default": 10,
                                "description": "Fast moving average period"
                            },
                            "slow_period": {
                                "type": "int",
                                "min": 10,
                                "max": 200,
                                "default": 50,
                                "description": "Slow moving average period"
                            }
                        }
                    }
                }
            },
            "volatility": {
                "name": "Volatility",
                "description": "Rules based on price volatility",
                "rules": {
                    "bollinger": {
                        "name": "Bollinger Bands",
                        "description": "Enter on Bollinger Band signals",
                        "parameters": {
                            "lookback": {
                                "type": "int",
                                "min": 5,
                                "max": 100,
                                "default": 20,
                                "description": "Lookback period for BB calculation"
                            },
                            "std_dev": {
                                "type": "float",
                                "min": 1.0,
                                "max": 3.0,
                                "default": 2.0,
                                "description": "Number of standard deviations"
                            }
                        }
                    }
                }
            }
        }
    },
    "exit": {
        "name": "Exit Rules",
        "description": "Rules for exiting positions",
        "subcategories": {
            "rebalancing": {
                "name": "Rebalancing",
                "description": "Time-based position rebalancing",
                "rules": {
                    "periodic": {
                        "name": "Periodic Rebalancing",
                        "description": "Exit based on time intervals",
                        "parameters": {
                            "period": {
                                "type": "int",
                                "min": 1,
                                "max": 252,
                                "default": 21,
                                "description": "Rebalancing period in trading days"
                            }
                        }
                    }
                }
            },
            "stop_loss": {
                "name": "Stop Loss",
                "description": "Rules for limiting losses",
                "rules": {
                    "fixed": {
                        "name": "Fixed Stop Loss",
                        "description": "Exit at fixed percentage loss",
                        "parameters": {
                            "stop_pct": {
                                "type": "float",
                                "min": 0.1,
                                "max": 20.0,
                                "default": 5.0,
                                "description": "Stop loss percentage"
                            }
                        }
                    },
                    "atr": {
                        "name": "ATR Stop Loss",
                        "description": "Exit based on ATR multiple",
                        "parameters": {
                            "atr_periods": {
                                "type": "int",
                                "min": 5,
                                "max": 50,
                                "default": 14,
                                "description": "ATR calculation period"
                            },
                            "atr_multiple": {
                                "type": "float",
                                "min": 1.0,
                                "max": 5.0,
                                "default": 2.0,
                                "description": "ATR multiple for stop distance"
                            }
                        }
                    }
                }
            },
            "take_profit": {
                "name": "Take Profit",
                "description": "Rules for profit taking",
                "rules": {
                    "trailing": {
                        "name": "Trailing Stop",
                        "description": "Exit using trailing stop",
                        "parameters": {
                            "trail_pct": {
                                "type": "float",
                                "min": 0.1,
                                "max": 20.0,
                                "default": 5.0,
                                "description": "Trailing stop percentage"
                            }
                        }
                    },
                    "time": {
                        "name": "Time-Based Exit",
                        "description": "Exit after holding period",
                        "parameters": {
                            "hold_days": {
                                "type": "int",
                                "min": 1,
                                "max": 252,
                                "default": 21,
                                "description": "Maximum holding period in days"
                            }
                        }
                    }
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