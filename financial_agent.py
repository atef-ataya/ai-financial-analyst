import os
import requrests
import json
from typing import List
from dotenv import load_dotenv

from langchain_core.tools import tool
from lanchain_openai import ChatOpenAI
from langgraph.prebuilt import create_openai_agent

# Load environment variables from .env file
# This will load the OPENAI_API_KEY and STRIPE_SECRET_KEY
load_dotenv()

#--- Tool Definitions ---
# These functions are wrappers that our agent can call. They make HTTP requests
# to the MCP servers.

@tool
def query_zerodha_kite(action: str, arguments: dict) -> dict:
    """
    Queries the Zerodha Kite MCP server to get stock market data.
    Use this for any questions about stock prices, quotes, or market data.
    Valid actions are 'get_quotes', 'get_ltp', 'get_ohlc', 'get_historical_data'.
    Arguments should be a dictionary matching the required parameters for the action.
    Example: {"action": "get_quotes", "arguments": {"instrument": "NSE:INFY"}}
    """
    
    print(f"--- Calling Zerodha Tool: {action} with args: {arguments} ---")
    try:
        response =requrests.post(
            "https://mcp.kite.trade/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": action, "arguments": arguments},
                "id": 1
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requrests.exceptions.RequestException as e:
        return {"error": f"Failed to call Zerodha MCP server: {str(e)}"}
    
@tool
def query_stripe(action: str, arguments: dict) -> dict:
    """
    Queries the local Stripe MCP server to get payment or customer data.
    Use this for any questions about revenue, payments, customers, or invoices.
    Valid actions are 'customers.create', 'charge_list', 'payment_intent_create', etc.
    Arguments should be a dictionary matching the required parameters for the action.
    Example: {"action": "charge_list", "arguments": {"limit": 5}}
    """
    
    print(f"--- Calling Stripe Tool: {action} with args: {arguments} ---")
    try:
        # The Stripe MCP server runs locally on port 3000 by default
        resposne = requrests.post(
            "http://localhost:3000",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": action, "arguments": arguments},
                "id": 1
            },
            timeout=30
        )
        
        resposne.raise_for_status()
        return resposne.json()
    except requrests.exceptions.RequestException as e:
        return {"error": f"Failed to call local Stripe MCP server. Is it running? Error: {str(e)}"}
    
#--- Agent Definition ---

# Combine the tools into a list for the agent
tools: List[tool] = [query_zerodha_kite, query_stripe]

# Set up the model (we're using gpt-4o for its strong reasoning capabilities)
model = ChatOpenAI(model="gpt-4o", temperature=0.0)

# This system prompt is the agent's "job description". It tells the agent how to behave.
system_prompt = """
You are a professional financial analyst. Your primary role is to assist users by answering their questions about financial data.

You have access to two main data sources, accessible via tools:
1.  **Zerodha Kite**: For all stock market data, including quotes, historical prices, and trading information.
2.  **Stripe**: For all business revenue data, including payments, customers, and invoices.

When a user asks a question, you must:
1.  **Analyze the query** to determine which data source (Zerodha or Stripe) is appropriate.
2.  **Select the correct tool** (`query_zerodha_kite` or `query_stripe`).
3.  **Formulate the `action` and `arguments`** required by the chosen tool based on the user's question.
4.  **Call the tool** to retrieve the data.
5.  **Synthesize the data** from the tool's response into a clear, concise, and human-readable answer.
6.  If a query requires information from both sources, you must call each tool sequentially and then combine the results in your final answer.
7.  Never ask the user for information you can get from a tool. Always try to use the tools first.
"""

# Create the ReAct agent using LangGraph's prebuilt function.
# This function wires up the model, tools, and prompt into a runnable agent.
agent_executor = create_react_agent(model, tools, messages_modifier=system_prompt)