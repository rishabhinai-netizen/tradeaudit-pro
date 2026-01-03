"""
Test Script - Verify Parsers Work
Run this to test if everything is working before using Streamlit
"""

import sys
sys.path.append('.')

from modules.parsers.broker_parser import parse_broker_file
from modules.analysis.discipline_scorer import analyze_trades, get_summary_stats

def test_parser(filepath, broker=None, trade_type='equity'):
    """Test a single file"""
    print(f"\n{'='*60}")
    print(f"Testing: {filepath}")
    print(f"{'='*60}")
    
    try:
        with open(filepath, 'rb') as f:
            trades_df, error = parse_broker_file(f, broker, trade_type)
        
        if error:
            print(f"❌ ERROR: {error}")
            return False
        
        if trades_df is None or len(trades_df) == 0:
            print("⚠️  No trades found")
            return False
        
        # Analyze
        trades_df = analyze_trades(trades_df)
        stats = get_summary_stats(trades_df)
        
        # Print results
        print(f"\n✅ Successfully parsed {len(trades_df)} trades!")
        print(f"\n📊 Summary:")
        print(f"   Total Trades: {stats['total_trades']}")
        print(f"   Winners: {stats['winning_trades']}")
        print(f"   Losers: {stats['losing_trades']}")
        print(f"   Win Rate: {stats['win_rate']:.1f}%")
        print(f"   Net P&L: ₹{stats['net_pnl']:,.2f}")
        print(f"   Avg Discipline: {stats['avg_discipline_score']:.1f}/100")
        
        # Show first 3 trades
        print(f"\n📋 Sample Trades:")
        for idx, trade in trades_df.head(3).iterrows():
            print(f"\n   {trade['symbol']}:")
            print(f"      Entry: ₹{trade['entry_price']} × {trade['quantity']}")
            print(f"      Exit:  ₹{trade['exit_price']}")
            print(f"      P&L:   ₹{trade['net_pnl']:,.2f}")
            print(f"      Score: {trade['discipline_score']:.0f}/100 ({trade['grade']})")
        
        return True
        
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TRADEAUDIT PRO - PARSER TEST")
    print("="*60)
    
    # Test all sample files
    test_files = [
        ('sample_data/Zerodha_Tradebook-BX9133-EQ.csv', 'zerodha', 'equity'),
        ('sample_data/Kotak_Equity_-_Transaction_Statement_YIPQH_20250401_20260103__1_.csv', 'kotak', 'equity'),
        ('sample_data/Kotak_Derivatives_-_Transaction_Statement_YIPQH_20250401_20260103.csv', 'kotak', 'derivatives'),
        ('sample_data/ICICI_Direct_Equity_-_orderBook_Equity_1767439970228.csv', 'icici', 'equity'),
    ]
    
    results = []
    for filepath, broker, trade_type in test_files:
        success = test_parser(filepath, broker, trade_type)
        results.append((filepath.split('/')[-1], success))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}\n")
    
    for filename, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {filename}")
    
    total_pass = sum(1 for _, s in results if s)
    print(f"\n{total_pass}/{len(results)} tests passed")
    
    if total_pass == len(results):
        print("\n🎉 ALL TESTS PASSED! Ready to use Streamlit app.")
        print("\nRun: streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
