"""
TradeAudit Pro - Main Application
India's First AI-Powered Trade Discipline Analyzer
"""

import streamlit as st
import pandas as pd
from modules.parsers.broker_parser import parse_broker_file, get_supported_brokers, detect_broker_format
from modules.analysis.discipline_scorer import analyze_trades, get_summary_stats, detect_patterns
from modules.utils.charts import (
    create_pnl_chart, 
    create_win_loss_distribution,
    create_discipline_score_chart,
    create_stock_performance_chart
)

# Page config
st.set_page_config(
    page_title="TradeAudit Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'trades_df' not in st.session_state:
    st.session_state.trades_df = None
if 'stats' not in st.session_state:
    st.session_state.stats = None

# Header
st.markdown('<h1 class="main-header">📊 TradeAudit Pro</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">India\'s First Trade Discipline Analyzer</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    st.markdown("---")
    
    # File upload
    st.subheader("📁 Upload Tradebook")
    
    uploaded_file = st.file_uploader(
        "Choose your broker's CSV file",
        type=['csv'],
        help="Download from your broker's trade history section"
    )
    
    if uploaded_file is not None:
        # Try to auto-detect broker
        detected_broker, detected_type = detect_broker_format(uploaded_file)
        uploaded_file.seek(0)  # Reset file pointer
        
        if detected_broker:
            st.success(f"✅ Detected: {detected_broker.upper()} ({detected_type})")
            broker_choice = detected_broker
            trade_type = detected_type
        else:
            st.warning("⚠️ Could not auto-detect. Please select manually:")
            broker_options = {
                'zerodha': 'Zerodha',
                'kotak': 'Kotak Securities',
                'icici': 'ICICI Direct'
            }
            broker_choice = st.selectbox("Select Broker", list(broker_options.keys()), 
                                        format_func=lambda x: broker_options[x])
            
            if broker_choice == 'kotak':
                trade_type = st.radio("Trade Type", ['equity', 'derivatives'])
            else:
                trade_type = 'equity'
        
        # Process button
        if st.button("🚀 Analyze Trades", type="primary"):
            with st.spinner("Processing your trades..."):
                # Parse file
                trades_df, error = parse_broker_file(uploaded_file, broker_choice, trade_type)
                
                if error:
                    st.error(f"❌ Error: {error}")
                elif trades_df is None or len(trades_df) == 0:
                    st.error("❌ No complete trades found in file")
                else:
                    # Analyze trades
                    trades_df = analyze_trades(trades_df)
                    stats = get_summary_stats(trades_df)
                    
                    # Store in session state
                    st.session_state.trades_df = trades_df
                    st.session_state.stats = stats
                    
                    st.success(f"✅ Analyzed {len(trades_df)} trades!")
    
    st.markdown("---")
    
    # Info
    st.subheader("ℹ️ Supported Brokers")
    st.markdown("""
    - ✅ Zerodha
    - ✅ Kotak Securities
    - ✅ ICICI Direct
    - 🔜 Upstox
    - 🔜 Angel One
    - 🔜 Groww
    """)
    
    st.markdown("---")
    st.markdown("**Made with ❤️ for Indian Traders**")

# Main content
if st.session_state.trades_df is not None:
    trades_df = st.session_state.trades_df
    stats = st.session_state.stats
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🔍 Trade Details", "💡 Insights"])
    
    with tab1:
        st.header("📊 Performance Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Trades",
                stats['total_trades'],
                delta=f"{stats['winning_trades']} wins"
            )
        
        with col2:
            st.metric(
                "Win Rate",
                f"{stats['win_rate']:.1f}%",
                delta=None
            )
        
        with col3:
            delta_color = "normal" if stats['net_pnl'] > 0 else "inverse"
            st.metric(
                "Net P&L",
                f"₹{stats['net_pnl']:,.0f}",
                delta=f"Profit Factor: {stats['profit_factor']:.2f}"
            )
        
        with col4:
            avg_score = stats['avg_discipline_score']
            grade = 'A' if avg_score >= 80 else 'B' if avg_score >= 60 else 'C'
            st.metric(
                "Avg Discipline",
                f"{avg_score:.0f}/100",
                delta=f"Grade: {grade}"
            )
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            pnl_chart = create_pnl_chart(trades_df)
            if pnl_chart:
                st.plotly_chart(pnl_chart, use_container_width=True)
        
        with col2:
            discipline_chart = create_discipline_score_chart(trades_df)
            if discipline_chart:
                st.plotly_chart(discipline_chart, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            wl_chart = create_win_loss_distribution(trades_df)
            if wl_chart:
                st.plotly_chart(wl_chart, use_container_width=True)
        
        with col2:
            stock_chart = create_stock_performance_chart(trades_df)
            if stock_chart:
                st.plotly_chart(stock_chart, use_container_width=True)
        
        # Additional stats
        st.markdown("---")
        st.subheader("📈 Detailed Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average Win", f"₹{stats['avg_win']:,.0f}")
            st.metric("Largest Win", f"₹{stats['largest_win']:,.0f}")
        
        with col2:
            st.metric("Average Loss", f"₹{stats['avg_loss']:,.0f}")
            st.metric("Largest Loss", f"₹{stats['largest_loss']:,.0f}")
        
        with col3:
            st.metric("Total Charges", f"₹{stats['total_charges']:,.0f}")
            st.metric("Brokerage Paid", f"₹{stats['total_brokerage']:,.0f}")
    
    with tab2:
        st.header("🔍 Trade-by-Trade Analysis")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_result = st.selectbox(
                "Filter by Result",
                ["All", "Winners Only", "Losers Only"]
            )
        
        with col2:
            filter_grade = st.selectbox(
                "Filter by Grade",
                ["All", "A (80+)", "B (60-79)", "C (50-59)", "D/F (<50)"]
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["Date (Latest)", "P&L (Highest)", "P&L (Lowest)", "Score (Highest)"]
            )
        
        # Apply filters
        filtered_df = trades_df.copy()
        
        if filter_result == "Winners Only":
            filtered_df = filtered_df[filtered_df['net_pnl'] > 0]
        elif filter_result == "Losers Only":
            filtered_df = filtered_df[filtered_df['net_pnl'] < 0]
        
        if filter_grade == "A (80+)":
            filtered_df = filtered_df[filtered_df['discipline_score'] >= 80]
        elif filter_grade == "B (60-79)":
            filtered_df = filtered_df[(filtered_df['discipline_score'] >= 60) & (filtered_df['discipline_score'] < 80)]
        elif filter_grade == "C (50-59)":
            filtered_df = filtered_df[(filtered_df['discipline_score'] >= 50) & (filtered_df['discipline_score'] < 60)]
        elif filter_grade == "D/F (<50)":
            filtered_df = filtered_df[filtered_df['discipline_score'] < 50]
        
        # Sort
        if sort_by == "Date (Latest)":
            filtered_df = filtered_df.sort_values('entry_date', ascending=False)
        elif sort_by == "P&L (Highest)":
            filtered_df = filtered_df.sort_values('net_pnl', ascending=False)
        elif sort_by == "P&L (Lowest)":
            filtered_df = filtered_df.sort_values('net_pnl', ascending=True)
        elif sort_by == "Score (Highest)":
            filtered_df = filtered_df.sort_values('discipline_score', ascending=False)
        
        st.write(f"**Showing {len(filtered_df)} trades**")
        
        # Display table
        display_columns = [
            'entry_date', 'symbol', 'quantity', 'entry_price', 'exit_price',
            'return_pct', 'net_pnl', 'discipline_score', 'grade'
        ]
        
        # Format the display
        display_df = filtered_df[display_columns].copy()
        display_df.columns = ['Date', 'Stock', 'Qty', 'Entry ₹', 'Exit ₹', 'Return %', 'P&L ₹', 'Score', 'Grade']
        
        # Color code P&L
        def color_pnl(val):
            color = '#2ecc71' if val > 0 else '#e74c3c' if val < 0 else 'black'
            return f'color: {color}; font-weight: bold'
        
        styled_df = display_df.style.applymap(color_pnl, subset=['P&L ₹'])
        
        st.dataframe(styled_df, use_container_width=True, height=600)
        
        # Download option
        st.download_button(
            "📥 Download Full Report (CSV)",
            trades_df.to_csv(index=False).encode('utf-8'),
            "tradeaudit_report.csv",
            "text/csv",
            key='download-csv'
        )
    
    with tab3:
        st.header("💡 Behavioral Insights")
        
        # Detect patterns
        patterns = detect_patterns(trades_df)
        
        if patterns:
            st.subheader("🔍 Detected Patterns")
            for pattern in patterns:
                if pattern['type'] == 'danger':
                    st.error(f"**{pattern['title']}**\n\n{pattern['message']}")
                elif pattern['type'] == 'warning':
                    st.warning(f"**{pattern['title']}**\n\n{pattern['message']}")
                else:
                    st.info(f"**{pattern['title']}**\n\n{pattern['message']}")
        else:
            st.success("✅ No major behavioral issues detected!")
        
        st.markdown("---")
        
        # Recommendations
        st.subheader("📌 Recommendations")
        
        # Based on stats
        if stats['win_rate'] < 40:
            st.warning("""
            **🎯 Improve Win Rate**
            - Your win rate is below 40%. Focus on entry quality.
            - Wait for better setups before entering trades.
            - Review your strategy - are you trading against the trend?
            """)
        
        if stats['profit_factor'] < 1:
            st.error("""
            **⚠️ Negative Profit Factor**
            - You're losing money despite wins. Your losses are too big.
            - Implement strict stop losses (7-8% max).
            - Let winners run - don't exit too early.
            """)
        
        if stats['avg_discipline_score'] < 60:
            st.warning("""
            **📚 Work on Discipline**
            - Average score below 60 indicates poor trade execution.
            - Follow a written trading plan.
            - Journal every trade - what went right/wrong.
            - Take a trading course or read "Trading in the Zone".
            """)
        
        if stats['total_brokerage'] > abs(stats['net_pnl']) * 0.5:
            st.warning("""
            **💰 High Brokerage Costs**
            - You're paying >50% of P&L in charges.
            - Reduce trading frequency.
            - Consider switching to discount brokers.
            - Focus on higher timeframe trades.
            """)

else:
    # Welcome screen
    st.markdown("""
    ## 👋 Welcome to TradeAudit Pro!
    
    ### 🎯 What This Tool Does:
    
    1. **Upload Your Tradebook** - Supports Zerodha, Kotak, ICICI formats
    2. **Instant Analysis** - Automatically calculates P&L, win rate, charges
    3. **Discipline Scoring** - Get a score (0-100) for each trade
    4. **Pattern Detection** - Identify overtrading, revenge trading, etc.
    5. **Actionable Insights** - Get specific recommendations to improve
    
    ### 🚀 Getting Started:
    
    1. Download your tradebook CSV from your broker's website
    2. Click "Browse files" in the sidebar
    3. Upload the file
    4. Click "Analyze Trades"
    5. Review your results!
    
    ### 📊 What You'll See:
    
    - **Performance Dashboard** - Charts, metrics, key stats
    - **Trade Details** - Every trade with discipline score
    - **Behavioral Insights** - What patterns you're showing
    
    ---
    
    ### 💡 Pro Tips:
    
    - For best results, upload at least 20-30 trades
    - Works with both equity and F&O trades
    - All calculations happen locally - your data is private
    - Export full report as CSV for record keeping
    
    ---
    
    **Ready? Upload your tradebook using the sidebar! 👈**
    """)
    
    # Sample data info
    with st.expander("📁 Sample CSV Format"):
        st.markdown("""
        **Zerodha Format:**
        - Symbol, Trade Date, Trade Type, Quantity, Price, Order Execution Time
        
        **Kotak Format:**
        - Trade Date, Security Name, Transaction Type, Quantity, Market Rate, Total Charges
        
        **ICICI Format:**
        - Date, Stock, Action, Qty, Price, Trade Value
        
        Download your tradebook from your broker's trade history section.
        """)
