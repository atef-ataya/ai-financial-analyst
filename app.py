# app.py

import streamlit as st
# We import our agent from the other file.
from financial_agent import agent_executor

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="MCP Financial Analyst", layout="wide")

st.title("🤖 AI Financial Analyst (MCP Demo)")
st.caption("Powered by LangGraph, Zerodha, and Stripe MCP Servers")

# --- Instructions Expander ---
with st.expander("ℹ️ How to use this demo"):
    st.write("""
        This application demonstrates an AI agent that connects to multiple real-world services via the Model Context Protocol (MCP).

        **Before you start:**
        1.  Make sure you have the local **Stripe MCP server running** in a separate terminal.
            - Command: `npx -y @stripe/mcp --tools=all`
        2.  The **Zerodha Kite MCP server** is hosted by Zerodha, so no local setup is needed for it.

        **Example Queries:**
        - `What is the current price of NIFTY 50?` (Uses Zerodha)
        - `Show me my last 3 charges on Stripe.` (Uses Stripe)
        - `What is the last traded price for NSE:RELIANCE, and also list my last charge on Stripe?` (Uses both)
    """)

# --- Session State Initialization ---
# This makes sure our chat history is saved even when the app reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Chat History Display ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and Agent Response ---
if prompt := st.chat_input("Ask a financial question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # The input to the agent is a list of messages
        inputs = {"messages": [("user", prompt)]}

        # We stream the response for a "live typing" effect
        for chunk in agent_executor.stream(inputs):
            # The output of create_react_agent is a dictionary with the key "messages"
            # The value is a list of messages. We take the last one.
            last_message = chunk.get("messages", [])[-1]
            if hasattr(last_message, 'content'):
                full_response += last_message.content
                message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    # Add agent response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})