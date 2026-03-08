# Interview Questions & Answers - Options Pricing & Greeks Simulator

This document contains 15 key interview questions about your options simulator project, covering mathematical foundations, practical applications, and real-world considerations.

---

## **Mathematical Foundation Questions**

### **1. Explain the Black-Scholes formula and what d1 and d2 represent mathematically.**

**Ideal Answer:** The Black-Scholes formula prices European options as `C = S·N(d1) - K·e^(-rT)·N(d2)` for calls. Mathematically, d1 represents the risk-adjusted growth rate of the underlying, while d2 represents the probability of the option finishing in-the-money under risk-neutral valuation. d1 incorporates both drift and volatility, while d2 adjusts d1 for volatility's impact, making it the true probability measure for option exercise.

---

### **2. Why does N(d1) equal Delta in the Black-Scholes model?**

**Ideal Answer:** N(d1) equals Delta because it represents the sensitivity of the option price to changes in the underlying asset price. Mathematically, this emerges from differentiating the Black-Scholes formula with respect to S, where the derivative of the normal CDF terms cancels out, leaving N(d1). This elegant result shows Delta is both a hedge ratio and the risk-neutral probability of option exercise.

---

### **3. How does put-call parity work and why is it important for arbitrage?**

**Ideal Answer:** Put-call parity states `C - P = S - K·e^(-rT)`, ensuring no arbitrage between calls, puts, and the underlying. It's crucial because any deviation creates risk-free arbitrage opportunities. In practice, this relationship validates model accuracy and helps identify pricing inefficiencies, though transaction costs and market frictions can create temporary violations.

---

## **Greeks & Practical Trading Questions**

### **4. What does Gamma tell a trader and why is it highest for ATM options?**

**Ideal Answer:** Gamma measures the rate of change of Delta, essentially the "acceleration" of option price sensitivity. It's highest for ATM options because Delta transitions most rapidly around the strike price - moving from near 0 to near 1 for calls as the underlying becomes in-the-money. Traders monitor Gamma to manage Delta hedging frequency and understand position risk during large price movements.

---

### **5. How would you use Theta to manage an options portfolio?**

**Ideal Answer:** Theta represents time decay, so I'd use it to manage holding costs and position timing. For long options, I'd minimize exposure to high-Theta ATM options near expiration, potentially using calendar spreads to harvest Theta. For portfolio management, I'd monitor total Theta exposure to ensure time decay aligns with my strategy and risk tolerance.

---

### **6. Explain Vega's practical significance in volatility trading.**

**Ideal Answer:** Vega measures sensitivity to volatility changes, making it crucial for volatility trading strategies. Since all options have positive Vega, I'd use it to construct volatility bets - long Vega positions benefit from volatility increases, while short Vega positions profit from volatility decreases. Understanding Vega helps size positions appropriately for expected volatility moves and event-driven strategies.

---

### **7. When is Rho most important for options traders?**

**Ideal Answer:** Rho matters most for long-term options like LEAPs where interest rate changes significantly impact present value calculations. For short-term options, Rho's impact is minimal compared to other Greeks. Traders focus on Rho when managing portfolios with extended time horizons or during periods of expected interest rate changes by central banks.

---

## **Real-World Application Questions**

### **8. How does your mispricing scanner handle the difference between historical and implied volatility?**

**Ideal Answer:** My scanner uses historical volatility as a baseline proxy, acknowledging it's backward-looking while implied volatility is forward-looking. I account for this limitation by filtering results based on liquidity, bid-ask spreads, and requiring significant mispricing thresholds. The scanner flags potential opportunities but emphasizes that historical vol may not capture market expectations or upcoming events.

---

### **9. What transaction costs would eliminate apparent arbitrage opportunities?**

**Ideal Answer:** Bid-ask spreads typically 1-5% of option price, brokerage commissions, exchange fees, and securities transaction tax can eliminate theoretical profits. For example, a 5% mispricing might disappear after accounting for 2% bid-ask spread, 0.5% commission, and 0.125% STT. Real arbitrage requires mispricing exceeding total transaction costs plus risk premium.

---

### **10. How would you improve the Black-Scholes model for American options?**

**Ideal Answer:** I'd implement a binomial tree model to handle early exercise possibilities, particularly important for dividend-paying stocks where early exercise can be optimal. The tree discretizes time and price movements, allowing backward induction to determine optimal exercise points at each node. This maintains the Black-Scholes framework while adding early exercise capability.

---

## **Risk Management & Limitations Questions**

### **11. What are the biggest limitations of using historical volatility as an IV proxy?**

**Ideal Answer:** Historical volatility is backward-looking and may not capture upcoming events, regime changes, or market sentiment shifts. It doesn't account for implied volatility risk premium or market expectations of future volatility. During earnings or macro events, historical vol significantly underestimates actual volatility risk, leading to systematic mispricing in the scanner results.

---

### **12. How do you handle deep ITM/OTM options where d1 and d2 become extreme?**

**Ideal Answer:** I implemented numerical safeguards including value clamping between [-10, 10], overflow protection with try-catch blocks, and special handling for extreme moneyness ratios. For deep ITM options, the model approaches intrinsic value, while deep OTM options approach zero. These edge cases prevent numerical instability while maintaining accurate pricing for realistic trading scenarios.

---

### **13. What market conditions would cause your scanner to produce false positives?**

**Ideal Answer:** Low liquidity environments with wide bid-ask spreads, during earnings announcements when volatility expectations change rapidly, or when corporate actions like dividends or splits occur. Additionally, stale quotes or delayed data can create apparent mispricings that don't represent real arbitrage opportunities. I filter these by requiring minimum volume and reasonable spread percentages.

---

## **Advanced Technical Questions**

### **14. How would you implement a volatility surface using your scanner data?**

**Ideal Answer:** I'd collect implied volatilities across multiple strikes and expirations, then use interpolation methods like cubic splines to create a smooth surface. The scanner would calculate implied volatilities from market prices using inverse Black-Scholes, then fit a surface showing how volatility varies by moneyness and time. This captures the volatility smile and term structure missing from constant volatility assumptions.

---

### **15. Explain how you'd extend this to a stochastic volatility model like Heston.**

**Ideal Answer:** I'd implement the Heston model where volatility follows its own stochastic process with mean reversion. This requires adding volatility parameters (kappa, theta, xi, rho) and solving partial differential equations numerically, typically using finite difference methods. The scanner would then compare Heston prices to market prices, potentially identifying more sophisticated mispricings that Black-Scholes misses, especially around volatility smile effects.

---

## **Additional Topics to Master**

### **Portfolio Applications**
- How to construct Delta-neutral portfolios
- Gamma scalping strategies
- Volatility trading using Vega
- Risk management using position Greeks

### **Market Microstructure**
- Bid-ask spread dynamics
- Market impact considerations
- Liquidity assessment methods
- Execution risk management

### **Model Extensions**
- Jump diffusion models for event risk
- Local volatility models
- Stochastic correlation models
- Multi-asset options pricing

### **Practical Considerations**
- Real-time data processing
- Model calibration techniques
- Backtesting methodologies
- Performance optimization

---

**Key Interview Strategy:** Emphasize both theoretical understanding and practical implementation challenges. Show awareness of model limitations while demonstrating ability to bridge theory with real-world application.
