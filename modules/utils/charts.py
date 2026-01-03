"""
Visualization Utilities
Creates charts for trade analysis
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_pnl_chart(trades_df):
    """
    Cumulative P&L over time
    """
    if trades_df is None or len(trades_df) == 0:
        return None
    
    # Sort by date
    trades_sorted = trades_df.sort_values('entry_date')
    trades_sorted['cumulative_pnl'] = trades_sorted['net_pnl'].cumsum()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=trades_sorted['entry_date'],
        y=trades_sorted['cumulative_pnl'],
        mode='lines+markers',
        name='Cumulative P&L',
        line=dict(color='#2ecc71', width=2),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(46, 204, 113, 0.1)'
    ))
    
    fig.update_layout(
        title='Cumulative P&L Over Time',
        xaxis_title='Date',
        yaxis_title='Cumulative P&L (₹)',
        hovermode='x unified',
        plot_bgcolor='white',
        height=400
    )
    
    return fig


def create_win_loss_distribution(trades_df):
    """
    Distribution of wins vs losses
    """
    if trades_df is None or len(trades_df) == 0:
        return None
    
    wins = trades_df[trades_df['net_pnl'] > 0]['net_pnl']
    losses = trades_df[trades_df['net_pnl'] < 0]['net_pnl']
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=wins,
        name='Wins',
        marker_color='#2ecc71',
        opacity=0.7,
        nbinsx=20
    ))
    
    fig.add_trace(go.Histogram(
        x=losses,
        name='Losses',
        marker_color='#e74c3c',
        opacity=0.7,
        nbinsx=20
    ))
    
    fig.update_layout(
        title='Win/Loss Distribution',
        xaxis_title='P&L (₹)',
        yaxis_title='Number of Trades',
        barmode='overlay',
        plot_bgcolor='white',
        height=400
    )
    
    return fig


def create_discipline_score_chart(trades_df):
    """
    Discipline score over time
    """
    if trades_df is None or len(trades_df) == 0:
        return None
    
    trades_sorted = trades_df.sort_values('entry_date')
    
    # Color code by grade
    colors = trades_sorted['discipline_score'].apply(lambda x: 
        '#2ecc71' if x >= 80 else 
        '#f39c12' if x >= 60 else 
        '#e74c3c'
    )
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=trades_sorted['entry_date'],
        y=trades_sorted['discipline_score'],
        mode='markers',
        marker=dict(
            size=10,
            color=colors,
            line=dict(width=1, color='white')
        ),
        text=trades_sorted['symbol'],
        hovertemplate='<b>%{text}</b><br>Score: %{y}<br>Date: %{x}<extra></extra>'
    ))
    
    # Add grade threshold lines
    fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="A Grade")
    fig.add_hline(y=60, line_dash="dash", line_color="orange", annotation_text="C Grade")
    
    fig.update_layout(
        title='Discipline Score Trend',
        xaxis_title='Date',
        yaxis_title='Discipline Score',
        yaxis=dict(range=[0, 110]),
        plot_bgcolor='white',
        height=400
    )
    
    return fig


def create_stock_performance_chart(trades_df):
    """
    Performance by stock (top 10)
    """
    if trades_df is None or len(trades_df) == 0:
        return None
    
    # Group by stock
    stock_perf = trades_df.groupby('symbol').agg({
        'net_pnl': 'sum',
        'symbol': 'count'
    }).rename(columns={'symbol': 'count'})
    
    stock_perf = stock_perf.sort_values('net_pnl', ascending=True).tail(10)
    
    colors = ['#2ecc71' if x > 0 else '#e74c3c' for x in stock_perf['net_pnl']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=stock_perf['net_pnl'],
        y=stock_perf.index,
        orientation='h',
        marker_color=colors,
        text=stock_perf['net_pnl'].round(0),
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Top 10 Stocks by P&L',
        xaxis_title='Net P&L (₹)',
        yaxis_title='Stock',
        plot_bgcolor='white',
        height=400
    )
    
    return fig
