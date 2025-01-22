from typing import Dict, List
from phi.assistant import Assistant
from phi.tools.streamlit import StreamlitKwargs

class CoordinatorAgent(Assistant):
    def __init__(self):
        super().__init__(
            name="Coordinator",
            description="Strategy backtesting coordinator that helps users design and test trading strategies",
            instructions="""
            You are a trading strategy coordinator. Your role is to:
            1. Understand the user's strategy requirements
            2. Validate the universe (crypto, stocks, etc.)
            3. Coordinate with the Data Agent for market data
            4. Send strategy rules to the Strategy Agent
            5. Handle clarification requests from other agents
            6. Present results to the user
            
            Always ask for the following information if not provided:
            - Asset universe (crypto, stocks, forex)
            - Time period for backtesting
            - Entry and exit rules
            - Position sizing preferences:
              * Fixed percentage
              * Volatility targeting
              * Equal risk per trade
              * Kelly Criterion
              * Inverse volatility weighting (for multi-asset)
            - Rebalancing preferences:
              * Frequency (daily, weekly, monthly)
              * Method (calendar, threshold-based)
            - Risk management rules:
              * Maximum position size
              * Stop-loss levels
              * Portfolio-level constraints
            """,
            tools=[],
            model="gpt-4-turbo-preview"
        ) 