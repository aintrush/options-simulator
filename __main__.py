"""
Options Pricing & Greeks Simulator - Main Entry Point

This module allows the entire project to be run as a Python module using:
    py -m options_simulator

It provides a menu interface to access all three main components:
1. Interactive Black-Scholes Calculator
2. Greeks Visualization Suite
3. Live Mispricing Scanner
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main_menu():
    """Display the main menu and handle user selection."""
    
    print("="*80)
    print("OPTIONS PRICING & GREEKS SIMULATOR")
    print("="*80)
    print("\nA comprehensive options analysis toolkit with:")
    print("• Black-Scholes pricing engine with Greeks calculation")
    print("• Advanced visualization suite for risk analysis")
    print("• Real-time mispricing scanner with market data")
    print("\nSelect a module to run:")
    
    while True:
        print("\n" + "-"*50)
        print("1. Black-Scholes Calculator (Interactive)")
        print("2. Greeks Visualization Suite")
        print("3. Live Mispricing Scanner")
        print("4. Run Example Calculations")
        print("5. Exit")
        print("-"*50)
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            run_black_scholes_calculator()
        elif choice == '2':
            run_visualization_suite()
        elif choice == '3':
            run_mispricing_scanner()
        elif choice == '4':
            run_examples()
        elif choice == '5':
            print("\nThank you for using the Options Pricing & Greeks Simulator!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

def run_black_scholes_calculator():
    """Run the interactive Black-Scholes calculator."""
    try:
        print("\n" + "="*60)
        print("BLACK-SCHOLES OPTIONS CALCULATOR")
        print("="*60)
        
        from main import main as bs_main
        bs_main()
        
    except ImportError as e:
        print(f"Error importing Black-Scholes calculator: {e}")
        print("Please ensure main.py exists in the project root.")
    except Exception as e:
        print(f"Error running Black-Scholes calculator: {e}")

def run_visualization_suite():
    """Run the Greeks visualization suite."""
    try:
        print("\n" + "="*60)
        print("GREEKS VISUALIZATION SUITE")
        print("="*60)
        print("\nThis will create interactive charts showing:")
        print("• Delta vs Stock Price for multiple expiries")
        print("• 3D option price surfaces")
        print("• All Greeks across volatility levels")
        print("• Strategy payoff diagrams")
        
        response = input("\nProceed with visualization suite? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            from visualization.greeks_plot import create_all_visualizations
            create_all_visualizations()
            print("\n✓ All visualizations created successfully!")
            print("  Check the current directory for PNG files.")
        else:
            print("Visualization cancelled.")
            
    except ImportError as e:
        print(f"Error importing visualization suite: {e}")
        print("Please ensure visualization/greeks_plot.py exists.")
    except Exception as e:
        print(f"Error running visualization suite: {e}")

def run_mispricing_scanner():
    """Run the live mispricing scanner."""
    try:
        print("\n" + "="*60)
        print("LIVE MISPRICING SCANNER")
        print("="*60)
        print("\nThis scanner compares Black-Scholes theoretical prices")
        print("to actual market prices to identify potential inefficiencies.")
        
        from data.run_scan import main as scanner_main
        scanner_main()
        
    except ImportError as e:
        print(f"Error importing mispricing scanner: {e}")
        print("Please ensure data/run_scan.py exists.")
    except Exception as e:
        print(f"Error running mispricing scanner: {e}")

def run_examples():
    """Run example calculations and demonstrations."""
    try:
        print("\n" + "="*60)
        print("EXAMPLE CALCULATIONS")
        print("="*60)
        
        # Black-Scholes example
        print("\n1. Black-Scholes Example:")
        print("-" * 30)
        from test_example import test_example
        test_example()
        
        # Visualization examples
        print("\n2. Creating sample visualizations...")
        from visualization.greeks_plot import plot_delta_vs_stock_price, plot_greeks_comparison
        import matplotlib.pyplot as plt
        
        # Create sample charts
        fig1 = plot_delta_vs_stock_price()
        plt.savefig('sample_delta_chart.png', dpi=150)
        plt.close(fig1)
        
        fig2 = plot_greeks_comparison()
        plt.savefig('sample_greeks_chart.png', dpi=150)
        plt.close(fig2)
        
        print("✓ Sample charts saved as:")
        print("  - sample_delta_chart.png")
        print("  - sample_greeks_chart.png")
        
        print("\n✓ All examples completed successfully!")
        
    except ImportError as e:
        print(f"Error running examples: {e}")
    except Exception as e:
        print(f"Error in examples: {e}")

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'numpy', 'scipy', 'pandas', 'matplotlib', 'yfinance'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  • {package}")
        print("\nInstall them with: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main entry point for the module."""
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies before running the simulator.")
        return
    
    # Display welcome message
    print("\nWelcome to the Options Pricing & Greeks Simulator!")
    print("This is a comprehensive toolkit for options analysis and trading research.")
    
    # Run main menu
    main_menu()

if __name__ == "__main__":
    main()
