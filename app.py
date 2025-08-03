# app.py

import streamlit as st
import time
import json
from financial_agent import agent_executor, tools

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Financial Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Clean white background */
    .main .block-container {
        padding-top: 2rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #64748b;
        margin-bottom: 2rem;
    }
    
    /* Tool badges */
    .tool-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .tool-badge-alpha {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    .tool-badge-stripe {
        background-color: #e0e7ff;
        color: #4c1d95;
    }
    
    .tool-badge-portfolio {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<h1 class="main-header">🤖 AI Financial Analyst</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Powered by LangGraph, Alpha Vantage, and Stripe</p>', unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Available tools
    st.subheader("🛠️ Available Tools")
    for tool in tools:
        tool_name = tool.name.replace("_", " ").title()
        st.success(f"✓ {tool_name}")
    
    # Settings
    show_thinking = st.checkbox("Show Agent Thinking Process", value=False)
    
    # Session metrics
    if "total_queries" not in st.session_state:
        st.session_state.total_queries = 0
        st.session_state.avg_response_time = 0
    
    if st.session_state.total_queries > 0:
        st.subheader("📊 Session Metrics")
        st.metric("Total Queries", st.session_state.total_queries)
        st.metric("Avg Response Time", f"{st.session_state.avg_response_time:.2f}s")
    
    # Example queries
    st.subheader("💡 Example Queries")
    
    if st.button("What is the stock price of Apple?"):
        st.session_state.example_query = "What is the stock price of Apple?"
        
    if st.button("Show me my last 5 Stripe charges"):
        st.session_state.example_query = "Show me my last 5 Stripe charges"
        
    if st.button("Calculate portfolio: 10 AAPL, 5 GOOGL"):
        st.session_state.example_query = "Calculate portfolio value: 10 AAPL, 5 GOOGL, 20 MSFT"

# --- Instructions ---
with st.expander("ℹ️ How to use this AI Financial Analyst"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **📈 Stock Queries:**
        - Get real-time stock prices
        - Use company names or tickers
        - Calculate portfolio values
        """)
    with col2:
        st.markdown("""
        **💳 Payment Queries:**
        - View recent Stripe charges
        - Check payment history
        - Analyze transaction data
        """)

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "response_times" not in st.session_state:
    st.session_state.response_times = []

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("execution_time"):
            st.caption(f"⚡ {message['execution_time']}")

# --- Handle Input ---
# Check for example query
if "example_query" in st.session_state:
    prompt = st.session_state.example_query
    del st.session_state.example_query
else:
    prompt = st.chat_input("Ask me about stocks or payments...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Show thinking indicator
        if show_thinking:
            with st.spinner("🤔 Thinking..."):
                start_time = time.time()
                
                try:
                    # Call the agent
                    response = agent_executor.invoke({"messages": [("user", prompt)]})
                    
                    # Extract the final message
                    final_message = response["messages"][-1].content
                    
                    # Calculate execution time
                    execution_time = time.time() - start_time
                    
                    # Update metrics
                    st.session_state.total_queries += 1
                    st.session_state.response_times.append(execution_time)
                    st.session_state.avg_response_time = sum(st.session_state.response_times) / len(st.session_state.response_times)
                    
                except Exception as e:
                    final_message = f"❌ Error: {str(e)}"
                    execution_time = time.time() - start_time
        else:
            # Without thinking indicator
            start_time = time.time()
            
            try:
                with st.spinner("Processing..."):
                    response = agent_executor.invoke({"messages": [("user", prompt)]})
                    final_message = response["messages"][-1].content
                    execution_time = time.time() - start_time
                    
                    # Update metrics
                    st.session_state.total_queries += 1
                    st.session_state.response_times.append(execution_time)
                    st.session_state.avg_response_time = sum(st.session_state.response_times) / len(st.session_state.response_times)
                    
            except Exception as e:
                final_message = f"❌ Error: {str(e)}"
                execution_time = time.time() - start_time
        
        # Display response with streaming effect
        displayed_text = ""
        for word in final_message.split():
            displayed_text += word + " "
            message_placeholder.markdown(displayed_text + "▌")
            time.sleep(0.02)
        
        # Final display
        message_placeholder.markdown(final_message)
        
        # Show execution time
        exec_time_str = f"{execution_time:.2f}s"
        st.caption(f"⚡ Response time: {exec_time_str}")
        
        # Add to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_message,
            "execution_time": exec_time_str
        })

# --- Footer ---
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔒 Your data is secure")
with col2:
    st.caption("⚡ Powered by GPT-4")
with col3:
    st.caption("🚀 Built with LangGraph")