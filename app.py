import streamlit as st
from utils.assistant import Assistant
from agents.data_agent import DataAgent
from agents.strategy_agent import StrategyAgent
from agents.backtest_agent import BacktestAgent
from agents.performance_agent import PerformanceAgent
from utils.strategy_rules import STRATEGY_CATEGORIES, StrategyRuleManager
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def initialize_session_state():
    if 'backtest_results' not in st.session_state:
        st.session_state.backtest_results = None
    if 'equity_curve' not in st.session_state:
        st.session_state.equity_curve = None
    if 'buy_hold_equity' not in st.session_state:
        st.session_state.buy_hold_equity = None
    if 'trades_df' not in st.session_state:
        st.session_state.trades_df = None
    if 'show_buy_hold' not in st.session_state:
        st.session_state.show_buy_hold = True
    if 'selected_year' not in st.session_state:
        st.session_state.selected_year = None
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'strategy_manager' not in st.session_state:
        st.session_state.strategy_manager = StrategyRuleManager()
    if 'configuring_rule' not in st.session_state:
        st.session_state.configuring_rule = None
    if 'temp_rule_params' not in st.session_state:
        st.session_state.temp_rule_params = {}

def render_strategy_rules():
    st.sidebar.header("Strategy Rules")
    
    # Add CSS for better styling
    st.markdown("""
        <style>
        .stMarkdown {margin-bottom: 0.5rem;}
        .stButton button {width: 100%;}
        .stSelectbox {margin-bottom: 1rem;}
        </style>
    """, unsafe_allow_html=True)
    
    # Iterate through strategy categories
    for category, cat_info in STRATEGY_CATEGORIES.items():
        with st.sidebar.expander(f"📊 {cat_info['name']}", expanded=True):
            st.markdown(f"_{cat_info['description']}_")
            
            # Category weight
            weight = st.slider(
                "Category Weight",
                0.0, 1.0, 1.0,
                key=f"weight_{category}"
            )
            st.session_state.strategy_manager.set_category_weight(category, weight)
            
            # Show active rules first
            if category in st.session_state.strategy_manager.active_rules:
                st.markdown("**Active Rules:**")
                for i, rule in enumerate(st.session_state.strategy_manager.active_rules[category]):
                    rule_info = cat_info['rules'][rule.rule_type]
                    with st.container():
                        st.markdown(f"🔹 {rule_info['name']}")
                        params = [f"{param_name}: {value}" for param_name, value in rule.parameters.items() if param_name != 'weight']
                        st.markdown(f"_{', '.join(params)}_")
                        if st.button("🗑️ Remove", key=f"remove_{category}_{i}", help=f"Remove this {rule_info['name']} rule"):
                            st.session_state.strategy_manager.remove_rule(category, i)
                            st.rerun()
                st.markdown("---")
            
            # Add rule section
            st.markdown("**Add New Rule:**")
            if st.session_state.configuring_rule != category:
                if st.button("➕ Add Rule", key=f"add_{category}"):
                    st.session_state.configuring_rule = category
                    st.session_state.temp_rule_params = {}
                    st.rerun()
            else:
                # Rule type selection
                rule_type = st.selectbox(
                    "Rule Type",
                    options=list(cat_info['rules'].keys()),
                    format_func=lambda x: cat_info['rules'][x]['name'],
                    key=f"rule_type_{category}"
                )
                
                # Rule parameters
                rule_info = cat_info['rules'][rule_type]
                rule_params = {}
                
                for param_name, param_info in rule_info['parameters'].items():
                    if param_info['type'] == 'int':
                        value = st.slider(
                            param_name.replace('_', ' ').title(),
                            param_info['min'],
                            param_info['max'],
                            param_info['default'],
                            key=f"param_{category}_{rule_type}_{param_name}"
                        )
                    else:  # float
                        value = st.slider(
                            param_name.replace('_', ' ').title(),
                            float(param_info['min']),
                            float(param_info['max']),
                            float(param_info['default']),
                            key=f"param_{category}_{rule_type}_{param_name}"
                        )
                    rule_params[param_name] = value
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✓ Add", key=f"confirm_{category}_{rule_type}", help="Add this rule to the strategy"):
                        st.session_state.strategy_manager.add_rule(category, rule_type, rule_params)
                        st.session_state.configuring_rule = None
                        st.session_state.temp_rule_params = {}
                        st.rerun()
                with col2:
                    if st.button("✗ Cancel", key=f"cancel_{category}_{rule_type}", help="Cancel adding this rule"):
                        st.session_state.configuring_rule = None
                        st.session_state.temp_rule_params = {}
                        st.rerun()

