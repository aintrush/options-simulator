"""
Black-Scholes Options Pricing - My Final Year Project

This is my implementation of the Black-Scholes model for pricing options.
I learned about this in my computational finance class and wanted to 
build it from scratch to really understand how it works.

The model calculates option prices using some cool math with normal 
distributions and stuff. It also gives us the "Greeks" which tell us how
sensitive the option price is to different things like stock price,
time, volatility, etc.

Note: This is for educational purposes only - don't actually use this
for real trading without understanding the risks!
"""

import numpy as np
from scipy.stats import norm


def calculate_d1_d2(S, K, T, r, sigma):
    """
    Calculate the d1 and d2 parameters that we need for Black-Scholes.
    
    These parameters are kind of like the "z-scores" of the option - they tell
    us how far the stock price is from the strike price, adjusted for time
    and volatility. My professor said these are the most important parts
    of the formula.
    
    Parameters:
    -----------
    S : float
        Current stock price (what the stock is trading at right now)
    K : float
        Strike price (the price you can buy/sell the stock at)
    T : float
        Time until expiration in years (I convert days to years)
    r : float
        Risk-free interest rate (like government bond rates)
    sigma : float
        Volatility (how much the stock price bounces around)
    
    Returns:
    --------
    tuple : (d1, d2)
        d1 : float
            This is like the "probability-adjusted" distance. It's also
            the Delta of the option which is pretty cool!
            Formula: d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
        d2 : float
            This tells us the probability the option will be worth something
            at expiration. It's just d1 minus the volatility term.
    """
    # Making sure the inputs make sense - no negative prices or time!
    if S <= 0:
        raise ValueError("Stock price (S) must be positive")
    if K <= 0:
        raise ValueError("Strike price (K) must be positive")
    if T < 0:
        raise ValueError("Time to expiration (T) cannot be negative")
    if r < 0:
        raise ValueError("Risk-free rate (r) cannot be negative")
    if sigma <= 0:
        raise ValueError("Volatility (sigma) must be positive")
    
    # If there's no time left, the option is basically at expiration
    if T <= 0:
        return 0, 0
    
    # Sometimes the math can get weird with extreme values, so I'm being careful
    try:
        # Calculate d1 - this is the main part of the formula
        numerator = np.log(S / K) + (r + 0.5 * sigma ** 2) * T
        denominator = sigma * np.sqrt(T)
        
        # Don't want to divide by a super tiny number
        if abs(denominator) < 1e-10:
            d1 = np.sign(numerator) * 10  # Just give it a big value
        else:
            d1 = numerator / denominator
        
        # Keep d1 reasonable so we don't get overflow errors
        d1 = np.clip(d1, -10, 10)
        
        # d2 is just d1 minus the volatility term
        d2 = d1 - sigma * np.sqrt(T)
        d2 = np.clip(d2, -10, 10)
        
        return d1, d2
        
    except (OverflowError, UnderflowError):
        # If something goes wrong with the math, handle extreme cases
        if S > K * 1.5:  # Deep in-the-money call
            return 10, 10
        elif S < K * 0.5:  # Deep out-of-the-money call
            return -10, -10
        else:
            return 0, 0


def call_price(S, K, T, r, sigma):
    """
    Calculate the price of a call option using Black-Scholes.
    
    A call option is like a coupon that lets you buy a stock at a fixed price
    (the strike price) by a certain date. If the stock price goes up above
    the strike, you can buy it cheap and make money!
    
    Parameters:
    -----------
    S, K, T, r, sigma : float
        Same stuff as before - stock price, strike, time, interest rate, volatility
    
    Returns:
    --------
    float : Call option price
    
    Formula:
    C = S·N(d1) - K·e^(-rT)·N(d2)
    
    Where:
    - N(d1) is the probability-adjusted forward price (also equals Delta!)
    - N(d2) is the risk-neutral probability of the option being worth something
    - e^(-rT) discounts the strike price to today's money
    """
    if T <= 0:
        # At expiration, the call is worth the difference between stock and strike
        return max(S - K, 0)
    
    d1, d2 = calculate_d1_d2(S, K, T, r, sigma)
    call = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call


def put_price(S, K, T, r, sigma):
    """
    Calculate the price of a put option using Black-Scholes.
    
    A put option is like insurance for your stock - it lets you sell the stock
    at a fixed price even if the stock price crashes. Useful if you're worried
    about the market going down!
    
    Parameters:
    -----------
    S, K, T, r, sigma : float
        Same parameters as always
    
    Returns:
    --------
    float : Put option price
    
    Formula:
    P = K·e^(-rT)·N(-d2) - S·N(-d1)
    
    Where:
    - N(-d1) is the put's Delta (it's negative)
    - N(-d2) is the probability the put will be worth something at expiration
    """
    if T <= 0:
        # At expiration, the put is worth the difference between strike and stock
        return max(K - S, 0)
    
    d1, d2 = calculate_d1_d2(S, K, T, r, sigma)
    put = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put


