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

# Load environment variables from .env file
load_dotenv()

# Set the Stripe API key for the library
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# --- Enhanced Tool Definitions with Better Error Handling ---

@tool
def query_alpha_vantage(query: str) -> dict:
    """
    Queries the Alpha Vantage API for the stock price of a specific public company.
    This tool does not support market indices, funds, or cryptocurrencies.
    Use it only for company names or stock tickers like 'Apple' or 'MSFT'.
    """
    print(f"--- Calling Alpha Vantage Tool with query: {query} ---")
    
    # Track execution time
    start_time = time.time()
    
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return {"error": "Alpha Vantage API key not found. Please check your .env file."}

    try:
        # Step 1: Search for the stock symbol
        search_url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey={api_key}"
        search_response = requests.get(search_url, timeout=20)
        search_response.raise_for_status()
        search_data = search_response.json()
        
        # Check for rate limiting
        if "Note" in search_data:
            return {"error": "API rate limit reached. Please wait 60 seconds and try again."}
        
        if "Information" in search_data:
            return {"error": f"API Error: {search_data['Information']}"}

        if not search_data.get("bestMatches"):
            return {"error": f"No stock symbol found for '{query}'. Try using the company ticker symbol (e.g., AAPL for Apple)."}
        
        # Get the best match
        best_match = search_data["bestMatches"][0]
        symbol = best_match["1. symbol"]
        company_name = best_match["2. name"]
        
        print(f"--- Found: {company_name} ({symbol}) ---")

        # Step 2: Get the stock quote
        quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        quote_response = requests.get(quote_url, timeout=20)
        quote_response.raise_for_status()
        quote_data = quote_response.json()
        
        # Check for rate limiting in quote response
        if "Note" in quote_data:
            return {"error": "API rate limit reached. Please wait 60 seconds and try again."}
        
        if "Information" in quote_data:
            return {"error": f"API Error: {quote_data['Information']}"}
        
        # Check if we got valid data
        if not quote_data.get("Global Quote") or not quote_data["Global Quote"]:
            return {
                "error": f"No real-time data available for {symbol}. This could mean:\n"
                         f"1. The market is closed (trading hours: 9:30 AM - 4:00 PM EST)\n"
                         f"2. The symbol is not actively traded\n"
                         f"3. There's a temporary data issue"
            }
        
        # Extract and format the data
        global_quote = quote_data["Global Quote"]
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        result = {
            "success": True,
            "company": company_name,
            "symbol": symbol,
            "price": global_quote.get("05. price", "N/A"),
            "change": global_quote.get("09. change", "N/A"),
            "change_percent": global_quote.get("10. change percent", "N/A"),
            "volume": global_quote.get("06. volume", "N/A"),
            "latest_trading_day": global_quote.get("07. latest trading day", "N/A"),
            "previous_close": global_quote.get("08. previous close", "N/A"),
            "execution_time": f"{execution_time:.2f} seconds"
        }
        
        print(f"--- Success! Retrieved data in {execution_time:.2f} seconds ---")
        return result

    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The API might be slow. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error. Please check your internet connection."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to call Alpha Vantage API: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


