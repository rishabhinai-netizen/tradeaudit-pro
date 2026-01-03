"""
Zerodha Tradebook Parser
Handles Zerodha equity tradebook CSV format
"""

import pandas as pd
from datetime import datetime

def parse_zerodha(file):
    """
    Parse Zerodha tradebook CSV
    
    Expected columns:
    symbol, isin, trade_date, exchange, segment, series, trade_type, 
    auction, quantity, price, trade_id, order_id, order_execution_time
    """
    try:
        # Read CSV
        df = pd.read_csv(file)
        
        # Validate format
        required_cols = ['symbol', 'trade_date', 'trade_type', 'quantity', 'price', 'order_execution_time']
        if not all(col in df.columns for col in required_cols):
            return None, "Invalid Zerodha format. Missing required columns."
        
        # Parse datetime
        df['trade_datetime'] = pd.to_datetime(df['order_execution_time'])
        df['trade_date_only'] = pd.to_datetime(df['trade_date']).dt.date
        
        # Standardize columns
        df['broker'] = 'Zerodha'
        df['stock_symbol'] = df['symbol']
        df['action'] = df['trade_type'].str.capitalize()  # Buy/Sell
        df['qty'] = df['quantity'].astype(float)
        df['trade_price'] = df['price'].astype(float)
        df['trade_value'] = df['qty'] * df['trade_price']
        
        # Zerodha doesn't provide charges in tradebook
        # We'll estimate based on standard charges
        df['brokerage'] = 0  # Zerodha is ₹20/order or 0.03%, whichever lower
        df['stt'] = 0
        df['exchange_charges'] = 0
        df['gst'] = 0
        df['stamp_duty'] = 0
        df['total_charges'] = 0
        
        # Calculate estimated charges
        df = calculate_zerodha_charges(df)
        
        # Group partial fills into single trades
        trades = reconstruct_zerodha_trades(df)
        
        return trades, None
        
    except Exception as e:
        return None, f"Error parsing Zerodha file: {str(e)}"


def calculate_zerodha_charges(df):
    """
    Calculate approximate Zerodha charges
    Zerodha charges: ₹20/order or 0.03% of turnover, whichever is lower
    """
    for idx, row in df.iterrows():
        turnover = row['trade_value']
        
        # Brokerage (₹20 or 0.03%)
        brokerage_pct = turnover * 0.0003  # 0.03%
        brokerage = min(20, brokerage_pct)
        
        # STT (0.1% on sell side for delivery, 0.025% for intraday)
        if row['action'] == 'Sell':
            stt = turnover * 0.001  # 0.1% (assuming delivery)
        else:
            stt = 0
        
        # Exchange charges (NSE: 0.00325%)
        exchange_charges = turnover * 0.0000325
        
        # SEBI charges (0.0001%)
        sebi_charges = turnover * 0.000001
        
        # Stamp duty (0.015% on buy side)
        if row['action'] == 'Buy':
            stamp_duty = turnover * 0.00015
        else:
            stamp_duty = 0
        
        # GST (18% on brokerage + exchange charges)
        gst = (brokerage + exchange_charges) * 0.18
        
        # Total
        total_charges = brokerage + stt + exchange_charges + sebi_charges + stamp_duty + gst
        
        df.at[idx, 'brokerage'] = round(brokerage, 2)
        df.at[idx, 'stt'] = round(stt, 2)
        df.at[idx, 'exchange_charges'] = round(exchange_charges + sebi_charges, 2)
        df.at[idx, 'stamp_duty'] = round(stamp_duty, 2)
        df.at[idx, 'gst'] = round(gst, 2)
        df.at[idx, 'total_charges'] = round(total_charges, 2)
    
    return df


def reconstruct_zerodha_trades(df):
    """
    Group partial fills into complete trades
    Match buy-sell pairs for same stock on same day
    """
    trades = []
    
    # Group by symbol and date
    for (symbol, date), group in df.groupby(['stock_symbol', 'trade_date_only']):
        buys = group[group['action'] == 'Buy'].copy()
        sells = group[group['action'] == 'Sell'].copy()
        
        if len(buys) == 0 or len(sells) == 0:
            # Incomplete trade (open position or data issue)
            continue
        
        # Calculate weighted average prices
        total_buy_qty = buys['qty'].sum()
        total_sell_qty = sells['qty'].sum()
        
        # Only process if quantities match (closed position)
        if abs(total_buy_qty - total_sell_qty) > 0.01:  # Allow small rounding errors
            continue
        
        avg_buy_price = (buys['qty'] * buys['trade_price']).sum() / total_buy_qty
        avg_sell_price = (sells['qty'] * sells['trade_price']).sum() / total_sell_qty
        
        entry_time = buys['trade_datetime'].min()
        exit_time = sells['trade_datetime'].max()
        
        # Calculate P&L
        gross_pnl = (avg_sell_price - avg_buy_price) * total_buy_qty
        total_charges = buys['total_charges'].sum() + sells['total_charges'].sum()
        net_pnl = gross_pnl - total_charges
        
        trades.append({
            'broker': 'Zerodha',
            'symbol': symbol,
            'entry_date': entry_time.date(),
            'entry_time': entry_time,
            'exit_time': exit_time,
            'quantity': total_buy_qty,
            'entry_price': round(avg_buy_price, 2),
            'exit_price': round(avg_sell_price, 2),
            'gross_pnl': round(gross_pnl, 2),
            'total_charges': round(total_charges, 2),
            'net_pnl': round(net_pnl, 2),
            'holding_period_minutes': int((exit_time - entry_time).total_seconds() / 60),
            'trade_type': 'Intraday' if (exit_time.date() == entry_time.date()) else 'Delivery',
            'num_partial_fills_buy': len(buys),
            'num_partial_fills_sell': len(sells)
        })
    
    return pd.DataFrame(trades)
