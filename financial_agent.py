# financial_agent.py

import os
import requests
import json
import time
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

import stripe

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()

# Set Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# --- Tool Definitions ---

@tool
def query_alpha_vantage(query: str) -> dict:
    """
    Queries the Alpha Vantage API for stock prices.
    Use company names or ticker symbols like 'Apple' or 'AAPL'.
    """
    print(f"[Alpha Vantage] Searching for: {query}")
    
    # Check for demo mode (useful for testing when API is limited)
    if os.getenv("DEMO_MODE", "").lower() == "true":
        # Return mock data for common stocks
        mock_data = {
            "apple": {"symbol": "AAPL", "price": "182.52", "change": "+1.25", "change_percent": "+0.69%"},
            "aapl": {"symbol": "AAPL", "price": "182.52", "change": "+1.25", "change_percent": "+0.69%"},
            "google": {"symbol": "GOOGL", "price": "142.85", "change": "-0.63", "change_percent": "-0.44%"},
            "googl": {"symbol": "GOOGL", "price": "142.85", "change": "-0.63", "change_percent": "-0.44%"},
            "microsoft": {"symbol": "MSFT", "price": "378.91", "change": "+2.15", "change_percent": "+0.57%"},
            "msft": {"symbol": "MSFT", "price": "378.91", "change": "+2.15", "change_percent": "+0.57%"},
            "tesla": {"symbol": "TSLA", "price": "251.44", "change": "-3.21", "change_percent": "-1.26%"},
            "tsla": {"symbol": "TSLA", "price": "251.44", "change": "-3.21", "change_percent": "-1.26%"},
        }
        
        query_lower = query.lower()
        if query_lower in mock_data:
            data = mock_data[query_lower]
            return {
                "success": True,
                "company": query.title(),
                "symbol": data["symbol"],
                "price": data["price"],
                "change": data["change"],
                "change_percent": data["change_percent"],
                "volume": "52,341,023",
                "latest_trading_day": datetime.now().strftime("%Y-%m-%d"),
                "note": "Demo mode - using mock data"
            }
        else:
            return {"error": f"Stock '{query}' not found in demo data. Try: Apple, Google, Microsoft, or Tesla"}
    
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return {"error": "Alpha Vantage API key not found in .env file"}
    
    try:
        # Search for symbol
        search_url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey={api_key}"
        print(f"[Alpha Vantage] Calling: {search_url}")
        
        search_response = requests.get(search_url, timeout=10)
        search_data = search_response.json()
        
        print(f"[Alpha Vantage] Search response: {json.dumps(search_data, indent=2)}")
        
        # Check for various API limit messages
        if "Note" in search_data:
            return {"error": "API rate limit reached (5 calls/minute). Please wait 60 seconds or enable DEMO_MODE=true in your .env file"}
        
        if "Information" in search_data:
            return {"error": f"API message: {search_data['Information']}"}
        
        if "Error Message" in search_data:
            return {"error": f"API error: {search_data['Error Message']}"}
        
        if not search_data.get("bestMatches"):
            return {"error": f"No stock found for '{query}'. The API might be temporarily unavailable."}
        
        # Get the symbol
        symbol = search_data["bestMatches"][0]["1. symbol"]
        company_name = search_data["bestMatches"][0]["2. name"]
        
        # Get quote
        quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        print(f"[Alpha Vantage] Getting quote: {quote_url}")
        
        quote_response = requests.get(quote_url, timeout=10)
        quote_data = quote_response.json()
        
        print(f"[Alpha Vantage] Quote response: {json.dumps(quote_data, indent=2)}")
        
        # Check for rate limits in quote response
        if "Note" in quote_data:
            return {"error": "API rate limit reached on quote request. Please wait 60 seconds or enable DEMO_MODE=true"}
        
        if not quote_data.get("Global Quote") or not quote_data["Global Quote"]:
            return {"error": f"No price data available for {symbol}. The market may be closed or API is limited."}
        
        quote = quote_data["Global Quote"]
        return {
            "success": True,
            "company": company_name,
            "symbol": symbol,
            "price": quote.get("05. price", "N/A"),
            "change": quote.get("09. change", "N/A"),
            "change_percent": quote.get("10. change percent", "N/A"),
            "volume": quote.get("06. volume", "N/A"),
            "latest_trading_day": quote.get("07. latest trading day", "N/A")
        }
        
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The API might be slow or unavailable."}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error. Please check your internet connection."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}. Consider enabling DEMO_MODE=true for testing."}


@tool
def list_stripe_charges(limit: int = 5) -> str:
    """
    Lists recent Stripe charges. Default limit is 5.
    """
    print(f"[Stripe] Fetching {limit} charges")
    
    if not stripe.api_key:
        return json.dumps({"error": "Stripe API key not found in .env file"})
    
    try:
        charges = stripe.Charge.list(limit=limit)
        
        if not charges.data:
            return json.dumps({"message": "No charges found", "count": 0})
        
        formatted_charges = []
        for charge in charges.data:
            formatted_charges.append({
                "amount": f"${charge.amount / 100:.2f}",
                "currency": charge.currency.upper(),
                "status": charge.status,
                "description": charge.description or "No description",
                "created": datetime.fromtimestamp(charge.created).strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return json.dumps({
            "success": True,
            "count": len(formatted_charges),
            "charges": formatted_charges
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch charges: {str(e)}"})


@tool
def calculate_portfolio_value(stocks: List[str], shares: List[int]) -> str:
    """
    Calculate portfolio value for multiple stocks.
    Example: stocks=['AAPL', 'GOOGL'], shares=[10, 5]
    """
    print(f"[Portfolio] Calculating value for {len(stocks)} stocks")
    
    if len(stocks) != len(shares):
        return json.dumps({"error": "Number of stocks must match number of shares"})
    
    portfolio = []
    total_value = 0
    
    for symbol, num_shares in zip(stocks, shares):
        stock_data = query_alpha_vantage(symbol)
        
        if stock_data.get("success"):
            try:
                price = float(stock_data["price"])
                value = price * num_shares
                total_value += value
                
                portfolio.append({
                    "symbol": stock_data["symbol"],
                    "company": stock_data["company"],
                    "shares": num_shares,
                    "price": f"${price:.2f}",
                    "value": f"${value:.2f}"
                })
            except:
                portfolio.append({
                    "symbol": symbol,
                    "error": "Could not calculate value"
                })
        else:
            portfolio.append({
                "symbol": symbol,
                "error": stock_data.get("error", "Unknown error")
            })
    
    return json.dumps({
        "portfolio": portfolio,
        "total_value": f"${total_value:.2f}",
        "stocks_count": len(portfolio)
    }, indent=2)


# --- Agent Setup ---

# List of available tools
tools = [query_alpha_vantage, list_stripe_charges, calculate_portfolio_value]

# Initialize the LLM
model = ChatOpenAI(model="gpt-4o", temperature=0)

# System prompt
system_prompt = """You are an AI Financial Analyst with access to real-time data.

Available tools:
1. query_alpha_vantage - Get stock prices for any public company
2. list_stripe_charges - View recent payment transactions
3. calculate_portfolio_value - Calculate total value of stock holdings

Always be helpful and provide clear, formatted responses. If a tool returns an error, 
explain it to the user and suggest alternatives."""

# Create the agent
agent_executor = create_react_agent(model, tools, messages_modifier=system_prompt)