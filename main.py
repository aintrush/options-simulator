"""
Options Pricing & Greeks Simulator - Main Entry Point

This is the main entry point for the Options Pricing & Greeks Simulator.
It provides an interactive command-line interface for calculating option prices
and Greeks using the Black-Scholes model.
"""

import sys
import os

# Add the project root to the Python path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.black_scholes import calculate_all_greeks, check_put_call_parity
from utils.inputs import get_user_inputs, validate_inputs, confirm_inputs, get_yes_no_input


def format_results_table(results, inputs):
    """
    Format the results into a clean, readable table.
    
    Parameters:
    -----------
    results : dict
        Dictionary containing all calculated values
    inputs : dict
        Dictionary containing input parameters
    
    Returns:
    --------
    str : Formatted table string
    """
    table = []
    table.append("\n" + "="*80)
    table.append("OPTIONS PRICING & GREEKS RESULTS")
    table.append("="*80)
    
    # Input parameters section
    table.append("\nINPUT PARAMETERS:")
    table.append("-" * 40)
    table.append(f"Stock Price (S):           ${inputs['S']:.2f}")
    table.append(f"Strike Price (K):          ${inputs['K']:.2f}")
    table.append(f"Time to Expiry:            {inputs['T']*365:.0f} days ({inputs['T']:.3f} years)")
    table.append(f"Risk-Free Rate:            {inputs['r']*100:.2f}%")
    table.append(f"Implied Volatility:        {inputs['sigma']*100:.2f}%")
    
    # Option prices section
    table.append("\nOPTION PRICES:")
    table.append("-" * 40)
    table.append(f"Call Price:                ${results['call_price']:.4f}")
    table.append(f"Put Price:                 ${results['put_price']:.4f}")
    
    # Greeks section
    table.append("\nGREEKS:")
    table.append("-" * 40)
    table.append(f"{'Greek':<12} {'Call':<15} {'Put':<15} {'Description'}")
    table.append("-" * 70)
    
    # Delta
    table.append(f"{'Delta':<12} {results['call_delta']:<15.4f} {results['put_delta']:<15.4f} Price sensitivity to stock")
    
    # Gamma (same for both)
    table.append(f"{'Gamma':<12} {results['gamma']:<15.4f} {results['gamma']:<15.4f} Delta sensitivity to stock")
    
    # Theta (per day)
    call_theta_daily = results['call_theta'] / 365
    put_theta_daily = results['put_theta'] / 365
    table.append(f"{'Theta':<12} {call_theta_daily:<15.4f} {put_theta_daily:<15.4f} Time decay per day")
    
    # Vega (per 1% change)
    vega_per_percent = results['vega'] / 100
    table.append(f"{'Vega':<12} {vega_per_percent:<15.4f} {vega_per_percent:<15.4f} Volatility sensitivity (1%)")
    
    # Rho (per 1% change)
    call_rho_per_percent = results['call_rho'] / 100
    put_rho_per_percent = results['put_rho'] / 100
    table.append(f"{'Rho':<12} {call_rho_per_percent:<15.4f} {put_rho_per_percent:<15.4f} Interest rate sensitivity (1%)")
    
    return "\n".join(table)


def display_put_call_parity_check(inputs):
    """
    Display the put-call parity verification results.
    
    Parameters:
    -----------
    inputs : dict
        Dictionary containing input parameters
    """
    parity_holds, difference, tolerance = check_put_call_parity(
        inputs['S'], inputs['K'], inputs['T'], inputs['r'], inputs['sigma']
    )
    
    print("\n" + "="*50)
    print("PUT-CALL PARITY VERIFICATION")
    print("="*50)
    print("Put-Call Parity: C - P = S - K·e^(-rT)")
    print("-" * 50)
    
    if parity_holds:
        print("✓ PUT-CALL PARITY HOLDS")
        print(f"  Difference: {difference:.6f} (within tolerance: {tolerance})")
    else:
        print("✗ PUT-CALL PARITY VIOLATION DETECTED")
        print(f"  Difference: {difference:.6f} (tolerance: {tolerance})")
        print("  This may indicate a calculation error or arbitrage opportunity")
    
    # Show the actual values
    call_price = calculate_all_greeks(inputs['S'], inputs['K'], inputs['T'], inputs['r'], inputs['sigma'])['call_price']
    put_price = calculate_all_greeks(inputs['S'], inputs['K'], inputs['T'], inputs['r'], inputs['sigma'])['put_price']
    
    print(f"\nVerification:")
    print(f"  C - P = ${call_price:.4f} - ${put_price:.4f} = ${call_price - put_price:.4f}")
    print(f"  S - K·e^(-rT) = ${inputs['S']:.4f} - ${inputs['K']:.4f}·e^(-{inputs['r']:.4f}·{inputs['T']:.4f}) = ${inputs['S'] - inputs['K'] * (2.718281828 ** (-inputs['r'] * inputs['T'])):.4f}")


