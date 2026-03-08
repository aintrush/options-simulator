"""
Test script to verify the Black-Scholes calculations work correctly.
"""

import sys
import os

# Add the project root to the Python path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.black_scholes import calculate_all_greeks, check_put_call_parity

def test_example():
    """Test with example values."""
    # Example: AAPL stock
    S = 100.0      # Stock price
    K = 105.0      # Strike price  
    T = 30/365.0   # 30 days to expiration
    r = 0.05       # 5% risk-free rate
    sigma = 0.25   # 25% volatility
    
    print("Testing Black-Scholes calculations...")
    print(f"Stock Price: ${S}")
    print(f"Strike Price: ${K}")
    print(f"Time to Expiry: {T*365:.0f} days")
    print(f"Risk-Free Rate: {r*100:.1f}%")
    print(f"Volatility: {sigma*100:.1f}%")
    print()
    
    # Calculate results
    results = calculate_all_greeks(S, K, T, r, sigma)
    
    print("RESULTS:")
    print("-" * 40)
    print(f"Call Price: ${results['call_price']:.4f}")
    print(f"Put Price:  ${results['put_price']:.4f}")
    print()
    print("GREEKS:")
    print("-" * 40)
    print(f"Call Delta: {results['call_delta']:.4f}")
    print(f"Put Delta:  {results['put_delta']:.4f}")
    print(f"Gamma:      {results['gamma']:.4f}")
    print(f"Call Theta: {results['call_theta']/365:.4f} (per day)")
    print(f"Put Theta:  {results['put_theta']/365:.4f} (per day)")
    print(f"Vega:       {results['vega']/100:.4f} (per 1%)")
    print(f"Call Rho:   {results['call_rho']/100:.4f} (per 1%)")
    print(f"Put Rho:    {results['put_rho']/100:.4f} (per 1%)")
    print()
    
    # Check put-call parity
    parity_holds, difference, tolerance = check_put_call_parity(S, K, T, r, sigma)
    print("PUT-CALL PARITY CHECK:")
    print("-" * 40)
    if parity_holds:
        print(f"✓ PUT-CALL PARITY HOLDS")
        print(f"  Difference: {difference:.8f} (within tolerance: {tolerance})")
    else:
        print(f"✗ PUT-CALL PARITY VIOLATION")
        print(f"  Difference: {difference:.8f} (tolerance: {tolerance})")
    
    # Verify put-call parity manually
    call_price = results['call_price']
    put_price = results['put_price']
    left_side = call_price - put_price
    right_side = S - K * (2.718281828 ** (-r * T))
    print(f"\nManual verification:")
    print(f"C - P = ${call_price:.4f} - ${put_price:.4f} = ${left_side:.4f}")
    print(f"S - K·e^(-rT) = ${S:.4f} - ${K:.4f}·e^(-{r:.4f}·{T:.4f}) = ${right_side:.4f}")
    print(f"Difference: ${abs(left_side - right_side):.8f}")

if __name__ == "__main__":
    test_example()
