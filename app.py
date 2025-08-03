# app.py

import streamlit as st
# We import our agent from the other file.
from financial_agent import agent_executor

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="MCP Financial Analyst", layout="wide")

st.title("🤖 AI Financial Analyst")
st.caption("Powered by LangGraph, Alpha Vantage, and Stripe")

# --- Instructions Expander ---
with st.expander("ℹ️ How to use this demo"):
    st.write("""
        This application demonstrates an AI agent that connects to multiple real-world services.

        **Example Queries:**
        - `What is the stock price of Apple?` (Uses Alpha Vantage)
        - `Show me my last 3 charges on Stripe.` (Uses Stripe)
    """)

# --- Session State Initialization ---
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
        # Use a spinner to let the user know something is happening
        with st.spinner("Thinking..."):
            # The input to the agent is a list of messages
            inputs = {"messages": [("user", prompt)]}
            
            # Invoke the agent directly to get the final response
            response = agent_executor.invoke(inputs)
            
            # The final answer is in the 'content' of the last message
            final_answer = response['messages'][-1].content
            st.markdown(final_answer)
    
    # Add agent response to chat history
    st.session_state.messages.append({"role": "assistant", "content": final_answer})