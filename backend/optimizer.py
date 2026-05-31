import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize

def fetch_data(tickers, period="1y"):
    """Fetch historical closing prices for given tickers."""
    try:
        data = yf.download(tickers, period=period, progress=False)
        
        # yfinance behavior: if only one ticker, 'Close' is a Series.
        # if multiple, 'Close' is a DataFrame.
        if 'Close' in data:
            data = data['Close']
        elif 'Adj Close' in data:
            data = data['Adj Close']
        else:
            # Multi-level columns workaround for latest yfinance version
            data = data.xs('Close', axis=1, level=0, drop_level=True)
            
        if isinstance(data, pd.Series):
            data = data.to_frame(name=tickers[0])
            
        # Reorder columns to match requested tickers
        # Also drop any tickers that completely failed
        valid_tickers = [t for t in tickers if t in data.columns]
        data = data[valid_tickers]
        data.dropna(inplace=True)
        return data, valid_tickers
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame(), []

def portfolio_performance(weights, mean_returns, cov_matrix):
    """Calculates expected return and volatility for a given set of weights."""
    returns = np.sum(mean_returns * weights) * 252
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    return returns, std

def get_optimal_portfolio(tickers, current_weights):
    """
    Calculate the efficient frontier and find the maximum Sharpe ratio portfolio.
    current_weights: list of weights corresponding to tickers (sum to 1)
    """
    if len(tickers) < 2:
        raise ValueError("At least two valid tickers are required for optimization.")

    data, valid_tickers = fetch_data(tickers)
    if data.empty or len(valid_tickers) < 2:
        raise ValueError("Could not fetch sufficient historical data.")

    # Filter weights for valid tickers only and renormalize
    filtered_weights = []
    for t, w in zip(tickers, current_weights):
        if t in valid_tickers:
            filtered_weights.append(w)
    
    total_w = sum(filtered_weights)
    if total_w == 0:
        filtered_weights = [1.0/len(valid_tickers)] * len(valid_tickers)
    else:
        filtered_weights = [w/total_w for w in filtered_weights]

    returns = data.pct_change().dropna()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    num_assets = len(valid_tickers)
    
    # Define optimization functions
    def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate=0.07):
        p_ret, p_std = portfolio_performance(weights, mean_returns, cov_matrix)
        if p_std == 0:
            return 0
        return -(p_ret - risk_free_rate) / p_std

    # Constraints: weights sum to 1
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    # Bounds: weights between 0 and 1 (no short selling)
    bounds = tuple((0, 1) for _ in range(num_assets))
    
    # Calculate Max Sharpe Portfolio
    initial_guess = np.array(num_assets * [1. / num_assets])
    opt_results = minimize(neg_sharpe_ratio, initial_guess, args=(mean_returns, cov_matrix),
                           method='SLSQP', bounds=bounds, constraints=constraints)
    
    max_sharpe_weights = opt_results.x
    
    # Current Portfolio Performance
    current_weights_arr = np.array(filtered_weights)
    curr_ret, curr_std = portfolio_performance(current_weights_arr, mean_returns, cov_matrix)
    curr_sharpe = (curr_ret - 0.07) / curr_std if curr_std > 0 else 0
    
    # Optimal Portfolio Performance
    opt_ret, opt_std = portfolio_performance(max_sharpe_weights, mean_returns, cov_matrix)
    opt_sharpe = (opt_ret - 0.07) / opt_std if opt_std > 0 else 0

    # Generate Efficient Frontier points
    frontier_returns = []
    frontier_volatility = []
    
    if opt_std > 0:
        min_ret = returns.mean().min() * 252
        max_ret = returns.mean().max() * 252
        
        # Ensure max_ret > min_ret
        if max_ret > min_ret:
            target_returns = np.linspace(min_ret, max_ret, 30)
            
            for target in target_returns:
                cons = ({'type': 'eq', 'fun': lambda x: portfolio_performance(x, mean_returns, cov_matrix)[0] - target},
                        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
                res = minimize(lambda w: portfolio_performance(w, mean_returns, cov_matrix)[1], 
                               initial_guess, method='SLSQP', bounds=bounds, constraints=cons)
                if res.success:
                    frontier_returns.append(target)
                    frontier_volatility.append(res.fun)

    return {
        "current_portfolio": {
            "weights": current_weights_arr.tolist(),
            "expected_return": curr_ret,
            "volatility": curr_std,
            "sharpe_ratio": curr_sharpe
        },
        "optimal_portfolio": {
            "weights": max_sharpe_weights.tolist(),
            "expected_return": opt_ret,
            "volatility": opt_std,
            "sharpe_ratio": opt_sharpe
        },
        "efficient_frontier": [
            {"volatility": v, "return": r} for v, r in zip(frontier_volatility, frontier_returns)
        ],
        "assets": valid_tickers
    }

def get_current_prices(tickers):
    if not tickers:
        return {}
    try:
        data = yf.download(tickers, period="5d", progress=False)
        
        if 'Close' in data:
            data = data['Close']
        elif 'Adj Close' in data:
            data = data['Adj Close']
        else:
            data = data.xs('Close', axis=1, level=0, drop_level=True)
            
        if isinstance(data, pd.Series):
            data = data.to_frame(name=tickers[0])
            
        latest_prices = data.iloc[-1].dropna().to_dict()
        return latest_prices
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return {}
