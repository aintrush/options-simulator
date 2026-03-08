"""
Demonstration script for the Options Visualization Module

This script showcases all the visualization capabilities and provides
interactive examples for understanding options pricing and Greeks.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from visualization.greeks_plot import (
    plot_delta_vs_stock_price,
    plot_3d_option_surface,
    plot_greeks_comparison,
    plot_pnl_at_expiry,
    create_all_visualizations
)
import matplotlib.pyplot as plt

def main():
    """Run all visualization demonstrations."""
    
    print("="*60)
    print("OPTIONS VISUALIZATION DEMONSTRATION")
    print("="*60)
    
    # Example parameters
    S = 100    # Stock price
    K = 100    # Strike price (ATM)
    r = 0.05   # 5% risk-free rate
    sigma = 0.25  # 25% volatility
    
    print(f"\nUsing example parameters:")
    print(f"Stock Price: ${S}")
    print(f"Strike Price: ${K}")
    print(f"Risk-Free Rate: {r*100:.1f}%")
    print(f"Volatility: {sigma*100:.1f}%")
    
    # 1. Delta vs Stock Price
    print("\n1. Creating Delta vs Stock Price plot...")
    fig1 = plot_delta_vs_stock_price(S, K, r, sigma)
    plt.show()
    
    # 2. 3D Surface Plot
    print("\n2. Creating 3D option price surface...")
    fig2 = plot_3d_option_surface(S, K, r, sigma, 'call')
    plt.show()
    
    # 3. Greeks Comparison
    print("\n3. Creating Greeks comparison across volatilities...")
    fig3 = plot_greeks_comparison(S, K, 30/365, r)
    plt.show()
    
    # 4. Strategy Payoffs
    strategies = ['long_call', 'long_put', 'long_straddle', 'bull_call_spread', 'long_strangle']
    
    for strategy in strategies:
        print(f"\n4.{strategies.index(strategy)+1} Creating {strategy} payoff diagram...")
        fig4 = plot_pnl_at_expiry(strategy, S, K)
        plt.show()
    
    # Option to create all charts at once
    response = input("\nWould you like to create all visualization files at once? (y/n): ").lower()
    if response in ['y', 'yes']:
        print("\nCreating all visualization files...")
        create_all_visualizations(S, K, r, sigma)
        print("All files saved in the current directory!")
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
