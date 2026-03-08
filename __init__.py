"""
Options Pricing & Greeks Simulator

A comprehensive Python-based options analysis toolkit that combines theoretical 
Black-Scholes pricing with real-world market data validation.

This package provides:
- Black-Scholes pricing engine with complete Greeks calculation
- Advanced visualization suite for options analysis
- Live mispricing scanner with market data integration
- Professional tools for quantitative finance research

Author: Computer Engineering Portfolio Project
License: Educational and Research Use Only
"""

__version__ = "1.0.0"
__title__ = "Options Pricing & Greeks Simulator"
__description__ = "Comprehensive options analysis toolkit with Black-Scholes pricing, Greeks visualization, and real-time mispricing scanning"

# Import key functions for easy access
from .models.black_scholes import (
    call_price, put_price, call_delta, put_delta, gamma,
    call_theta, put_theta, vega, call_rho, put_rho,
    calculate_all_greeks, check_put_call_parity
)

__all__ = [
    'call_price', 'put_price', 'call_delta', 'put_delta', 'gamma',
    'call_theta', 'put_theta', 'vega', 'call_rho', 'put_rho',
    'calculate_all_greeks', 'check_put_call_parity'
]
