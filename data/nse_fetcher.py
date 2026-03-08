"""
NSE Options Data Fetcher and Mispricing Scanner

This module provides real-world validation by comparing Black-Scholes theoretical
prices to actual market data from NSE (National Stock Exchange of India) using
yfinance data.

Key Features:
- Fetch live stock prices and historical data for NSE stocks
- Calculate historical volatility from log returns
- Retrieve options chains and identify mispricing opportunities
- Export results for further analysis

IMPORTANT LIMITATIONS:
- Historical volatility is an imperfect proxy for implied volatility
- Real arbitrage faces transaction costs, bid-ask spreads, and execution risks
- Market prices include factors not captured by basic Black-Scholes
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for Black-Scholes imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.black_scholes import call_price, put_price

# Set pandas display options for better readability
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', '{:.4f}'.format)


def get_stock_data(ticker, period="30d"):
    """
    Fetch current stock price and historical data for an NSE stock.
    
    Parameters:
    -----------
    ticker : str
        NSE ticker symbol (e.g., "RELIANCE.NS", "INFY.NS")
    period : str
        Historical data period (default: "30d" for 30 days)
    
    Returns:
    --------
    tuple : (current_price, historical_data)
        current_price : float
            Latest stock price
        historical_data : pd.DataFrame
            Historical OHLCV data
    """
    try:
        # Create ticker object
        stock = yf.Ticker(ticker)
        
        # Fetch historical data
        hist_data = stock.history(period=period)
        
        if hist_data.empty:
            raise ValueError(f"No historical data found for {ticker}")
        
        # Get current price (last close price)
        current_price = hist_data['Close'].iloc[-1]
        
        print(f"✓ Successfully fetched data for {ticker}")
        print(f"  Current Price: ₹{current_price:.2f}")
        print(f"  Data Period: {len(hist_data)} days")
        
        return current_price, hist_data
        
    except Exception as e:
        print(f"✗ Error fetching data for {ticker}: {str(e)}")
        raise


def calculate_historical_volatility(historical_data, trading_days_per_year=252):
    """
    Calculate historical volatility from log returns of closing prices.
    
    HISTORICAL VOLATILITY FORMULA:
    σ = √(Var[ln(P_t/P_{t-1})]) × √(trading_days_per_year)
    
    Where:
    - ln(P_t/P_{t-1}) are the log returns (continuously compounded returns)
    - Var[...] is the variance of these log returns
    - √(trading_days_per_year) annualizes the daily volatility
    
    WHY LOG RETURNS:
    - Log returns are continuously compounded and additive over time
    - They follow a more normal distribution than simple returns
    - They align with the assumptions of the Black-Scholes model
    
    LIMITATIONS AS IV PROXY:
    - Historical volatility looks backward, implied volatility looks forward
    - Market conditions may have changed since the historical period
    - Earnings announcements, news events can cause volatility regime changes
    - Implied volatility includes risk premium for uncertainty
    
    Parameters:
    -----------
    historical_data : pd.DataFrame
        Historical stock price data with 'Close' column
    trading_days_per_year : int
        Number of trading days in a year (default: 252 for Indian markets)
    
    Returns:
    --------
    float : Annualized historical volatility (as decimal, e.g., 0.25 for 25%)
    """
    if len(historical_data) < 2:
        raise ValueError("Need at least 2 days of data to calculate volatility")
    
    # Calculate log returns: ln(P_t/P_{t-1})
    log_returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1))
    
    # Remove the first NaN value
    log_returns = log_returns.dropna()
    
    # Calculate daily volatility (standard deviation of log returns)
    daily_volatility = log_returns.std()
    
    # Annualize the volatility
    annualized_volatility = daily_volatility * np.sqrt(trading_days_per_year)
    
    print(f"  Historical Volatility: {annualized_volatility*100:.2f}%")
    print(f"  Daily Volatility: {daily_volatility*100:.2f}%")
    print(f"  Data Points Used: {len(log_returns)}")
    
    return annualized_volatility


def get_options_chain(ticker):
    """
    Fetch the complete options chain for a given NSE ticker.
    
    The options chain contains all available call and put contracts for different
    expiration dates and strike prices. This is the raw market data we'll compare
    against our theoretical Black-Scholes prices.
    
    BID-ASK SPREAD IMPLICATIONS:
    - The 'lastPrice' may be closer to bid or ask depending on trade direction
    - True mid-market price is (bid + ask) / 2
    - Wide bid-ask spreads can create apparent mispricings that aren't arbitrageable
    - Transaction costs (bid-ask spread) can eliminate theoretical arbitrage profits
    
    MARKET DATA LIMITATIONS:
    - Options may have low liquidity (wide spreads, stale prices)
    - Some strikes may have no open interest or volume
    - Market prices include dividends, early exercise rights, and other factors
    - Time to expiration needs exact calculation from expiration dates
    
    Parameters:
    -----------
    ticker : str
        NSE ticker symbol (e.g., "RELIANCE.NS", "INFY.NS")
    
    Returns:
    --------
    tuple : (calls_df, puts_df, expiration_dates)
        calls_df : pd.DataFrame
            Call options data
        puts_df : pd.DataFrame
            Put options data
        expiration_dates : list
            Available expiration dates
    """
    try:
        # Create ticker object
        stock = yf.Ticker(ticker)
        
        # Get all expiration dates
        exp_dates = stock.options
        
        if not exp_dates:
            raise ValueError(f"No options data available for {ticker}")
        
        print(f"✓ Found {len(exp_dates)} expiration dates")
        print(f"  Nearest expiration: {exp_dates[0]}")
        
        # Get options chain for the nearest expiration
        opt_chain = stock.option_chain(exp_dates[0])
        
        calls_df = opt_chain.calls
        puts_df = opt_chain.puts
        
        print(f"  Available calls: {len(calls_df)}")
        print(f"  Available puts: {len(puts_df)}")
        
        return calls_df, puts_df, exp_dates
        
    except Exception as e:
        print(f"✗ Error fetching options chain for {ticker}: {str(e)}")
        raise


def calculate_time_to_expiry(expiration_date):
    """
    Calculate time to expiration in years from a given expiration date.
    
    Parameters:
    -----------
    expiration_date : str
        Expiration date in YYYY-MM-DD format
    
    Returns:
    --------
    float : Time to expiration in years
    """
    try:
        exp_date = datetime.strptime(expiration_date, '%Y-%m-%d')
        current_date = datetime.now()
        
        # Calculate time difference in days
        time_diff = exp_date - current_date
        
        # Convert to years (assuming 252 trading days per year)
        time_to_expiry = max(time_diff.days / 365.0, 1/365.0)  # Minimum 1 day
        
        return time_to_expiry
        
    except Exception as e:
        print(f"Error calculating time to expiry: {str(e)}")
        return 30/365.0  # Default to 30 days


def scan_mispricing(ticker, threshold=0.05, risk_free_rate=0.06):
    """
    Scan for mispriced options by comparing Black-Scholes theoretical prices
    to market prices.
    
    ARBITRAGE REALITY CHECK:
    Real arbitrage is much harder than this model suggests because:
    
    1. TRANSACTION COSTS:
    - Bid-ask spreads can be 1-5% or more for illiquid options
    - Brokerage commissions and exchange fees
    - Securities transaction tax (STT) in India
    
    2. EXECUTION RISK:
    - Prices can move between analysis and execution
    - Limited liquidity at quoted prices
    - Partial fills and slippage
    
    3. MODEL LIMITATIONS:
    - Black-Scholes doesn't handle American-style early exercise
    - No dividend adjustments (NSE stocks pay dividends)
    - Constant volatility assumption (volatility surfaces exist)
    
    4. MARKET IMPACT:
    - Large trades move prices against you
    - Market makers adjust quotes when they detect arbitrage
    
    Despite these limitations, this scan can identify:
    - Potential pricing inefficiencies
    - Options that may be over/undervalued
    - Opportunities for further research
    
    Parameters:
    -----------
    ticker : str
        NSE ticker symbol
    threshold : float
        Mispricing threshold (default: 5% = 0.05)
    risk_free_rate : float
        Risk-free rate (default: 6% for Indian government bonds)
    
    Returns:
    --------
    pd.DataFrame : Mispriced options sorted by mispricing magnitude
    """
    print(f"\n{'='*60}")
    print(f"MISPRICING SCAN FOR {ticker}")
    print(f"{'='*60}")
    
    try:
        # Step 1: Get stock data and historical volatility
        current_price, hist_data = get_stock_data(ticker)
        hist_vol = calculate_historical_volatility(hist_data)
        
        # Step 2: Get options chain
        calls_df, puts_df, exp_dates = get_options_chain(ticker)
        
        # Step 3: Calculate time to expiry
        time_to_expiry = calculate_time_to_expiry(exp_dates[0])
        print(f"  Time to Expiry: {time_to_expiry*365:.1f} days")
        
        # Step 4: Calculate theoretical prices and identify mispricings
        mispriced_options = []
        
        # Process calls
        print(f"\nScanning {len(calls_df)} call options...")
        for idx, row in calls_df.iterrows():
            try:
                strike = row['strike']
                market_price = row['lastPrice']
                
                # Skip options with no price or zero price
                if pd.isna(market_price) or market_price <= 0:
                    continue
                
                # Calculate theoretical price using historical volatility
                theoretical_price = call_price(current_price, strike, time_to_expiry, 
                                              risk_free_rate, hist_vol)
                
                # Calculate mispricing percentage
                # Skip options with very low theoretical prices (less than 0.01)
                # as they create misleading percentage mispricings
                if theoretical_price >= 0.01:
                    mispricing_pct = abs(theoretical_price - market_price) / theoretical_price
                    
                    if mispricing_pct > threshold:
                        mispriced_options.append({
                            'type': 'CALL',
                            'strike': strike,
                            'market_price': market_price,
                            'theoretical_price': theoretical_price,
                            'mispricing_pct': mispricing_pct,
                            'mispricing_amount': market_price - theoretical_price,
                            'volume': row.get('volume', 0),
                            'open_interest': row.get('openInterest', 0),
                            'bid': row.get('bid', 0),
                            'ask': row.get('ask', 0),
                            'bid_ask_spread': row.get('ask', 0) - row.get('bid', 0) if pd.notna(row.get('bid')) and pd.notna(row.get('ask')) else 0
                        })
            except Exception as e:
                continue  # Skip problematic calculations
        
        # Process puts
        print(f"Scanning {len(puts_df)} put options...")
        for idx, row in puts_df.iterrows():
            try:
                strike = row['strike']
                market_price = row['lastPrice']
                
                # Skip options with no price or zero price
                if pd.isna(market_price) or market_price <= 0:
                    continue
                
                # Calculate theoretical price using historical volatility
                theoretical_price = put_price(current_price, strike, time_to_expiry, 
                                             risk_free_rate, hist_vol)
                
                # Calculate mispricing percentage
                # Skip options with very low theoretical prices (less than 0.01)
                # as they create misleading percentage mispricings
                if theoretical_price >= 0.01:
                    mispricing_pct = abs(theoretical_price - market_price) / theoretical_price
                    
                    if mispricing_pct > threshold:
                        mispriced_options.append({
                            'type': 'PUT',
                            'strike': strike,
                            'market_price': market_price,
                            'theoretical_price': theoretical_price,
                            'mispricing_pct': mispricing_pct,
                            'mispricing_amount': market_price - theoretical_price,
                            'volume': row.get('volume', 0),
                            'open_interest': row.get('openInterest', 0),
                            'bid': row.get('bid', 0),
                            'ask': row.get('ask', 0),
                            'bid_ask_spread': row.get('ask', 0) - row.get('bid', 0) if pd.notna(row.get('bid')) and pd.notna(row.get('ask')) else 0
                        })
            except Exception as e:
                continue  # Skip problematic calculations
        
        # Create DataFrame and sort by mispricing percentage
        if mispriced_options:
            mispriced_df = pd.DataFrame(mispriced_options)
            mispriced_df = mispriced_df.sort_values('mispricing_pct', ascending=False)
            
            # Add additional analysis columns
            mispriced_df['spread_as_pct_of_price'] = mispriced_df['bid_ask_spread'] / mispriced_df['market_price']
            mispriced_df['theoretical_vs_mid'] = mispriced_df['theoretical_price'] - ((mispriced_df['bid'] + mispriced_df['ask']) / 2)
            
            print(f"\n✓ Found {len(mispriced_df)} potentially mispriced options")
            print(f"  Threshold used: {threshold*100:.1f}%")
            print(f"  Historical volatility used: {hist_vol*100:.2f}%")
            
            return mispriced_df
        else:
            print(f"\n✓ No mispriced options found above {threshold*100:.1f}% threshold")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"✗ Error in mispricing scan: {str(e)}")
        return pd.DataFrame()


def save_mispricing_results(mispriced_df, ticker, threshold):
    """
    Save mispricing scan results to CSV file.
    
    Parameters:
    -----------
    mispriced_df : pd.DataFrame
        Mispriced options data
    ticker : str
        Stock ticker symbol
    threshold : float
        Mispricing threshold used
    """
    if mispriced_df.empty:
        print("No results to save")
        return
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"mispricing_results_{ticker}_{timestamp}.csv"
    
    # Add metadata columns
    mispriced_df['scan_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mispriced_df['ticker'] = ticker
    mispriced_df['threshold_pct'] = threshold * 100
    
    # Save to CSV
    mispriced_df.to_csv(filename, index=False)
    print(f"✓ Results saved to: {filename}")
    
    # Also save a copy with generic name
    mispriced_df.to_csv("mispricing_results.csv", index=False)
    print(f"✓ Results also saved to: mispricing_results.csv")


def format_mispricing_table(mispriced_df, top_n=10):
    """
    Format mispricing results into a readable table.
    
    Parameters:
    -----------
    mispriced_df : pd.DataFrame
        Mispriced options data
    top_n : int
        Number of top results to display
    
    Returns:
    --------
    str : Formatted table string
    """
    if mispriced_df.empty:
        return "No mispriced options found."
    
    # Get top N results
    top_df = mispriced_df.head(top_n).copy()
    
    # Format columns for display
    display_df = top_df[['type', 'strike', 'market_price', 'theoretical_price', 
                        'mispricing_pct', 'mispricing_amount', 'bid_ask_spread', 
                        'volume', 'open_interest']].copy()
    
    # Format numeric columns
    display_df['market_price'] = display_df['market_price'].apply(lambda x: f"₹{x:.2f}")
    display_df['theoretical_price'] = display_df['theoretical_price'].apply(lambda x: f"₹{x:.2f}")
    display_df['mispricing_pct'] = display_df['mispricing_pct'].apply(lambda x: f"{x*100:.2f}%")
    display_df['mispricing_amount'] = display_df['mispricing_amount'].apply(lambda x: f"₹{x:.2f}")
    display_df['bid_ask_spread'] = display_df['bid_ask_spread'].apply(lambda x: f"₹{x:.2f}")
    
    # Rename columns for better display
    display_df.columns = ['Type', 'Strike', 'Market', 'Theoretical', 'Mispricing %', 
                          'Mispricing ₹', 'Bid-Ask Spread', 'Volume', 'Open Interest']
    
    return display_df.to_string(index=False)


if __name__ == "__main__":
    # Example usage
    ticker = "RELIANCE.NS"
    threshold = 0.05  # 5%
    
    # Run mispricing scan
    results = scan_mispricing(ticker, threshold)
    
    if not results.empty:
        print(f"\nTop 10 Mispriced Options:")
        print(format_mispricing_table(results, 10))
        
        # Save results
        save_mispricing_results(results, ticker, threshold)
    else:
        print("No mispriced options found.")
