# financial_agent.py

import os
import requests
import json
from typing import List
from dotenv import load_dotenv

import stripe # Import the new library

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Load environment variables from .env file
load_dotenv()

# Set the Stripe API key for the library
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# --- Tool Definitions ---

@tool
def query_alpha_vantage(query: str) -> dict:
    """
    Queries the Alpha Vantage API for the stock price of a specific public company.
    This tool does not support market indices, funds, or cryptocurrencies.
    Use it only for company names or stock tickers like 'Apple' or 'MSFT'.
    """
    # This function remains the same...
    print(f"--- Calling Alpha Vantage Tool with query: {query} ---")
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return {"error": "Alpha Vantage API key not found."}

    try:
        search_url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey={api_key}"
        search_response = requests.get(search_url, timeout=20)
        search_response.raise_for_status()
        search_data = search_response.json()

        if not search_data.get("bestMatches"):
            return {"error": f"No stock symbol found for '{query}'."}
        
        symbol = search_data["bestMatches"][0]["1. symbol"]
        print(f"--- Found symbol: {symbol} for query: {query} ---")

        quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        quote_response = requests.get(quote_url, timeout=20)
        quote_response.raise_for_status()
        quote_data = quote_response.json()
        
        print(f"--- Response JSON: {quote_data} ---")
        return quote_data

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to call Alpha Vantage API: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}


@tool
def list_stripe_charges(limit: int = 3) -> str:
    """
    Lists the most recent charges from Stripe.
    You can specify how many charges to retrieve with the 'limit' parameter.
    """
    print(f"--- Calling Stripe Tool: list_charges with limit: {limit} ---")
    try:
        charges = stripe.Charge.list(limit=limit)
        if not charges.data:
            return "No charges found."
        # Convert the Stripe objects to a more readable JSON string for the agent
        return json.dumps([charge.to_dict() for charge in charges.data], indent=2)
    except Exception as e:
        print(f"--- ERROR in Stripe Tool: {e} ---")
        return f"An error occurred while fetching charges from Stripe: {e}"

# --- Agent Definition ---

tools: List[tool] = [query_alpha_vantage, list_stripe_charges] # Updated tool list

model = ChatOpenAI(model="gpt-4o", temperature=0)

system_prompt = """
You are a helpful financial analyst. Your primary role is to assist users by answering their questions using the tools you have access to.

You have two tools:
1.  **Alpha Vantage**: Use this to get stock market data for **publicly traded companies only**.
2.  **Stripe**: Use the `list_stripe_charges` tool to get business revenue data like recent payments.

Your workflow is:
1.  Analyze the user's question.
2.  If the question is about a company's stock price, use the `query_alpha_vantage` tool.
3.  If the question is about business revenue or recent charges, use the `list_stripe_charges` tool.
4.  If you cannot answer the question with your tools, you must explain why.
5.  After using a tool, synthesize the data into a clear, human-readable answer.
"""

agent_executor = create_react_agent(model, tools, messages_modifier=system_prompt)