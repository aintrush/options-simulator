"""
Advanced Visualization Module for Options Pricing & Greeks Simulator

This module provides comprehensive visualization capabilities for understanding
option pricing dynamics, Greeks behavior, and strategy payoffs.

Charts included:
1. Delta vs Stock Price for multiple expiry horizons
2. 3D surface of option prices across stock price and time
3. All Greeks comparison across different volatility levels
4. Strategy payoff diagrams at expiry
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.black_scholes import (
    call_price, put_price, call_delta, put_delta, gamma,
    call_theta, put_theta, vega, call_rho, put_rho
)

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
plt.rcParams['figure.titlesize'] = 14


def plot_delta_vs_stock_price(S=100, K=100, r=0.05, sigma=0.25):
    """
    Plot Delta vs Stock Price for both call and put options across multiple expiry horizons.
    
    This visualization shows how Delta changes as the underlying price moves and
    how time to expiration affects Delta's behavior. Key insights:
    - Delta approaches 1 for deep ITM calls, 0 for deep OTM calls
    - Shorter expirations create steeper Delta curves (more binary outcomes)
    - ATM options have Delta ≈ 0.5 for calls, -0.5 for puts
    
    Parameters:
    -----------
    S : float
        Current stock price (ATM strike)
    K : float  
        Strike price
    r : float
        Risk-free rate
    sigma : float
        Volatility
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Stock price range (50% to 150% of current price)
    stock_prices = np.linspace(S * 0.5, S * 1.5, 100)
    
    # Different expiry horizons
    expiries = [7/365, 30/365, 90/365]  # 7 days, 30 days, 90 days
    expiry_labels = ['7 days', '30 days', '90 days']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    # Plot Call Delta
    for i, (T, label, color) in enumerate(zip(expiries, expiry_labels, colors)):
        call_deltas = [call_delta(sp, K, T, r, sigma) for sp in stock_prices]
        ax1.plot(stock_prices, call_deltas, color=color, linewidth=2.5, 
                label=f'{label} (T={T:.3f})', alpha=0.8)
    
    # Add ATM vertical line for calls
    ax1.axvline(x=S, color='black', linestyle='--', alpha=0.5, linewidth=1.5)
    ax1.text(S, ax1.get_ylim()[1]*0.9, 'ATM', ha='center', fontsize=9, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.3))
    
    ax1.set_xlabel('Stock Price ($)')
    ax1.set_ylabel('Call Delta')
    ax1.set_title('Call Delta vs Stock Price')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-0.1, 1.1)
    
    # Plot Put Delta
    for i, (T, label, color) in enumerate(zip(expiries, expiry_labels, colors)):
        put_deltas = [put_delta(sp, K, T, r, sigma) for sp in stock_prices]
        ax2.plot(stock_prices, put_deltas, color=color, linewidth=2.5,
                label=f'{label} (T={T:.3f})', alpha=0.8)
    
    # Add ATM vertical line for puts
    ax2.axvline(x=S, color='black', linestyle='--', alpha=0.5, linewidth=1.5)
    ax2.text(S, ax2.get_ylim()[0]*0.9, 'ATM', ha='center', fontsize=9,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.3))
    
    ax2.set_xlabel('Stock Price ($)')
    ax2.set_ylabel('Put Delta')
    ax2.set_title('Put Delta vs Stock Price')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-1.1, 0.1)
    
    # Add parameter text box
    param_text = f'Parameters:\nS=${S:.1f}, K=${K:.1f}\nr={r*100:.1f}%, σ={sigma*100:.1f}%'
    fig.text(0.02, 0.98, param_text, transform=fig.transFigure, fontsize=9,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.suptitle('Delta Behavior Across Different Expiry Horizons', fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig


def plot_3d_option_surface(S=100, K=100, r=0.05, sigma=0.25, option_type='call'):
    """
    Create a 3D surface plot of option prices across stock price and time to expiry.
    
    This visualization shows how option prices evolve as both the underlying price
    and time to expiration change. Key insights:
    - Time value is highest for ATM options with longer expiration
    - Intrinsic value dominates for deep ITM options regardless of time
    - OTM options lose value rapidly as expiration approaches
    
    Parameters:
    -----------
    S : float
        Current stock price
    K : float
        Strike price  
    r : float
        Risk-free rate
    sigma : float
        Volatility
    option_type : str
        'call' or 'put'
    """
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create mesh grid
    stock_prices = np.linspace(S * 0.7, S * 1.3, 50)  # 70% to 130% of current price
    times_to_expiry = np.linspace(1/365, 90/365, 50)   # 1 day to 90 days
    S_grid, T_grid = np.meshgrid(stock_prices, times_to_expiry)
    
    # Calculate option prices across the grid
    if option_type == 'call':
        prices = np.array([[call_price(sp, K, t, r, sigma) for sp in stock_prices] 
                          for t in times_to_expiry])
        title = 'Call Option Price Surface'
        cmap = cm.RdYlBu_r
    else:
        prices = np.array([[put_price(sp, K, t, r, sigma) for sp in stock_prices] 
                          for t in times_to_expiry])
        title = 'Put Option Price Surface'
        cmap = cm.RdYlBu
    
    # Create surface plot
    surf = ax.plot_surface(S_grid, T_grid, prices, cmap=cmap, alpha=0.9,
                          linewidth=0.5, antialiased=True, edgecolors='gray')
    
    # Add colorbar
    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    cbar.set_label('Option Price ($)', rotation=270, labelpad=20)
    
    # Labels and title
    ax.set_xlabel('Stock Price ($)', fontsize=11)
    ax.set_ylabel('Time to Expiry (Years)', fontsize=11)
    ax.set_zlabel('Option Price ($)', fontsize=11)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Add parameter text
    param_text = f'S=${S:.1f}, K=${K:.1f}\nr={r*100:.1f}%, σ={sigma*100:.1f}%'
    ax.text2D(0.02, 0.98, param_text, transform=ax.transAxes, fontsize=10,
              verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Adjust viewing angle for better visualization
    ax.view_init(elev=25, azim=45)
    
    return fig


def plot_greeks_comparison(S=100, K=100, T=30/365, r=0.05):
    """
    Plot all five Greeks plus option price in a 2x3 subplot across different volatility levels.
    
    This comprehensive visualization shows how volatility affects each Greek.
    Key insights:
    - Higher volatility increases option prices (Vega is always positive)
    - Delta curves flatten with higher volatility (less certainty)
    - Gamma peaks for ATM options, increases with volatility
    - Theta (time decay) is most severe for ATM options
    - Rho effect is relatively small compared to other Greeks
    
    Parameters:
    -----------
    S : float
        Current stock price
    K : float
        Strike price
    T : float
        Time to expiry in years
    r : float
        Risk-free rate
    """
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()
    
    # Stock price range
    stock_prices = np.linspace(S * 0.7, S * 1.3, 100)
    
    # Different volatility levels
    vol_levels = [0.15, 0.25, 0.40]  # 15%, 25%, 40%
    vol_labels = ['Low (15%)', 'Medium (25%)', 'High (40%)']
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    # Calculate all Greeks and prices
    data = {
        'Option Price': [],
        'Delta': [],
        'Gamma': [],
        'Theta': [],
        'Vega': [],
        'Rho': []
    }
    
    for sigma in vol_levels:
        prices = [call_price(sp, K, T, r, sigma) for sp in stock_prices]
        deltas = [call_delta(sp, K, T, r, sigma) for sp in stock_prices]
        gammas = [gamma(sp, K, T, r, sigma) for sp in stock_prices]
        thetas = [call_theta(sp, K, T, r, sigma) / 365 for sp in stock_prices]  # Daily theta
        vegas = [vega(sp, K, T, r, sigma) / 100 for sp in stock_prices]  # Per 1%
        rhos = [call_rho(sp, K, T, r, sigma) / 100 for sp in stock_prices]  # Per 1%
        
        data['Option Price'].append(prices)
        data['Delta'].append(deltas)
        data['Gamma'].append(gammas)
        data['Theta'].append(thetas)
        data['Vega'].append(vegas)
        data['Rho'].append(rhos)
    
    # Plot each Greek
    titles = ['Option Price ($)', 'Delta', 'Gamma', 'Theta (daily)', 'Vega (per 1%)', 'Rho (per 1%)']
    ylabels = ['Price ($)', 'Delta', 'Gamma', 'Theta ($/day)', 'Vega ($/1%)', 'Rho ($/1%)']
    
    for i, (title, ylabel, key) in enumerate(zip(titles, ylabels, data.keys())):
        ax = axes[i]
        
        for j, (sigma, label, color) in enumerate(zip(vol_levels, vol_labels, colors)):
            ax.plot(stock_prices, data[key][j], color=color, linewidth=2.5,
                   label=label, alpha=0.8)
        
        # Add ATM line
        ax.axvline(x=S, color='black', linestyle='--', alpha=0.5, linewidth=1)
        
        ax.set_xlabel('Stock Price ($)')
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # Add parameter text box
    param_text = f'Parameters:\nS=${S:.1f}, K=${K:.1f}\nT={T*365:.0f} days, r={r*100:.1f}%'
    fig.text(0.02, 0.98, param_text, transform=fig.transFigure, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.suptitle('Greeks Behavior Across Different Volatility Levels', fontsize=16, fontweight='bold')
    plt.tight_layout()
    return fig


def plot_pnl_at_expiry(strategy='long_call', S=100, K1=100, K2=None, premium=None):
    """
    Plot P&L payoff diagrams for various options strategies at expiry.
    
    This visualization shows the risk/reward profile of different strategies.
    Key insights:
    - Long options: Limited risk, unlimited upside (calls) or limited upside (puts)
    - Spreads: Defined risk and reward, reduce premium cost
    - Straddles/Strangles: Profit from large price movements in either direction
    - Breakeven points show where strategy becomes profitable
    
    Parameters:
    -----------
    strategy : str
        Strategy type: 'long_call', 'long_put', 'long_straddle', 'bull_call_spread', 'long_strangle'
    S : float
        Current stock price
    K1 : float
        Primary strike price
    K2 : float
        Secondary strike price (for spreads and strangles)
    premium : float
        Option premium (calculated automatically if None)
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Stock price range for payoff diagram
    stock_prices = np.linspace(S * 0.5, S * 1.5, 200)
    
    # Calculate premiums if not provided
    if premium is None:
        if strategy == 'long_call':
            premium = call_price(S, K1, 30/365, 0.05, 0.25)
        elif strategy == 'long_put':
            premium = put_price(S, K1, 30/365, 0.05, 0.25)
        elif strategy == 'long_straddle':
            premium = call_price(S, K1, 30/365, 0.05, 0.25) + put_price(S, K1, 30/365, 0.05, 0.25)
        elif strategy == 'bull_call_spread':
            if K2 is None:
                K2 = K1 * 1.1  # Default 10% OTM
            premium = call_price(S, K1, 30/365, 0.05, 0.25) - call_price(S, K2, 30/365, 0.05, 0.25)
        elif strategy == 'long_strangle':
            if K2 is None:
                K2 = K1 * 1.1  # Default 10% OTM call
            K1 = K1 * 0.9  # 10% OTM put
            premium = call_price(S, K2, 30/365, 0.05, 0.25) + put_price(S, K1, 30/365, 0.05, 0.25)
    
    # Calculate payoffs
    payoffs = []
    breakeven_points = []
    
    for sp in stock_prices:
        if strategy == 'long_call':
            # Long call payoff: max(S-K,0) - premium
            payoff = max(sp - K1, 0) - premium
            breakeven_points.append(K1 + premium)
            
        elif strategy == 'long_put':
            # Long put payoff: max(K-S,0) - premium
            payoff = max(K1 - sp, 0) - premium
            breakeven_points.append(K1 - premium)
            
        elif strategy == 'long_straddle':
            # Long straddle: max(S-K,0) + max(K-S,0) - total_premium
            payoff = max(sp - K1, 0) + max(K1 - sp, 0) - premium
            breakeven_points.extend([K1 - premium/2, K1 + premium/2])
            
        elif strategy == 'bull_call_spread':
            # Bull call spread: max(S-K1,0) - max(S-K2,0) - net_premium
            payoff = max(sp - K1, 0) - max(sp - K2, 0) - premium
            breakeven_points.append(K1 + premium)
            
        elif strategy == 'long_strangle':
            # Long strangle: max(S-K2,0) + max(K1-S,0) - total_premium
            payoff = max(sp - K2, 0) + max(K1 - sp, 0) - premium
            breakeven_points.extend([K1 - premium/2, K2 + premium/2])
        
        payoffs.append(payoff)
    
    # Plot payoff diagram
    ax.plot(stock_prices, payoffs, 'b-', linewidth=3, label='Payoff at Expiry')
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
    ax.axvline(x=S, color='red', linestyle='--', alpha=0.7, linewidth=2, label=f'Current Price: ${S:.1f}')
    
    # Mark breakeven points
    for be in breakeven_points:
        if S * 0.5 <= be <= S * 1.5:  # Only show if in plot range
            ax.axvline(x=be, color='green', linestyle=':', alpha=0.8, linewidth=2)
            ax.text(be, ax.get_ylim()[1]*0.1, f'BE: ${be:.2f}', 
                   rotation=90, ha='right', va='bottom', fontsize=9,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
    
    # Highlight profit and loss regions
    ax.fill_between(stock_prices, 0, payoffs, where=(np.array(payoffs) > 0), 
                   alpha=0.3, color='green', label='Profit Region')
    ax.fill_between(stock_prices, 0, payoffs, where=(np.array(payoffs) < 0), 
                   alpha=0.3, color='red', label='Loss Region')
    
    # Labels and formatting
    ax.set_xlabel('Stock Price at Expiry ($)', fontsize=12)
    ax.set_ylabel('Profit/Loss ($)', fontsize=12)
    
    # Strategy-specific titles
    strategy_titles = {
        'long_call': 'Long Call Strategy',
        'long_put': 'Long Put Strategy', 
        'long_straddle': 'Long Straddle Strategy',
        'bull_call_spread': 'Bull Call Spread Strategy',
        'long_strangle': 'Long Strangle Strategy'
    }
    
    ax.set_title(f'{strategy_titles.get(strategy, strategy)} - Payoff at Expiry', 
                fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # Add parameter text box
    if strategy in ['long_call', 'long_put']:
        param_text = f'Parameters:\nStrike: ${K1:.1f}\nPremium Paid: ${premium:.2f}\nCurrent Price: ${S:.1f}'
    elif strategy == 'long_straddle':
        param_text = f'Parameters:\nStrike: ${K1:.1f}\nTotal Premium: ${premium:.2f}\nCurrent Price: ${S:.1f}'
    elif strategy == 'bull_call_spread':
        param_text = f'Parameters:\nLong K1: ${K1:.1f}, Short K2: ${K2:.1f}\nNet Premium: ${premium:.2f}\nCurrent Price: ${S:.1f}'
    elif strategy == 'long_strangle':
        param_text = f'Parameters:\nPut K1: ${K1:.1f}, Call K2: ${K2:.1f}\nTotal Premium: ${premium:.2f}\nCurrent Price: ${S:.1f}'
    
    ax.text(0.02, 0.98, param_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    return fig


def create_all_visualizations(S=100, K=100, r=0.05, sigma=0.25):
    """
    Create all visualization charts and save them.
    
    This function generates all the visualization charts and saves them
    as PNG files for easy inclusion in presentations or reports.
    
    Parameters:
    -----------
    S, K, r, sigma : float
        Black-Scholes parameters
    """
    print("Creating all visualizations...")
    
    # 1. Delta vs Stock Price
    fig1 = plot_delta_vs_stock_price(S, K, r, sigma)
    fig1.savefig('delta_vs_stock_price.png', dpi=300, bbox_inches='tight')
    plt.close(fig1)
    print("✓ Delta vs Stock Price chart saved")
    
    # 2. 3D Surface Plots
    fig2_call = plot_3d_option_surface(S, K, r, sigma, 'call')
    fig2_call.savefig('call_price_surface.png', dpi=300, bbox_inches='tight')
    plt.close(fig2_call)
    print("✓ Call price surface saved")
    
    fig2_put = plot_3d_option_surface(S, K, r, sigma, 'put')
    fig2_put.savefig('put_price_surface.png', dpi=300, bbox_inches='tight')
    plt.close(fig2_put)
    print("✓ Put price surface saved")
    
    # 3. Greeks Comparison
    fig3 = plot_greeks_comparison(S, K, 30/365, r)
    fig3.savefig('greeks_comparison.png', dpi=300, bbox_inches='tight')
    plt.close(fig3)
    print("✓ Greeks comparison chart saved")
    
    # 4. Strategy Payoffs
    strategies = ['long_call', 'long_put', 'long_straddle', 'bull_call_spread', 'long_strangle']
    for strategy in strategies:
        fig4 = plot_pnl_at_expiry(strategy, S, K)
        fig4.savefig(f'{strategy}_payoff.png', dpi=300, bbox_inches='tight')
        plt.close(fig4)
        print(f"✓ {strategy} payoff diagram saved")
    
    print("\nAll visualizations created successfully!")


if __name__ == "__main__":
    # Create all visualizations with default parameters
    create_all_visualizations()
    
    # Display examples interactively
    print("\nDisplaying example charts...")
    plt.show()