def call_delta(S, K, T, r, sigma):
    """
    Calculate Delta for a European call option.
    
    Delta measures the rate of change of the option price with respect to changes
    in the underlying stock price. It represents how much the option price changes
    for a $1 change in the stock price.
    
    For calls: Delta ∈ [0, 1]
    - Delta = 0: Deep out-of-the-money (unlikely to expire ITM)
    - Delta = 0.5: At-the-money
    - Delta = 1: Deep in-the-money (certain to expire ITM)
    
    Parameters:
    -----------
    S, K, T, r, sigma : float
        Same as defined in calculate_d1_d2()
    
    Returns:
    --------
    float : Call Delta
    
    Formula: Δ_call = N(d1)
    
    Why N(d1) = Delta:
    N(d1) represents the risk-neutral probability that the option will be exercised,
    adjusted for the expected growth of the underlying. It's the sensitivity of the
    option price to changes in the underlying price.
    """
    if T <= 0:
        # At expiration, Delta is 1 if S > K, 0 if S < K
        return 1.0 if S > K else 0.0
    
    d1, _ = calculate_d1_d2(S, K, T, r, sigma)
    return norm.cdf(d1)


def put_delta(S, K, T, r, sigma):
    """
    Calculate Delta for a European put option.
    
    For puts: Delta ∈ [-1, 0]
    - Delta = 0: Deep out-of-the-money
    - Delta = -0.5: At-the-money
    - Delta = -1: Deep in-the-money
    
    Parameters:
    -----------
    S, K, T, r, sigma : float
        Same as defined in calculate_d1_d2()
    
    Returns:
    --------
    float : Put Delta
    
    Formula: Δ_put = N(d1) - 1 = -N(-d1)
    """
    if T <= 0:
        # At expiration, Delta is -1 if S < K, 0 if S > K
        return -1.0 if S < K else 0.0
    
    d1, _ = calculate_d1_d2(S, K, T, r, sigma)
    return norm.cdf(d1) - 1


def gamma(S, K, T, r, sigma):
    """
    Calculate Gamma for European options (same for calls and puts).
    
    Gamma measures the rate of change of Delta with respect to changes in the
    underlying stock price. It represents the curvature of the option price
    and is highest for at-the-money options with short time to expiration.
    
    High Gamma means Delta changes rapidly as the stock price changes,
    making the option more sensitive to stock price movements.
    
    Parameters:
    -----------
    S, K, T, r, sigma : float
        Same as defined in calculate_d1_d2()
    
    Returns:
    --------
    float : Gamma
    
    Formula: Γ = φ(d1) / (S·σ·√T)
    
    Where φ(d1) is the standard normal probability density function at d1.
    """
    if T <= 0:
        return 0.0
    
    d1, _ = calculate_d1_d2(S, K, T, r, sigma)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    return gamma


def call_theta(S, K, T, r, sigma):
    """
    Calculate Theta for a European call option.
    
    Theta measures the rate of change of the option price with respect to time.
    It represents time decay - how much value the option loses each day as it
    approaches expiration (all else equal).
    
    Theta is usually negative for long option positions (you lose money as time passes).
    
    Parameters:
    -----------
    S, K, T, r, sigma : float
        Same as defined in calculate_d1_d2()
    
    Returns:
    --------
    float : Call Theta (per year, divide by 365 for daily theta)
    
    Formula: Θ_call = -[S·φ(d1)·σ/(2√T)] - r·K·e^(-rT)·N(d2) + r·S·N(d1)
    """
    if T <= 0:
        return 0.0
    
    d1, d2 = calculate_d1_d2(S, K, T, r, sigma)
    theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) 
             - r * K * np.exp(-r * T) * norm.cdf(d2) 
             + r * S * norm.cdf(d1))
    return theta


def put_theta(S, K, T, r, sigma):
    """
    Calculate Theta for a European put option.
    
    Parameters:
    -----------
    S, K, T, r, sigma : float
        Same as defined in calculate_d1_d2()
    
    Returns:
    --------
    float : Put Theta (per year, divide by 365 for daily theta)
    
    Formula: Θ_put = -[S·φ(d1)·σ/(2√T)] + r·K·e^(-rT)·N(-d2) - r·S·N(-d1)
    """
    if T <= 0:
        return 0.0
    
    d1, d2 = calculate_d1_d2(S, K, T, r, sigma)
    theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) 
             + r * K * np.exp(-r * T) * norm.cdf(-d2) 
             - r * S * norm.cdf(-d1))
    return theta


