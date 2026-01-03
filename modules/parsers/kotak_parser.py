"""
Kotak Securities Parser
Handles both Equity and Derivatives transaction statements
"""

import pandas as pd
from datetime import datetime

def parse_kotak(file, trade_type='equity'):
    """
    Parse Kotak Securities transaction statement CSV
    
    trade_type: 'equity' or 'derivatives'
    
    Expected columns (both formats):
    Trade Date, Trade Time, Order Time, Security Name, ISIN, Exchange, 
    Order Source, Transaction Type, Quantity, Market Rate, Total, GST, 
    Brokerage, Misc., Total Charges, STT/CTT
    """
    try:
        # Read CSV - Kotak files have BOM (Byte Order Mark)
        df = pd.read_csv(file, encoding='utf-8-sig')
        
        # Validate format
        required_cols = ['Trade Date', 'Transaction Type', 'Quantity', 'Market Rate', 'Total Charges']
        if not all(col in df.columns for col in required_cols):
            return None, "Invalid Kotak format. Missing required columns."
        
        # Parse dates (Kotak uses DD/MM/YYYY format)
        df['trade_datetime'] = pd.to_datetime(
            df['Trade Date'] + ' ' + df['Trade Time'], 
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        df['trade_date_only'] = pd.to_datetime(df['Trade Date'], format='%d/%m/%Y', errors='coerce').dt.date
        
        # Standardize columns
        df['broker'] = 'Kotak Securities'
        df['stock_symbol'] = df['Security Name'].str.strip()
        df['action'] = df['Transaction Type'].str.capitalize()
        df['qty'] = df['Quantity'].astype(float)
        df['trade_price'] = df['Market Rate'].astype(float)
        df['trade_value'] = df['Total'].astype(float)
        
        # Charges (Kotak provides complete breakdown!)
        df['brokerage'] = df['Brokerage'].astype(float)
        df['gst'] = df['GST'].astype(float)
        df['stt'] = df['STT/CTT'].astype(float)
        df['misc_charges'] = df['Misc.'].astype(float)
        df['total_charges'] = df['Total Charges'].astype(float)
        
        # Add exchange info
        df['exchange'] = df['Exchange'].str.strip()
        df['trade_category'] = trade_type
        
        # Reconstruct trades
        trades = reconstruct_kotak_trades(df, trade_type)
        
        return trades, None
        
    except Exception as e:
        return None, f"Error parsing Kotak file: {str(e)}"


def reconstruct_kotak_trades(df, trade_type):
    """
    Kotak already separates buy/sell with individual P&L
    We just need to pair them for complete trade analysis
    """
    trades = []
    
    # Group by symbol and date
    for (symbol, date), group in df.groupby(['stock_symbol', 'trade_date_only']):
        buys = group[group['action'] == 'Buy'].copy()
        sells = group[group['action'] == 'Sell'].copy()
        
        if len(buys) == 0 or len(sells) == 0:
            # Incomplete trade (carry forward position)
            continue
        
        # Kotak can have multiple buy/sell in same day
        # Match closest quantities
        for _, buy_row in buys.iterrows():
            # Find matching sell (closest quantity)
            matching_sells = sells[abs(sells['qty'] - buy_row['qty']) < buy_row['qty'] * 0.1]  # Within 10%
            
            if len(matching_sells) == 0:
                continue
            
            sell_row = matching_sells.iloc[0]
            
            quantity = buy_row['qty']
            entry_price = buy_row['trade_price']
            exit_price = sell_row['trade_price']
            entry_time = buy_row['trade_datetime']
            exit_time = sell_row['trade_datetime']
            
            # Calculate P&L
            gross_pnl = (exit_price - entry_price) * quantity
            total_charges = buy_row['total_charges'] + sell_row['total_charges']
            net_pnl = gross_pnl - total_charges
            
            # Holding period
            if pd.notna(entry_time) and pd.notna(exit_time):
                holding_minutes = int((exit_time - entry_time).total_seconds() / 60)
            else:
                holding_minutes = 0
            
            trades.append({
                'broker': 'Kotak Securities',
                'symbol': symbol,
                'entry_date': date,
                'entry_time': entry_time if pd.notna(entry_time) else None,
                'exit_time': exit_time if pd.notna(exit_time) else None,
                'quantity': quantity,
                'entry_price': round(entry_price, 2),
                'exit_price': round(exit_price, 2),
                'gross_pnl': round(gross_pnl, 2),
                'brokerage': round(buy_row['brokerage'] + sell_row['brokerage'], 2),
                'stt': round(buy_row['stt'] + sell_row['stt'], 2),
                'gst': round(buy_row['gst'] + sell_row['gst'], 2),
                'misc_charges': round(buy_row['misc_charges'] + sell_row['misc_charges'], 2),
                'total_charges': round(total_charges, 2),
                'net_pnl': round(net_pnl, 2),
                'holding_period_minutes': holding_minutes,
                'trade_type': 'Intraday' if holding_minutes < 24*60 else 'Delivery',
                'trade_category': trade_type,
                'exchange': buy_row['exchange']
            })
            
            # Remove used sell to avoid duplicate matching
            sells = sells.drop(sell_row.name)
    
    return pd.DataFrame(trades)
