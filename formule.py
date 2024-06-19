from scipy.stats import norm
import numpy as np


def Black_Scholes(S0, K, r, T, sigma):
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def monte_carlo_american_call(S0, K, r, sigma, T, paths):
    dt = T / paths
    option_prices = []

    for i in range(paths):
        prices = [S0]
        for j in range(1, paths):
            Z = np.random.normal(0, 1)
            S_next = prices[-1] * np.exp(
                (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
            )
            prices.append(S_next)

        # Determine exercise opportunities
        payoffs = np.maximum(np.array(prices) - K, 0)

        # Backward induction for early exercise
        for j in range(paths - 2, 0, -1):
            payoffs[j] = np.maximum(
                payoffs[j], np.exp(-r * dt) * (0.5 * payoffs[j + 1] + 0.5 * payoffs[j])
            )

        option_prices.append(payoffs[0])

    return np.mean(option_prices)


def american_call_option_price(S, K, r, T, sigma, n):
    n = int(n)
    dt = T / n  # Time step
    u = 1 + sigma * (dt**0.5)  # Up factor
    d = 1 - sigma * (dt**0.5)  # Down factor
    p = (np.exp(r * dt) - d) / (u - d)  # Probability of up move

    # Initialize option prices at maturity
    call_option_prices = [
        np.maximum(0, S * (u**j) * (d ** (n - j)) - K) for j in range(n + 1)
    ]

    # Calculate option prices at each node using backward induction
    for i in range(n - 1, -1, -1):
        for j in range(i + 1):
            option_value = np.exp(-r * dt) * (
                p * call_option_prices[j + 1] + (1 - p) * call_option_prices[j]
            )
            intrinsic_value = np.maximum(0, S * (u**j) * (d ** (i - j)) - K)
            call_option_prices[j] = np.maximum(intrinsic_value, option_value)

    return call_option_prices[0]