def main():
    st.title("Trading Strategy Assistant")
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize agents
    data_agent = DataAgent()
    strategy_agent = StrategyAgent()
    backtest_agent = BacktestAgent()
    performance_agent = PerformanceAgent()
    
    # Sidebar for inputs
    with st.sidebar:
        # Data Settings
        with st.expander("📈 Data Settings", expanded=True):
            symbol = st.text_input("Symbol", "AAPL")
            period = st.selectbox(
                "Data Period",
                ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"],
                index=3,
                format_func=lambda x: {
                    "1mo": "1 Month",
                    "3mo": "3 Months",
                    "6mo": "6 Months",
                    "1y": "1 Year",
                    "2y": "2 Years",
                    "5y": "5 Years",
                    "10y": "10 Years",
                    "max": "Maximum"
                }[x]
            )
        
        # Strategy Rules
        render_strategy_rules()
        
        # Position Sizing
        with st.expander("💰 Position Sizing", expanded=True):
            position_methods = {
                "volatility_targeting": "Volatility Targeting",
                "fixed_percentage": "Fixed Percentage",
                "equal_risk": "Equal Risk per Trade",
                "inverse_volatility": "Inverse Volatility",
                "kelly_criterion": "Kelly Criterion"
            }
            
            position_method = st.selectbox(
                "Method",
                options=list(position_methods.keys()),
                format_func=lambda x: position_methods[x]
            )
            
            if position_method == "volatility_targeting":
                target_vol = st.slider("Target Volatility (%)", 1, 50, 20) / 100
                vol_lookback = st.slider("Volatility Lookback (days)", 20, 252, 60)
                max_position = st.slider("Maximum Position Size (%)", 10, 100, 30) / 100
                sizing_params = {
                    "target_vol": target_vol,
                    "lookback": vol_lookback,
                    "max_size": max_position
                }
            elif position_method == "fixed_percentage":
                position_size = st.slider("Position Size (%)", 1, 100, 10) / 100
                sizing_params = {"position_size": position_size}
            elif position_method == "equal_risk":
                risk_per_trade = st.slider("Risk Per Trade (%)", 1, 10, 1) / 100
                atr_periods = st.slider("ATR Periods", 5, 50, 14)
                sizing_params = {
                    "risk_per_trade": risk_per_trade,
                    "atr_periods": atr_periods
                }
            elif position_method == "inverse_volatility":
                lookback = st.slider("Volatility Lookback (days)", 20, 252, 60)
                max_position = st.slider("Maximum Position Size (%)", 10, 100, 30) / 100
                sizing_params = {
                    "lookback": lookback,
                    "max_size": max_position
                }
            else:  # kelly_criterion
                win_rate = st.slider("Expected Win Rate (%)", 1, 99, 50) / 100
                profit_ratio = st.slider("Profit Ratio (Avg Win / Avg Loss)", 0.1, 5.0, 2.0, 0.1)
                max_position = st.slider("Maximum Position Size (%)", 10, 100, 30) / 100
                sizing_params = {
                    "win_rate": win_rate,
                    "profit_ratio": profit_ratio,
                    "max_size": max_position
                }
    
    # Main area - Run Backtest button
    if st.button("🚀 Run Backtest", help="Run the backtest with the current strategy configuration"):
        with st.spinner("Running backtest..."):
            try:
                # Get strategy configuration
                strategy_config = st.session_state.strategy_manager.get_rules_config()
                
                # Strategy specification
                strategy_spec = {
                    'type': 'combined',
                    'categories': strategy_config,
                    'position_sizing': {
                        'method': position_method,
                        'params': sizing_params
                    }
                }
                
                # Run backtest
                data = data_agent.fetch_data(symbol, period)
                if isinstance(data, str):
                    st.error(f"Error fetching data: {data}")
                    return
                
                strategy_code = strategy_agent.generate_complete_strategy(strategy_spec)
                
                # Debug information
                st.write("Strategy Configuration:")
                st.json(strategy_spec)
                if strategy_code:
                    st.write("Generated Strategy Code:")
                    st.code(strategy_code.get('signal_code', 'No signal code generated'))
                
                backtest_results = backtest_agent.run_backtest(
                    {symbol: data},
                    {**strategy_spec, **strategy_code}
                )
                
                if backtest_results['status'] == 'success':
                    st.success("Backtest completed successfully!")
                    
                    # Store results
                    st.session_state.backtest_results = backtest_results
                    st.session_state.equity_curve = pd.Series(backtest_results['equity_curve'])
                    st.session_state.trades_df = pd.DataFrame(backtest_results['trades'])
                    st.session_state.data = data
                    st.session_state.buy_hold_equity = data['Close'] / data['Close'].iloc[0]
                    
                    # Show results
                    performance = performance_agent.analyze_performance(
                        st.session_state.equity_curve,
                        st.session_state.trades_df
                    )
                    
                    # Display metrics
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Performance Metrics")
                        metrics_df = pd.DataFrame(
                            performance['metrics'].items(),
                            columns=['Metric', 'Value']
                        ).set_index('Metric')
                        st.dataframe(metrics_df.style.format("{:.2f}"))
                    
                    with col2:
                        st.subheader("Trade Statistics")
                        trade_stats = performance['trade_stats']
                        stats_df = pd.DataFrame({
                            "Total Trades": trade_stats['total_trades'],
                            "Win Rate (%)": trade_stats['win_rate'],
                            "Avg Win": trade_stats['avg_win'],
                            "Avg Loss": trade_stats['avg_loss'],
                            "Profit Factor": trade_stats['profit_factor'],
                            "Avg Hold Time (days)": trade_stats['avg_hold_time']
                        }, index=['Value']).T
                        st.dataframe(stats_df.style.format("{:.2f}"))
                    
                    # Show equity curve
                    st.subheader("Strategy Performance")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=st.session_state.equity_curve.index,
                        y=st.session_state.equity_curve,
                        name='Strategy'
                    ))
                    if st.session_state.show_buy_hold:
                        fig.add_trace(go.Scatter(
                            x=st.session_state.buy_hold_equity.index,
                            y=st.session_state.buy_hold_equity,
                            name='Buy & Hold',
                            line=dict(dash='dash')
                        ))
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Equity",
                        template='plotly_dark'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show trade analysis
                    if len(st.session_state.trades_df) > 0:
                        st.subheader("Trade Analysis")
                        
                        # Group trades by year
                        trades_df = st.session_state.trades_df.copy()
                        trades_df.index = pd.to_datetime(trades_df.index)
                        years = sorted(trades_df.index.year.unique())
                        
                        # Initialize selected year if needed
                        if st.session_state.selected_year is None or st.session_state.selected_year not in years:
                            st.session_state.selected_year = years[-1]
                        
                        selected_year = st.selectbox(
                            "Select Year",
                            years,
                            index=years.index(st.session_state.selected_year),
                            key='year_selector'
                        )
                        st.session_state.selected_year = selected_year
                        
                        # Filter trades for selected year
                        year_trades = trades_df[trades_df.index.year == selected_year]
                        
                        # Create trade visualization
                        fig = go.Figure()
                        
                        # Add price line with position coloring
                        if st.session_state.data is not None and 'positions' in st.session_state.backtest_results:
                            year_data = st.session_state.data[st.session_state.data.index.year == selected_year]
                            positions = pd.Series(st.session_state.backtest_results['positions'])
                            year_positions = positions[positions.index.year == selected_year]
                            
                            # Align positions with price data
                            aligned_data = pd.DataFrame({
                                'price': year_data['Close'],
                                'position': year_positions
                            })
                            aligned_data['position'] = aligned_data['position'].fillna(0)
                            
                            # Add base price line for continuity
                            fig.add_trace(go.Scatter(
                                x=aligned_data.index,
                                y=aligned_data['price'],
                                name='Price',
                                line=dict(color='rgba(0,179,179,0.3)', width=1),
                                showlegend=False,
                                hoverinfo='skip'
                            ))
                            
                            # Split data into segments based on position
                            for position_type, color, pos_name in [
                                (lambda x: x > 0, 'rgba(0,255,0,1)', 'Long'),  # Long - Green
                                (lambda x: x < 0, 'rgba(255,0,0,1)', 'Short'),  # Short - Red
                                (lambda x: x == 0, '#00b3b3', 'No Position'),   # No position - Default
                            ]:
                                mask = position_type(aligned_data['position'])
                                if mask.any():
                                    segment_data = aligned_data[mask].copy()
                                    segment_data['position_pct'] = segment_data['position'] * 100
                                    
                                    fig.add_trace(go.Scatter(
                                        x=segment_data.index,
                                        y=segment_data['price'],
                                        name=pos_name,
                                        line=dict(color=color, width=2),
                                        hovertemplate=
                                        "<b>%{text}</b><br>" +
                                        "Date: %{x}<br>" +
                                        "Price: $%{y:.2f}<br>" +
                                        "<extra></extra>",
                                        text=[f"{pos_name} ({row['position_pct']:.1f}%)" for _, row in segment_data.iterrows()]
                                    ))
                            
                            # Add buy/sell markers with PnL information
                            entries = year_trades[year_trades['size'] != 0].copy()
                            entries['direction'] = entries['size'].apply(lambda x: 'Buy' if x > 0 else 'Sell')
                            entries['marker_color'] = entries['direction'].apply(lambda x: 'green' if x == 'Buy' else 'red')
                            
                            fig.add_trace(go.Scatter(
                                x=entries.index,
                                y=entries['price'],
                                mode='markers',
                                name='Trades',
                                marker=dict(
                                    color=entries['marker_color'],
                                    size=10,
                                    symbol=['triangle-up' if x == 'Buy' else 'triangle-down' for x in entries['direction']]
                                ),
                                hovertemplate=
                                "<b>%{text}</b><br>" +
                                "Date: %{x}<br>" +
                                "Price: $%{y:.2f}<br>" +
                                "Size: %{customdata:.1%}<br>" +
                                "<extra></extra>",
                                text=[f"{row['direction']} ({row['pnl']:.2f})" for _, row in entries.iterrows()],
                                customdata=abs(entries['size'])
                            ))
                            
                            fig.update_layout(
                                title=f"Trades for {selected_year}",
                                xaxis_title="Date",
                                yaxis_title="Price",
                                height=400,
                                template='plotly_dark',
                                showlegend=True,
                                hovermode='x unified'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Add position size visualization
                            fig_pos = go.Figure()
                            
                            # Create a continuous filled area from min to max of the time range
                            dates = pd.date_range(start=year_positions.index.min(), end=year_positions.index.max(), freq='D')
                            full_positions = year_positions.reindex(dates).fillna(0)
                            
                            # Add long positions (green)
                            long_mask = full_positions >= 0
                            if long_mask.any():
                                fig_pos.add_trace(go.Scatter(
                                    x=full_positions.index,
                                    y=full_positions.where(long_mask, 0),
                                    name='Long',
                                    fill='tozeroy',
                                    line=dict(color='rgba(0,255,0,0.5)', width=1),
                                    fillcolor='rgba(0,255,0,0.2)'
                                ))
                            
                            # Add short positions (red)
                            short_mask = full_positions < 0
                            if short_mask.any():
                                fig_pos.add_trace(go.Scatter(
                                    x=full_positions.index,
                                    y=full_positions.where(short_mask, 0),
                                    name='Short',
                                    fill='tozeroy',
                                    line=dict(color='rgba(255,0,0,0.5)', width=1),
                                    fillcolor='rgba(255,0,0,0.2)'
                                ))
                            
                            # Add zero line
                            fig_pos.add_hline(
                                y=0, 
                                line_dash="dash", 
                                line_color="white",
                                line_width=1,
                                opacity=0.5
                            )
                            
                            fig_pos.update_layout(
                                title=f"Position Sizes for {selected_year}",
                                xaxis_title="Date",
                                yaxis_title="Position Size",
                                height=300,
                                template='plotly_dark',
                                showlegend=True,
                                yaxis=dict(
                                    tickformat='.0%',  # Format y-axis as percentages
                                    zeroline=True,
                                    zerolinecolor='white',
                                    zerolinewidth=1
                                )
                            )
                            st.plotly_chart(fig_pos, use_container_width=True)
                            
                            # Show trade statistics for the year
                            year_stats = pd.DataFrame({
                                "Total Trades": len(year_trades),
                                "Winning Trades": len(year_trades[year_trades['pnl'] > 0]),
                                "Losing Trades": len(year_trades[year_trades['pnl'] < 0]),
                                "Win Rate": f"{len(year_trades[year_trades['pnl'] > 0]) / len(year_trades) * 100:.1f}%",
                                "Average Win": f"${year_trades[year_trades['pnl'] > 0]['pnl'].mean():.2f}",
                                "Average Loss": f"${year_trades[year_trades['pnl'] < 0]['pnl'].mean():.2f}",
                                "Average Hold Time": f"{year_trades['hold_time'].mean():.1f} days"
                            }, index=['Value']).T
                            
                            st.dataframe(year_stats)
                else:
                    st.error(f"Backtest failed: {backtest_results['message']}")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 