"""
FastAPI Payment Processing Application

This module implements a FastAPI application that provides endpoints for:
- Chat-based payment agent interactions
- Cryptocurrency price analysis
- Price bargaining simulation

The application integrates with:
- CoinGecko API for cryptocurrency data
- Custom payment agent for processing transactions
- Mock bargaining system for price negotiations
"""

import os
import random
from datetime import datetime
from typing import Dict, Any

import pandas as pd
import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from payment_ops import create_payment_agent

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="Payment Processing API",
    description="API for payment processing, crypto analysis, and price negotiation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"


class CryptoRequest(BaseModel):
    """Request model for cryptocurrency price checks."""
    coin_name: str


class BargainRequest(BaseModel):
    """Request model for price bargaining."""
    target_price: float
    offered_price: float


class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    message: str


@app.post("/chat")
async def chat_with_agent(request: ChatRequest) -> Dict[Any, Any]:
    """
    Process chat messages through the payment agent.

    Args:
        request (ChatRequest): The chat message request

    Returns:
        Dict[Any, Any]: Response containing agent's output and status

    Raises:
        HTTPException: If there's an error processing the request
    """
    agent = create_payment_agent()
    try:
        response = agent.invoke({"input": request.message})
        return {
            "response": response["output"],
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )


@app.post("/check-crypto-price")
async def check_crypto_price(request: CryptoRequest):
    """
    Check if a cryptocurrency's current price is below its 50-day moving average.

    Args:
        request (CryptoRequest): The cryptocurrency to check

    Returns:
        dict: Contains boolean indicating if price is below moving average

    Raises:
        HTTPException: If cryptocurrency is not found or there's an API error
    """
    try:
        # Get coin ID from CoinGecko
        search_response = requests.get(
            f"{COINGECKO_BASE_URL}/search",
            params={"query": request.coin_name}
        )
        search_response.raise_for_status()
        search_data = search_response.json()
        
        if not search_data['coins']:
            raise HTTPException(
                status_code=404,
                detail=f"Cryptocurrency {request.coin_name} not found"
            )
        
        coin_id = search_data['coins'][0]['id']
        
        # Fetch historical price data
        price_response = requests.get(
            f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart",
            params={
                "vs_currency": "usd",
                "days": "50",
                "interval": "daily"
            }
        )
        price_response.raise_for_status()
        price_data = price_response.json()
        
        # Calculate moving average
        prices_df = pd.DataFrame(price_data['prices'], columns=['timestamp', 'price'])
        current_price = prices_df['price'].iloc[-1]
        ma_50 = prices_df['price'].rolling(window=50).mean().iloc[-1]
        
        return {
            "below_ma": bool(current_price < ma_50),
            "current_price": float(current_price),
            "moving_average": float(ma_50)
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching data from CoinGecko: {str(e)}"
        )


@app.post("/bargain")
async def bargain(request: BargainRequest):
    """
    Simulate price bargaining with a simple probability model.

    The success chance is based on the price difference percentage:
    - Higher price difference = Lower success chance
    - Base chance is 50%
    - Final chance is adjusted based on price difference

    Args:
        request (BargainRequest): Target and offered prices

    Returns:
        dict: Contains boolean indicating if bargain was successful
    """
    price_difference_percentage = (
        (request.target_price - request.offered_price)
        / request.target_price * 100
    )
    base_chance = 0.5
    adjusted_chance = base_chance - (price_difference_percentage * 0.01)
    final_chance = max(0.1, min(0.9, adjusted_chance))
    success = random.random() < final_chance
    
    return {"success": success}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )