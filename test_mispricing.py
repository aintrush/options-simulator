"""
Test script for the mispricing scanner functionality.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.nse_fetcher import scan_mispricing, save_mispricing_results
import pandas as pd

def test_mispricing_scanner():
    """Test the mispricing scanner with sample data."""
    
    print("Testing Mispricing Scanner...")
    print("="*50)
    
    # Test with a stock that has options data
    ticker = "AAPL"  # Apple has good options data
    threshold = 0.10  # 10% threshold for testing
    
    try:
        # Run the scan
        results = scan_mispricing(ticker, threshold)
        
        if not results.empty:
            print(f"✓ Found {len(results)} mispriced options")
            print("\nTop 5 results:")
            print(results[['type', 'strike', 'market_price', 'theoretical_price', 
                          'mispricing_pct']].head())
            
            # Save results
            save_mispricing_results(results, ticker, threshold)
            print("\n✓ Test completed successfully")
        else:
            print("✓ No mispriced options found (this is normal)")
            print("✓ Test completed successfully")
            
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_mispricing_scanner()
