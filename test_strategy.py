from agents.data_agent import DataAgent
from agents.strategy_agent import StrategyAgent
from agents.backtest_agent import BacktestAgent
from agents.performance_agent import PerformanceAgent

def test_momentum_strategy():
    # Initialize agents
    data_agent = DataAgent()
    strategy_agent = StrategyAgent()
    backtest_agent = BacktestAgent()
    performance_agent = PerformanceAgent()
    
    # Test parameters
    symbol = "AAPL"  # Let's start with Apple stock
    start_date = "2022-01-01"
    end_date = "2024-01-01"
    
    # Strategy specification
    strategy_spec = {
        'type': 'momentum',
        'params': {
            'lookback': 30,
            'zscore_threshold': 1.0
        },
        'position_sizing': {
            'method': 'volatility_targeting',
            'params': {
                'target_vol': 0.20,
                'lookback': 60
            }
        }
    }
    
    try:
        # 1. Fetch data
        print("Fetching data...")
        data = data_agent.fetch_data(symbol, start_date, end_date)
        
        # 2. Generate strategy code
        print("Generating strategy code...")
        strategy_code = strategy_agent.generate_complete_strategy(strategy_spec)
        
        # 3. Run backtest
        print("Running backtest...")
        backtest_results = backtest_agent.run_backtest(
            {symbol: data},
            {**strategy_spec, **strategy_code}
        )
        
        # 4. Analyze performance
        if backtest_results['status'] == 'success':
            print("Analyzing performance...")
            performance = performance_agent.analyze_performance(
                backtest_results['equity_curve'],
                backtest_results['trades']
            )
            
            # Print results
            print("\nPerformance Metrics:")
            print(performance['metrics'])
            print("\nTrade Statistics:")
            print(performance['trade_stats'])
        else:
            print(f"Backtest failed: {backtest_results['message']}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_momentum_strategy() 