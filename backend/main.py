from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
from optimizer import get_optimal_portfolio, get_current_prices

app = FastAPI(title="Portfolio Optimizer API")

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TickerUnits(BaseModel):
    ticker: str
    units: float

class OptimizeRequest(BaseModel):
    holdings: List[TickerUnits]

@app.get("/prices")
def fetch_prices(tickers: str):
    """Fetch current prices for a comma-separated list of tickers."""
    ticker_list = [t.strip() for t in tickers.split(",") if t.strip()]
    if not ticker_list:
        return {"prices": {}}
    
    prices = get_current_prices(ticker_list)
    return {"prices": prices}

@app.post("/optimize")
def optimize_portfolio(request: OptimizeRequest):
    if len(request.holdings) < 2:
        raise HTTPException(status_code=400, detail="At least two valid instruments are required for optimization.")
    
    tickers = [h.ticker for h in request.holdings]
    units = [h.units for h in request.holdings]
    
    # Calculate current value of each holding
    prices = get_current_prices(tickers)
    
    if not prices:
        raise HTTPException(status_code=400, detail="Could not fetch latest prices for the given instruments.")
        
    current_values = []
    valid_tickers = []
    
    for t, u in zip(tickers, units):
        if t in prices:
            current_values.append(u * prices[t])
            valid_tickers.append(t)
            
    if len(valid_tickers) < 2:
        raise HTTPException(status_code=400, detail="Not enough valid instruments found on Yahoo Finance to optimize.")
        
    total_value = sum(current_values)
    current_weights = [cv / total_value for cv in current_values] if total_value > 0 else [1.0/len(valid_tickers)] * len(valid_tickers)
    
    try:
        results = get_optimal_portfolio(valid_tickers, current_weights)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