@tool
def list_stripe_charges(limit: int = 5) -> str:
    """
    Lists the most recent charges from Stripe.
    You can specify how many charges to retrieve with the 'limit' parameter (default: 5, max: 100).
    """
    print(f"--- Calling Stripe Tool: list_charges with limit: {limit} ---")
    
    # Validate limit
    limit = min(max(1, limit), 100)  # Ensure limit is between 1 and 100
    
    start_time = time.time()
    
    try:
        # Check if API key is set
        if not stripe.api_key:
            return json.dumps({
                "error": "Stripe API key not found. Please check your .env file.",
                "success": False
            })
        
        # Retrieve charges
        charges = stripe.Charge.list(limit=limit)
        
        if not charges.data:
            return json.dumps({
                "success": True,
                "message": "No charges found in your Stripe account.",
                "count": 0,
                "charges": []
            })
        
        # Format the charges for better readability
        formatted_charges = []
        for charge in charges.data:
            formatted_charge = {
                "id": charge.id,
                "amount": f"${charge.amount / 100:.2f}",  # Convert cents to dollars
                "currency": charge.currency.upper(),
                "status": charge.status,
                "description": charge.description or "No description",
                "customer_email": charge.billing_details.email if charge.billing_details else "N/A",
                "created": datetime.fromtimestamp(charge.created).strftime("%Y-%m-%d %H:%M:%S"),
                "payment_method": charge.payment_method_details.type if charge.payment_method_details else "N/A"
            }
            formatted_charges.append(formatted_charge)
        
        execution_time = time.time() - start_time
        
        result = {
            "success": True,
            "count": len(formatted_charges),
            "execution_time": f"{execution_time:.2f} seconds",
            "charges": formatted_charges
        }
        
        print(f"--- Success! Retrieved {len(formatted_charges)} charges in {execution_time:.2f} seconds ---")
        return json.dumps(result, indent=2)
        
    except stripe.error.AuthenticationError:
        return json.dumps({
            "error": "Invalid Stripe API key. Please check your credentials.",
            "success": False
        })
    except stripe.error.RateLimitError:
        return json.dumps({
            "error": "Stripe API rate limit exceeded. Please try again in a moment.",
            "success": False
        })
    except stripe.error.APIConnectionError:
        return json.dumps({
            "error": "Network error connecting to Stripe. Please check your connection.",
            "success": False
        })
    except Exception as e:
        print(f"--- ERROR in Stripe Tool: {e} ---")
        return json.dumps({
            "error": f"An unexpected error occurred: {str(e)}",
            "success": False
        })


@tool
def calculate_portfolio_value(stocks: List[str], shares: List[int]) -> str:
    """
    Calculate the total value of a stock portfolio.
    Provide a list of stock symbols and the number of shares for each.
    Example: stocks=['AAPL', 'GOOGL'], shares=[10, 5]
    """
    print(f"--- Calculating portfolio value for {len(stocks)} stocks ---")
    
    if len(stocks) != len(shares):
        return json.dumps({
            "error": "The number of stocks must match the number of shares.",
            "success": False
        })
    
    portfolio = []
    total_value = 0
    errors = []
    
    for symbol, num_shares in zip(stocks, shares):
        stock_data = query_alpha_vantage(symbol)
        
        if isinstance(stock_data, dict) and stock_data.get("success"):
            try:
                price = float(stock_data["price"])
                value = price * num_shares
                total_value += value
                
                portfolio.append({
                    "symbol": stock_data["symbol"],
                    "company": stock_data["company"],
                    "shares": num_shares,
                    "price_per_share": f"${price:.2f}",
                    "total_value": f"${value:.2f}",
                    "change_percent": stock_data.get("change_percent", "N/A")
                })
            except (ValueError, KeyError):
                errors.append(f"Could not process data for {symbol}")
        else:
            errors.append(f"Failed to get data for {symbol}: {stock_data.get('error', 'Unknown error')}")
    
    result = {
        "success": len(portfolio) > 0,
        "portfolio": portfolio,
        "total_portfolio_value": f"${total_value:.2f}",
        "stocks_analyzed": len(portfolio),
        "errors": errors if errors else None
    }
    
    return json.dumps(result, indent=2)


# --- Agent Definition with Memory ---

tools: List[tool] = [
    query_alpha_vantage, 
    list_stripe_charges,
    calculate_portfolio_value
]

# Initialize the model
model = ChatOpenAI(
    model="gpt-4o", 
    temperature=0,
    streaming=True  # Enable streaming for better UX
)

# Enhanced system prompt
system_prompt = """
You are a helpful AI Financial Analyst with access to real-time market data and payment information. 

Your capabilities include:
1. **Alpha Vantage**: Get real-time stock prices and market data for publicly traded companies
2. **Stripe**: Access business payment data, including recent charges
3. **Portfolio Calculator**: Calculate the total value of a stock portfolio

Important guidelines:
- Always provide specific, actionable insights when analyzing data
- If you encounter an API rate limit, inform the user and suggest waiting 60 seconds
- For stock queries, you can use company names or ticker symbols
- Market hours are 9:30 AM - 4:00 PM EST (Mon-Fri)
- Format monetary values clearly (e.g., $1,234.56)
- If an error occurs, provide helpful suggestions to resolve it

When analyzing financial data:
- Highlight significant changes or trends
- Provide context for the numbers (e.g., "up 5% from yesterday")
- Suggest relevant follow-up analyses when appropriate
"""

# Create agent executor
agent_executor = create_react_agent(
    model, 
    tools, 
    messages_modifier=system_prompt
)

# Export the tools list for the UI
__all__ = ['agent_executor', 'tools']