"""
Interactive Mispricing Scanner - User Interface and Visualization

This script provides an interactive interface for scanning options mispricing
opportunities and visualizing the results.

Features:
- User-friendly interface for ticker input
- Real-time mispricing scanning
- Formatted results display
- Mispricing visualization charts
- CSV export functionality
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.nse_fetcher import scan_mispricing, save_mispricing_results, format_mispricing_table
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# Set professional plotting style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9


def get_user_input():
    """
    Get user input for scanning parameters.
    
    Returns:
    --------
    tuple : (ticker, threshold, top_n, save_chart)
        ticker : str
            Stock ticker symbol
        threshold : float
            Mispricing threshold
        top_n : int
            Number of top results to display
        save_chart : bool
            Whether to save chart
    """
    print("="*60)
    print("OPTIONS MISPRICING SCANNER")
    print("="*60)
    print("\nThis scanner compares Black-Scholes theoretical prices")
    print("to actual market prices to identify potential inefficiencies.\n")
    
    # Get ticker with default
    while True:
        ticker_input = input("Enter ticker symbol (default: AAPL): ").strip()
        if not ticker_input:
            ticker = "AAPL"
        else:
            ticker = ticker_input.upper()
        
        # Accept any ticker (NSE, US stocks, etc.)
        if ticker:  # Just ensure ticker is not empty
            break
        else:
            print("Please enter a valid ticker symbol")
    
    # Get threshold
    while True:
        try:
            threshold_input = input("Enter mispricing threshold % (default: 5): ").strip()
            if not threshold_input:
                threshold = 0.05  # 5%
            else:
                threshold = float(threshold_input) / 100.0
            
            if 0 < threshold <= 1:
                break
            else:
                print("Threshold must be between 0% and 100%")
        except ValueError:
            print("Please enter a valid number")
    
    # Get top N results
    while True:
        try:
            top_n_input = input("Number of top results to display (default: 10): ").strip()
            if not top_n_input:
                top_n = 10
            else:
                top_n = int(top_n_input)
            
            if 1 <= top_n <= 50:
                break
            else:
                print("Please enter a number between 1 and 50")
        except ValueError:
            print("Please enter a valid number")
    
    # Ask about saving chart
    save_chart = input("Save mispricing chart? (y/n, default: y): ").strip().lower()
    save_chart = save_chart in ['y', 'yes', '']
    
    return ticker, threshold, top_n, save_chart


def create_mispricing_chart(mispriced_df, ticker, threshold):
    """
    Create a bar chart showing mispricing percentages by strike.
    
    This visualization helps identify patterns in mispricing:
    - Are certain strikes consistently mispriced?
    - Is there a pattern between calls and puts?
    - How large are the mispricings relative to the threshold?
    
    Parameters:
    -----------
    mispriced_df : pd.DataFrame
        Mispriced options data
    ticker : str
        Stock ticker
    threshold : float
        Mispricing threshold used
    """
    if mispriced_df.empty:
        print("No data to chart")
        return
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Prepare data
    calls_df = mispriced_df[mispriced_df['type'] == 'CALL'].head(15)
    puts_df = mispriced_df[mispriced_df['type'] == 'PUT'].head(15)
    
    # Plot 1: Mispricing by Strike (Calls)
    if not calls_df.empty:
        colors_calls = ['red' if x > 0 else 'green' for x in calls_df['mispricing_amount']]
        bars1 = ax1.bar(range(len(calls_df)), calls_df['mispricing_pct'] * 100, 
                       color=colors_calls, alpha=0.7, edgecolor='black')
        
        ax1.set_xlabel('Call Options (sorted by mispricing)')
        ax1.set_ylabel('Mispricing (%)')
        ax1.set_title(f'CALL Options Mispricing - {ticker}', fontweight='bold')
        ax1.axhline(y=threshold*100, color='orange', linestyle='--', 
                   linewidth=2, label=f'Threshold: {threshold*100:.1f}%')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Add strike labels on x-axis
        strike_labels = [f"₹{int(s)}" for s in calls_df['strike']]
        ax1.set_xticks(range(len(calls_df)))
        ax1.set_xticklabels(strike_labels, rotation=45)
        
        # Add value labels on bars
        for i, (bar, pct) in enumerate(zip(bars1, calls_df['mispricing_pct'] * 100)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{pct:.1f}%', ha='center', va='bottom', fontsize=8)
    
    else:
        ax1.text(0.5, 0.5, 'No mispriced calls found', ha='center', va='center', 
                transform=ax1.transAxes, fontsize=12)
        ax1.set_title(f'CALL Options Mispricing - {ticker}', fontweight='bold')
    
    # Plot 2: Mispricing by Strike (Puts)
    if not puts_df.empty:
        colors_puts = ['red' if x > 0 else 'green' for x in puts_df['mispricing_amount']]
        bars2 = ax2.bar(range(len(puts_df)), puts_df['mispricing_pct'] * 100, 
                       color=colors_puts, alpha=0.7, edgecolor='black')
        
        ax2.set_xlabel('Put Options (sorted by mispricing)')
        ax2.set_ylabel('Mispricing (%)')
        ax2.set_title(f'PUT Options Mispricing - {ticker}', fontweight='bold')
        ax2.axhline(y=threshold*100, color='orange', linestyle='--', 
                   linewidth=2, label=f'Threshold: {threshold*100:.1f}%')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Add strike labels on x-axis
        strike_labels = [f"₹{int(s)}" for s in puts_df['strike']]
        ax2.set_xticks(range(len(puts_df)))
        ax2.set_xticklabels(strike_labels, rotation=45)
        
        # Add value labels on bars
        for i, (bar, pct) in enumerate(zip(bars2, puts_df['mispricing_pct'] * 100)):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{pct:.1f}%', ha='center', va='bottom', fontsize=8)
    
    else:
        ax2.text(0.5, 0.5, 'No mispriced puts found', ha='center', va='center', 
                transform=ax2.transAxes, fontsize=12)
        ax2.set_title(f'PUT Options Mispricing - {ticker}', fontweight='bold')
    
    # Add overall title and parameter info
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    param_text = f"Scan Time: {timestamp}\nThreshold: {threshold*100:.1f}%\nTotal Mispriced: {len(mispriced_df)}"
    fig.text(0.02, 0.98, param_text, transform=fig.transFigure, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Add color legend
    red_patch = plt.Rectangle((0, 0), 1, 1, fc='red', alpha=0.7, label='Overpriced (Market > Theory)')
    green_patch = plt.Rectangle((0, 0), 1, 1, fc='green', alpha=0.7, label='Underpriced (Market < Theory)')
    fig.legend(handles=[red_patch, green_patch], loc='lower center', bbox_to_anchor=(0.5, 0.02), 
              ncol=2, frameon=True)
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)  # Make room for legend
    
    return fig


def create_summary_statistics(mispriced_df):
    """
    Create summary statistics for the mispricing scan.
    
    Parameters:
    -----------
    mispriced_df : pd.DataFrame
        Mispriced options data
    
    Returns:
    --------
    str : Formatted summary statistics
    """
    if mispriced_df.empty:
        return "No mispriced options found."
    
    stats = []
    
    # Overall statistics
    total_contracts = len(mispriced_df)
    calls_count = len(mispriced_df[mispriced_df['type'] == 'CALL'])
    puts_count = len(mispriced_df[mispriced_df['type'] == 'PUT'])
    
    avg_mispricing = mispriced_df['mispricing_pct'].mean() * 100
    max_mispricing = mispriced_df['mispricing_pct'].max() * 100
    min_mispricing = mispriced_df['mispricing_pct'].min() * 100
    
    # Direction analysis
    overpriced = len(mispriced_df[mispriced_df['mispricing_amount'] > 0])
    underpriced = len(mispriced_df[mispriced_df['mispricing_amount'] < 0])
    
    # Liquidity analysis
    avg_volume = mispriced_df['volume'].mean()
    avg_open_interest = mispriced_df['open_interest'].mean()
    avg_bid_ask_spread = mispriced_df['bid_ask_spread'].mean()
    
    stats.append("MISPRICING SCAN SUMMARY")
    stats.append("="*40)
    stats.append(f"Total Mispriced Contracts: {total_contracts}")
    stats.append(f"  Calls: {calls_count}")
    stats.append(f"  Puts: {puts_count}")
    stats.append("")
    stats.append("MISPRICING STATISTICS:")
    stats.append(f"  Average Mispricing: {avg_mispricing:.2f}%")
    stats.append(f"  Maximum Mispricing: {max_mispricing:.2f}%")
    stats.append(f"  Minimum Mispricing: {min_mispricing:.2f}%")
    stats.append("")
    stats.append("DIRECTION ANALYSIS:")
    stats.append(f"  Overpriced (Market > Theory): {overpriced}")
    stats.append(f"  Underpriced (Market < Theory): {underpriced}")
    stats.append("")
    stats.append("LIQUIDITY METRICS:")
    stats.append(f"  Average Volume: {avg_volume:.0f}")
    stats.append(f"  Average Open Interest: {avg_open_interest:.0f}")
    stats.append(f"  Average Bid-Ask Spread: ₹{avg_bid_ask_spread:.2f}")
    
    return "\n".join(stats)


def display_results(mispriced_df, ticker, threshold, top_n):
    """
    Display the mispricing scan results in a formatted way.
    
    Parameters:
    -----------
    mispriced_df : pd.DataFrame
        Mispriced options data
    ticker : str
        Stock ticker
    threshold : float
        Mispricing threshold used
    top_n : int
        Number of top results to display
    """
    print("\n" + "="*60)
    print(f"MISPRICING SCAN RESULTS FOR {ticker}")
    print("="*60)
    
    if mispriced_df.empty:
        print("No mispriced options found.")
        print("This could mean:")
        print("  • Options are efficiently priced")
        print("  • Historical volatility differs significantly from implied volatility")
        print("  • Bid-ask spreads are too wide for arbitrage opportunities")
        print("  • Market conditions have changed recently")
        return
    
    # Display summary statistics
    print(create_summary_statistics(mispriced_df))
    print("\n" + "="*60)
    
    # Display top results
    print(f"\nTOP {top_n} MISPRICED OPTIONS:")
    print("="*60)
    print(format_mispricing_table(mispriced_df, top_n))
    
    # Display warnings and cautions
    print("\n" + "="*60)
    print("IMPORTANT CAUTIONS:")
    print("="*60)
    print("⚠️  These are theoretical mispricings, not guaranteed arbitrage opportunities")
    print("📊 Historical volatility may differ from current implied volatility")
    print("💰 Transaction costs (bid-ask spreads, brokerage, taxes) can eliminate profits")
    print("⏱️  Prices can change between analysis and execution")
    print("🏦  Consider liquidity, volume, and open interest before trading")
    print("📈  This analysis doesn't account for dividends, early exercise, or corporate actions")


def main():
    """
    Main function to run the interactive mispricing scanner.
    """
    print("Welcome to the Options Mispricing Scanner!")
    print("This tool helps identify potentially mispriced options by comparing")
    print("Black-Scholes theoretical prices to actual market prices.\n")
    
    while True:
        try:
            # Get user input
            ticker, threshold, top_n, save_chart = get_user_input()
            
            print(f"\nScanning {ticker} for mispriced options...")
            print("This may take a moment to fetch market data...\n")
            
            # Run the scan
            mispriced_df = scan_mispricing(ticker, threshold)
            
            # Display results
            display_results(mispriced_df, ticker, threshold, top_n)
            
            # Create and save chart if requested
            if save_chart and not mispriced_df.empty:
                print("\nCreating mispricing chart...")
                fig = create_mispricing_chart(mispriced_df, ticker, threshold)
                
                # Save chart
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                chart_filename = f"mispricing_chart_{ticker}_{timestamp}.png"
                fig.savefig(chart_filename, dpi=300, bbox_inches='tight')
                fig.savefig("mispricing_chart.png", dpi=300, bbox_inches='tight')  # Generic name
                
                print(f"✓ Chart saved as: {chart_filename}")
                print("✓ Chart also saved as: mispricing_chart.png")
                plt.show()
            
            # Save results to CSV
            if not mispriced_df.empty:
                save_mispricing_results(mispriced_df, ticker, threshold)
            
            # Ask if user wants to run another scan
            print("\n" + "="*60)
            another_scan = input("Would you like to run another scan? (y/n): ").strip().lower()
            if another_scan not in ['y', 'yes']:
                print("\nThank you for using the Options Mispricing Scanner!")
                break
            print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nScan interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\nError during scan: {str(e)}")
            retry = input("Would you like to try again? (y/n): ").strip().lower()
            if retry not in ['y', 'yes']:
                break
            print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