def display_interpretation_guide():
    """
    Display a practical interpretation guide for the Greeks.
    """
    print("\n" + "="*70)
    print("PRACTICAL INTERPRETATION GUIDE")
    print("="*70)
    print("""
WHAT EACH GREEK TELLS A TRADER:

📈 DELTA (Δ):
• Call: For every $1 increase in stock price, option price changes by Delta dollars
• Put: For every $1 increase in stock price, option price changes by Delta dollars (negative)
• Example: Delta = 0.60 means call option gains $0.60 when stock rises $1
• Use for: Hedging stock exposure, probability of finishing ITM

📊 GAMMA (Γ):
• Rate of change of Delta - how fast Delta changes as stock moves
• High Gamma = Delta changes rapidly (more risk/reward)
• Highest for ATM options with short expiration
• Use for: Managing Delta hedging, understanding acceleration risk

⏰ THETA (Θ):
• Time decay - how much value option loses each day (shown as daily)
• Always negative for long options (you lose money as time passes)
• Highest decay for ATM options near expiration
• Use for: Understanding holding costs, timing strategies

📊 VEGA (ν):
• Sensitivity to volatility changes (shown per 1% change in vol)
• All options have positive Vega - they gain when volatility rises
• Highest for ATM options with long expiration
• Use for: Volatility trading, event-driven strategies

🏦 RHO (ρ):
• Sensitivity to interest rate changes (shown per 1% change in rates)
• Calls: Positive Rho (benefit from higher rates)
• Puts: Negative Rho (hurt by higher rates)
• Most important for long-term options
• Use for: Interest rate exposure management

💡 KEY INSIGHTS:
• Delta ≈ Probability of finishing ITM (for calls)
• Gamma is the "speedometer" for your Delta position
• Theta is the "rent" you pay for holding options
• Vega is your bet on future volatility
• Rho matters most for LEAPs and rate-sensitive strategies
""")


def main():
    """
    The main function that runs my interactive options calculator.
    
    This is where everything starts - it prompts the user for inputs,
    calculates the option prices and Greeks, and displays everything
    in a nice formatted way.
    """
    print("Welcome to my Options Pricing & Greeks Calculator!")
    print("This is a project I built for my Computer Engineering portfolio.")
    print("It calculates option prices using the Black-Scholes model.\n")
    
    while True:
        try:
            # Get all the user inputs with validation
            inputs = get_user_inputs()
            
            # Check if the inputs look reasonable
            is_valid, warnings = validate_inputs(inputs)
            if warnings:
                print("\n⚠️  Just a heads up:")
                for warning in warnings:
                    print(f"  • {warning}")
            
            # Let the user confirm their inputs
            if not confirm_inputs(inputs):
                print("\nNo worries, let's try again...\n")
                continue
            
            # Calculate all the prices and Greeks
            results = calculate_all_greeks(
                inputs['S'], inputs['K'], inputs['T'], inputs['r'], inputs['sigma']
            )
            
            # Display the results in a nice table
            print(format_results_table(results, inputs))
            
            # Check if put-call parity holds (this is a good way to verify my math)
            display_put_call_parity_check(inputs)
            
            # Show what the Greeks actually mean in practice
            display_interpretation_guide()
            
            # Ask if they want to run another calculation
            print("\n" + "="*50)
            if not get_yes_no_input("Want to try another calculation? (y/n): "):
                print("\nThanks for trying out my Options Calculator!")
                break
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nProgram stopped by user. See you later!")
            break
        except Exception as e:
            print(f"\nOops, something went wrong: {str(e)}")
            print("Please try again or let me know if this keeps happening.")
            if not get_yes_no_input("Want to try again? (y/n): "):
                break


if __name__ == "__main__":
    main()
