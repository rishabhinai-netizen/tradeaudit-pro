"""
Trade Discipline Analyzer
Calculates discipline scores and identifies patterns
"""

import pandas as pd
import numpy as np

def calculate_basic_discipline_score(trade):
    """
    Basic discipline score (0-100)
    More advanced scoring will come in Phase 2
    
    For now, checks:
    - Win rate contribution
    - Risk-reward ratio
    - Position sizing consistency
    """
    score = 50  # Start at neutral
    
    # 1. P&L Performance (30 points)
    if trade['net_pnl'] > 0:
        score += 30
    elif trade['net_pnl'] > -500:  # Small loss
        score += 15
    else:
        score += 0
    
    # 2. Holding Period (20 points)
    # Penalize very short holds (< 5 min) - likely panic
    if trade['holding_period_minutes'] > 0:
        if trade['holding_period_minutes'] < 5:
            score -= 10
        elif 15 <= trade['holding_period_minutes'] <= 240:  # 15 min to 4 hours
            score += 20
        else:
            score += 10
    
    # 3. Trade Size Reasonableness (20 points)
    # Check if position value is reasonable (will improve with account size input)
    position_value = trade['quantity'] * trade['entry_price']
    if 10000 <= position_value <= 500000:  # ₹10K to ₹5L
        score += 20
    elif position_value > 500000:  # Very large position
        score += 5
    else:
        score += 10
    
    # Cap at 100
    score = min(100, max(0, score))
    
    return score


def get_grade(score):
    """Convert numerical score to letter grade"""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"


def analyze_trades(trades_df):
    """
    Add discipline scores and analysis to trades dataframe
    """
    if trades_df is None or len(trades_df) == 0:
        return None
    
    # Calculate discipline score for each trade
    trades_df['discipline_score'] = trades_df.apply(calculate_basic_discipline_score, axis=1)
    trades_df['grade'] = trades_df['discipline_score'].apply(get_grade)
    
    # Add some basic metrics
    trades_df['win'] = trades_df['net_pnl'] > 0
    trades_df['return_pct'] = ((trades_df['exit_price'] - trades_df['entry_price']) / 
                                trades_df['entry_price'] * 100).round(2)
    
    return trades_df


def get_summary_stats(trades_df):
    """
    Calculate portfolio-level statistics
    """
    if trades_df is None or len(trades_df) == 0:
        return None
    
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['net_pnl'] > 0])
    losing_trades = len(trades_df[trades_df['net_pnl'] < 0])
    
    stats = {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': round(winning_trades / total_trades * 100, 1) if total_trades > 0 else 0,
        
        'gross_pnl': trades_df['gross_pnl'].sum(),
        'total_charges': trades_df['total_charges'].sum(),
        'net_pnl': trades_df['net_pnl'].sum(),
        
        'avg_win': trades_df[trades_df['net_pnl'] > 0]['net_pnl'].mean() if winning_trades > 0 else 0,
        'avg_loss': trades_df[trades_df['net_pnl'] < 0]['net_pnl'].mean() if losing_trades > 0 else 0,
        
        'largest_win': trades_df['net_pnl'].max(),
        'largest_loss': trades_df['net_pnl'].min(),
        
        'avg_discipline_score': trades_df['discipline_score'].mean(),
        
        'total_brokerage': trades_df['brokerage'].sum() if 'brokerage' in trades_df.columns else 0,
        'total_stt': trades_df['stt'].sum() if 'stt' in trades_df.columns else 0,
    }
    
    # Profit factor
    total_wins = trades_df[trades_df['net_pnl'] > 0]['net_pnl'].sum()
    total_losses = abs(trades_df[trades_df['net_pnl'] < 0]['net_pnl'].sum())
    stats['profit_factor'] = round(total_wins / total_losses, 2) if total_losses > 0 else 0
    
    return stats


def detect_patterns(trades_df):
    """
    Detect behavioral patterns
    Phase 1: Basic patterns only
    """
    patterns = []
    
    if len(trades_df) < 5:
        return patterns
    
    # Pattern 1: Overtrading detection
    if len(trades_df) > 50:
        avg_trades_per_day = len(trades_df) / trades_df['entry_date'].nunique()
        if avg_trades_per_day > 5:
            patterns.append({
                'type': 'warning',
                'title': '⚠️ Possible Overtrading',
                'message': f'Average {avg_trades_per_day:.1f} trades per day. Consider reducing frequency.',
                'severity': 'medium'
            })
    
    # Pattern 2: Consecutive losses
    consecutive_losses = 0
    max_consecutive_losses = 0
    
    for _, trade in trades_df.iterrows():
        if trade['net_pnl'] < 0:
            consecutive_losses += 1
            max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        else:
            consecutive_losses = 0
    
    if max_consecutive_losses >= 5:
        patterns.append({
            'type': 'danger',
            'title': '🚨 Long Losing Streak Detected',
            'message': f'You had {max_consecutive_losses} consecutive losses. Take a break after 3 losses.',
            'severity': 'high'
        })
    
    # Pattern 3: Win rate vs profit factor mismatch
    stats = get_summary_stats(trades_df)
    if stats['win_rate'] > 60 and stats['profit_factor'] < 1:
        patterns.append({
            'type': 'warning',
            'title': '⚠️ Cutting Winners, Letting Losers Run',
            'message': f"Win rate is {stats['win_rate']:.0f}% but profit factor is {stats['profit_factor']:.2f}. Your losses are bigger than wins.",
            'severity': 'high'
        })
    
    return patterns
