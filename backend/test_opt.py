import numpy as np
from scipy.optimize import minimize

def neg_sharpe(w, expected_returns, cov_matrix, risk_free_rate):
    ret = np.dot(w, expected_returns)
    vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
    if vol == 0:
        return 0
    return -(ret - risk_free_rate) / vol

er = np.array([0.4816, 0.19])
cov = np.array([[0.0887, 0.02], [0.02, 0.0169]]) # 30% vol and 13% vol, some correlation

initial_weights = np.array([0.5, 0.5])
bounds = ((0, 1), (0, 1))
constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

res1 = minimize(neg_sharpe, initial_weights, args=(er, cov, 0.068), method="SLSQP", bounds=bounds, constraints=constraints)
print("With Rf=0.068:", res1.x)

res2 = minimize(neg_sharpe, initial_weights, args=(er, cov, 0.15), method="SLSQP", bounds=bounds, constraints=constraints)
print("With Rf=0.15:", res2.x)

res3 = minimize(neg_sharpe, initial_weights, args=(er, cov, 0.0), method="SLSQP", bounds=bounds, constraints=constraints)
print("With Rf=0.0:", res3.x)
