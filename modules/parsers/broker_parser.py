"""
Main Broker Parser
Routes to specific broker parsers based on file format
"""

import pandas as pd
from modules.parsers.zerodha_parser import parse_zerodha
from modules.parsers.kotak_parser import parse_kotak
from modules.parsers.icici_parser import parse_icici

def detect_broker_format(file):
    """
    Auto-detect broker format from CSV structure
    Returns: broker_name, trade_type (for derivatives)
    """
    try:
        # Read first few rows to check format
        df = pd.read_csv(file, nrows=5, encoding='utf-8-sig')
        columns = [col.lower() for col in df.columns]
        
        # Check for Zerodha
        if 'symbol' in columns and 'order_execution_time' in columns and 'trade_type' in columns:
            return 'zerodha', 'equity'
        
        # Check for Kotak
        if 'trade date' in columns and 'security name' in columns and 'transaction type' in columns:
            # Check if derivatives (has FUTCOM or FUTSTK in security name)
            security_sample = df.iloc[0]['Security Name'] if 'Security Name' in df.columns else ''
            if 'FUT' in security_sample.upper() or 'OPT' in security_sample.upper():
                return 'kotak', 'derivatives'
            else:
                return 'kotak', 'equity'
        
        # Check for ICICI
        if 'stock' in columns and 'order ref.' in columns and 'settlement' in columns:
            return 'icici', 'equity'
        
        return None, None
    
    except Exception as e:
        return None, None


def parse_broker_file(file, broker=None, trade_type='equity'):
    """
    Main parsing function
    
    Args:
        file: Uploaded file object
        broker: 'zerodha', 'kotak', 'icici', or None (auto-detect)
        trade_type: 'equity' or 'derivatives' (for Kotak)
    
    Returns:
        DataFrame of trades, error message
    """
    # Auto-detect if broker not specified
    if broker is None:
        detected_broker, detected_type = detect_broker_format(file)
        if detected_broker is None:
            return None, "Could not auto-detect broker format. Please select manually."
        broker = detected_broker
        trade_type = detected_type
    
    # Reset file pointer
    file.seek(0)
    
    # Route to appropriate parser
    if broker == 'zerodha':
        trades, error = parse_zerodha(file)
    elif broker == 'kotak':
        trades, error = parse_kotak(file, trade_type)
    elif broker == 'icici':
        trades, error = parse_icici(file)
    else:
        return None, f"Unsupported broker: {broker}"
    
    return trades, error


def get_supported_brokers():
    """
    Returns list of supported brokers
    """
    return {
        'zerodha': 'Zerodha (Equity Tradebook)',
        'kotak_equity': 'Kotak Securities (Equity)',
        'kotak_derivatives': 'Kotak Securities (Derivatives)',
        'icici': 'ICICI Direct (Equity Orderbook)',
    }
