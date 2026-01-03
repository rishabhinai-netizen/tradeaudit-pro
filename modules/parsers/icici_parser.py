"""
ICICI Direct Orderbook Parser
Handles ICICI Direct equity orderbook CSV format
"""

import pandas as pd
from datetime import datetime

def parse_icici(file):
    """
    Parse ICICI Direct orderbook CSV
    
    Expected columns:
    Date, Stock, Action, Qty, Price, Trade Value, Order Ref., Settlement, 
    Segment, DP Id, Exchange, STT, Transaction charges, Stamp Duty, 
    Brokerage + Service Tax, Brokerage Incl. Taxes
    """
    try:
        # Read CSV
        df = pd.read_csv(file)
        
        # Validate format
        required_cols = ['Date', 'Stock', 'Action', 'Qty', 'Price']
        if not all(col in df.columns for col in required_cols):
            return None, "Invalid ICICI Direct format. Missing required columns."
        
        # Parse dates (ICICI uses DD-MMM-YY format like "17-Dec-25")
        df['trade_date_only'] = pd.to_datetime(df['Date'], format='%d-%b-%y', errors='coerce').dt.date
        
        # ICICI doesn't provide time in orderbook, use date only
        df['trade_datetime'] = pd.to_datetime(df['Date'], format='%d-%b-%y', errors='coerce')
        
        # Standardize columns
        df['broker'] = 'ICICI Direct'
        df['stock_symbol'] = df['Stock'].astype(str).str.strip()
        df['action'] = df['Action'].astype(str).str.capitalize()
        
        # Handle numeric columns - they might be strings with commas
        def clean_numeric(col):
            if col.dtype == 'object':
                return col.astype(str).str.replace(',', '').astype(float)
            return col.astype(float)
        
        df['qty'] = clean_numeric(df['Qty'])
        df['trade_price'] = clean_numeric(df['Price'])
        df['trade_value'] = clean_numeric(df['Trade Value'])
        
        # Charges
        df['stt'] = clean_numeric(df['STT'])
        df['exchange_charges'] = clean_numeric(df['Transaction and SEBI Turnover charges'])
        df['stamp_duty'] = clean_numeric(df['Stamp Duty'])
        df['brokerage'] = clean_numeric(df['Brokerage Incl. Taxes'])
        df['total_charges'] = df['stt'] + df['exchange_charges'] + df['stamp_duty'] + df['brokerage']
        
        # Reconstruct trades
        trades = reconstruct_icici_trades(df)
        
        return trades, None
        
    except Exception as e:
        return None, f"Error parsing ICICI file: {str(e)}"


def reconstruct_icici_trades(df):
    """
    ICICI has multiple partial fills per order
    Group by stock and date, then match buy-sell
    """
    trades = []
    
    # Group by symbol and date
    for (symbol, date), group in df.groupby(['stock_symbol', 'trade_date_only']):
        buys = group[group['action'] == 'Buy'].copy()
        sells = group[group['action'] == 'Sell'].copy()
        
        if len(buys) == 0 or len(sells) == 0:
            # Incomplete trade
            continue
        
        # Sum all partial fills
        total_buy_qty = buys['qty'].sum()
        total_sell_qty = sells['qty'].sum()
        
        # Only process if quantities match
        if abs(total_buy_qty - total_sell_qty) > 0.01:
            continue
        
        # Calculate weighted average prices
        avg_buy_price = (buys['qty'] * buys['trade_price']).sum() / total_buy_qty
        avg_sell_price = (sells['qty'] * sells['trade_price']).sum() / total_sell_qty
        
        # Since ICICI doesn't have time, we can't calculate exact holding period
        # Assume trades on same date = intraday
        trade_type = 'Intraday'
        
        # Calculate P&L
        gross_pnl = (avg_sell_price - avg_buy_price) * total_buy_qty
        total_charges = buys['total_charges'].sum() + sells['total_charges'].sum()
        net_pnl = gross_pnl - total_charges
        
        trades.append({
            'broker': 'ICICI Direct',
            'symbol': symbol,
            'entry_date': date,
            'entry_time': None,  # Not available
            'exit_time': None,
            'quantity': total_buy_qty,
            'entry_price': round(avg_buy_price, 2),
            'exit_price': round(avg_sell_price, 2),
            'gross_pnl': round(gross_pnl, 2),
            'brokerage': round(buys['brokerage'].sum() + sells['brokerage'].sum(), 2),
            'stt': round(buys['stt'].sum() + sells['stt'].sum(), 2),
            'exchange_charges': round(buys['exchange_charges'].sum() + sells['exchange_charges'].sum(), 2),
            'stamp_duty': round(buys['stamp_duty'].sum() + sells['stamp_duty'].sum(), 2),
            'total_charges': round(total_charges, 2),
            'net_pnl': round(net_pnl, 2),
            'holding_period_minutes': 0,  # Unknown
            'trade_type': trade_type,
            'num_partial_fills_buy': len(buys),
            'num_partial_fills_sell': len(sells)
        })
    
    return pd.DataFrame(trades)