def vega(S, K, T, r, sigma):
    """
    Calculate Vega for European options (same for calls and puts).
    
    Vega measures the sensitivity of the option price to changes in volatility.
    It represents how much the option price changes for a 1% change in volatility.
    
    Vega is highest for at-the-money options with longer time to expiration.
    All options have positive vega - they gain value as volatility increases.
    
    Parameters:
    -----------
    S, K, T, r, sigma : float
        Same as defined in calculate_d1_d2()
    
    Returns:
    --------
    float : Vega (change in option price for 1.0 change in volatility)
    
    Formula: V = S·φ(d1)·√T
    
    Note: To get vega for 1% change, divide by 100.
    """
    if T <= 0:
        return 0.0
    
    d1, _ = calculate_d1_d2(S, K, T, r, sigma)
    vega = S * norm.pdf(d1) * np.sqrt(T)
    return vega


def call_rho(S, K, T, r, sigma):
    """
    Calculate Rho for a European call option.
    
    Rho measures the sensitivity of the option price to changes in the
    risk-free interest rate. It represents how much the option price changes
    for a 1% change in interest rates.
    
    Call options have positive rho (benefit from higher rates)
    Put options have negative rho (hurt by higher rates)
    
    Parameters:
    -----------
    S, K, T, r, sigma : float
        Same as defined in calculate_d1_d2()
    
    Returns:
    --------
    float : Call Rho (change in option price for 1.0 change in interest rate)
    
    Formula: ρ_call = K·T·e^(-rT)·N(d2)
    
    Note: To get rho for 1% change, divide by 100.
    """
    if T <= 0:
        return 0.0
    
    _, d2 = calculate_d1_d2(S, K, T, r, sigma)
    rho = K * T * np.exp(-r * T) * norm.cdf(d2)
    return rho


def put_rho(S, K, T, r, sigma):
    """
    Calculate Rho for a European put option.
    
    Parameters:
    -----------
    S, K, T, r, sigma : float
        Same as defined in calculate_d1_d2()
    
    Returns:
    --------
    float : Put Rho (change in option price for 1.0 change in interest rate)
    
    Formula: ρ_put = -K·T·e^(-rT)·N(-d2)
    """
    if T <= 0:
        return 0.0
    
    _, d2 = calculate_d1_d2(S, K, T, r, sigma)
    rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
    return rho


def calculate_all_greeks(S, K, T, r, sigma):
    """
    Calculate all option prices and Greeks in a single function.
    
    Parameters:
    -----------
    S, K, T, r, sigma : float
        Same as defined in calculate_d1_d2()
    
    Returns:
    --------
    dict : Dictionary containing all calculated values
    """
    results = {
        'call_price': call_price(S, K, T, r, sigma),
        'put_price': put_price(S, K, T, r, sigma),
        'call_delta': call_delta(S, K, T, r, sigma),
        'put_delta': put_delta(S, K, T, r, sigma),
        'gamma': gamma(S, K, T, r, sigma),
        'call_theta': call_theta(S, K, T, r, sigma),
        'put_theta': put_theta(S, K, T, r, sigma),
        'vega': vega(S, K, T, r, sigma),
        'call_rho': call_rho(S, K, T, r, sigma),
        'put_rho': put_rho(S, K, T, r, sigma)
    }
    return results


def check_put_call_parity(S, K, T, r, sigma):
    """
    Verify put-call parity relationship.
    
    Put-call parity is a fundamental relationship that must hold for European options:
    C - P = S - K·e^(-rT)
    
    This ensures no arbitrage opportunities exist between calls, puts, and the underlying.
    
    Parameters:
    -----------
    S, K, T, r, sigma : float
        Same as defined in calculate_d1_d2()
    
    Returns:
    --------
    tuple : (parity_holds, difference, tolerance)
        parity_holds : bool
            True if parity holds within tolerance
        difference : float
            The actual difference: (C - P) - (S - K·e^(-rT))
        tolerance : float
            Acceptable tolerance (0.01)
    """
    call = call_price(S, K, T, r, sigma)
    put = put_price(S, K, T, r, sigma)
    
    left_side = call - put
    right_side = S - K * np.exp(-r * T)
    difference = left_side - right_side
    tolerance = 0.01  # Allow small numerical errors
    
    parity_holds = abs(difference) <= tolerance
    return parity_holds, difference, tolerance
