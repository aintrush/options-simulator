"""
Input validation utilities for the Options Pricing & Greeks Simulator.

This module provides functions to validate and sanitize user inputs for
the Black-Scholes model parameters.
"""

import sys


def get_positive_float(prompt, field_name):
    """
    Get a positive float value from user input with validation.
    
    Parameters:
    -----------
    prompt : str
        The prompt message to display to the user
    field_name : str
        Name of the field for error messages
    
    Returns:
    --------
    float : Validated positive float value
    """
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print(f"Error: {field_name} must be positive. Please try again.")
                continue
            return value
        except ValueError:
            print(f"Error: Please enter a valid number for {field_name}.")


def get_non_negative_float(prompt, field_name):
    """
    Get a non-negative float value from user input with validation.
    
    Parameters:
    -----------
    prompt : str
        The prompt message to display to the user
    field_name : str
        Name of the field for error messages
    
    Returns:
    --------
    float : Validated non-negative float value
    """
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print(f"Error: {field_name} cannot be negative. Please try again.")
                continue
            return value
        except ValueError:
            print(f"Error: Please enter a valid number for {field_name}.")


def get_percentage_input(prompt, field_name):
    """
    Get a percentage value from user input and convert to decimal.
    
    Parameters:
    -----------
    prompt : str
        The prompt message to display to the user
    field_name : str
        Name of the field for error messages
    
    Returns:
    --------
    float : Percentage converted to decimal (e.g., 5% -> 0.05)
    """
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print(f"Error: {field_name} cannot be negative. Please try again.")
                continue
            return value / 100.0  # Convert percentage to decimal
        except ValueError:
            print(f"Error: Please enter a valid number for {field_name}.")


def get_user_inputs():
    """
    Get all required inputs from the user for the Black-Scholes model.
    
    Returns:
    --------
    dict : Dictionary containing all validated inputs
    """
    print("\n" + "="*60)
    print("OPTIONS PRICING & GREEKS SIMULATOR")
    print("="*60)
    print("\nEnter the following parameters:\n")
    
    inputs = {}
    
    # Current Stock Price (S)
    inputs['S'] = get_positive_float(
        "Current Stock Price (S): $",
        "Stock Price"
    )
    
    # Strike Price (K)
    inputs['K'] = get_positive_float(
        "Strike Price (K): $",
        "Strike Price"
    )
    
    # Time to Expiry in days, convert to years
    days = get_positive_float(
        "Time to Expiry (in days): ",
        "Time to Expiry"
    )
    inputs['T'] = days / 365.0  # Convert days to years
    
    # Risk-Free Rate (as percentage, convert to decimal)
    inputs['r'] = get_percentage_input(
        "Risk-Free Rate (as %, e.g., 5 for 5%): ",
        "Risk-Free Rate"
    )
    
    # Implied Volatility (as percentage, convert to decimal)
    inputs['sigma'] = get_percentage_input(
        "Implied Volatility (as %, e.g., 20 for 20%): ",
        "Implied Volatility"
    )
    
    return inputs


def validate_inputs(inputs):
    """
    Validate that all inputs are within reasonable ranges.
    
    Parameters:
    -----------
    inputs : dict
        Dictionary containing input parameters
    
    Returns:
    --------
    tuple : (is_valid, error_messages)
        is_valid : bool
            True if all inputs are valid
        error_messages : list
            List of error messages for invalid inputs
    """
    error_messages = []
    is_valid = True
    
    # Validate stock price
    if inputs['S'] <= 0:
        error_messages.append("Stock price must be positive")
        is_valid = False
    elif inputs['S'] > 100000:
        error_messages.append("Warning: Stock price seems unusually high (> $100,000)")
    
    # Validate strike price
    if inputs['K'] <= 0:
        error_messages.append("Strike price must be positive")
        is_valid = False
    elif inputs['K'] > 100000:
        error_messages.append("Warning: Strike price seems unusually high (> $100,000)")
    
    # Validate time to expiry
    if inputs['T'] <= 0:
        error_messages.append("Time to expiry must be positive")
        is_valid = False
    elif inputs['T'] > 10:
        error_messages.append("Warning: Time to expiration seems unusually long (> 10 years)")
    
    # Validate risk-free rate
    if inputs['r'] < 0:
        error_messages.append("Risk-free rate cannot be negative")
        is_valid = False
    elif inputs['r'] > 0.5:
        error_messages.append("Warning: Risk-free rate seems unusually high (> 50%)")
    
    # Validate volatility
    if inputs['sigma'] <= 0:
        error_messages.append("Volatility must be positive")
        is_valid = False
    elif inputs['sigma'] > 5:
        error_messages.append("Warning: Volatility seems extremely high (> 500%)")
    elif inputs['sigma'] < 0.01:
        error_messages.append("Warning: Volatility seems very low (< 1%)")
    
    # Check for extreme moneyness
    if inputs['S'] > 0 and inputs['K'] > 0:
        moneyness = inputs['S'] / inputs['K']
        if moneyness < 0.1:
            error_messages.append("Note: Option is deep out-of-the-money (S/K < 0.1)")
        elif moneyness > 10:
            error_messages.append("Note: Option is deep in-the-money (S/K > 10)")
    
    return is_valid, error_messages


def confirm_inputs(inputs):
    """
    Display the inputs back to the user for confirmation.
    
    Parameters:
    -----------
    inputs : dict
        Dictionary containing input parameters
    
    Returns:
    --------
    bool : True if user confirms, False if user wants to re-enter
    """
    print("\n" + "-"*40)
    print("INPUT SUMMARY:")
    print("-"*40)
    print(f"Stock Price (S): ${inputs['S']:.2f}")
    print(f"Strike Price (K): ${inputs['K']:.2f}")
    print(f"Time to Expiry: {inputs['T']*365:.0f} days ({inputs['T']:.3f} years)")
    print(f"Risk-Free Rate: {inputs['r']*100:.2f}%")
    print(f"Implied Volatility: {inputs['sigma']*100:.2f}%")
    print("-"*40)
    
    while True:
        response = input("\nAre these inputs correct? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def get_yes_no_input(prompt):
    """
    Get a yes/no response from the user.
    
    Parameters:
    -----------
    prompt : str
        The prompt message to display to the user
    
    Returns:
    --------
    bool : True for yes, False for no
    """
    while True:
        response = input(prompt).lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")
