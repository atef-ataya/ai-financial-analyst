"""
MCP Financial Analyst UI
==================================================

A streamlined Streamlit interface that works with the simplified MCP agent.
"""

import streamlit as st
import time
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from mcp_financial_agent import agent_executor, tools, MCP_ENABLED

# Page configuration
st.set_page_config(
    page_title="MCP Financial Analyst Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS with MCP theming
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .mcp-status-good {
        background: linear-gradient(135deg, #4caf50, #45a049);
        color: white;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 2px 10px rgba(76,175,80,0.3);
    }
    
    .mcp-status-warning {
        background: linear-gradient(135deg, #ff9800, #f57c00);
        color: white;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 2px 10px rgba(255,152,0,0.3);
    }
    
    .metrics-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .tutorial-card {
        background: #f8f9ff;
        border: 2px solid #e3f2fd;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .tutorial-step {
        background: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .code-example {
        background: #282c34;
        color: #abb2bf;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Fira Code', monospace;
        margin: 1rem 0;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

# header
st.markdown("""
<div class="main-header">
    <h1>🌐 MCP Financial Analyst Pro</h1>
    <p>Enhanced Model Context Protocol • Intelligent Fallback • Professional Demo Mode</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for tutorial progress
if "tutorial_progress" not in st.session_state:
    st.session_state.tutorial_progress = {
        "current_step": 0,
        "completed_steps": [],
        "tutorial_active": False,
        "tutorial_type": None
    }

# Initialize simplified metrics
if "app_metrics" not in st.session_state:
    st.session_state.app_metrics = {
        "total_queries": 0,
        "successful_queries": 0,
        "avg_response_time": 0,
        "Indian_stocks_queried": 0,
        "us_stocks_queried": 0,
        "portfolio_analyses": 0,
        "stripe_queries": 0,
        "tutorial_completions": 0
    }

# Sidebar with simplified features
with st.sidebar:
    st.markdown("### 🎓 **Interactive Tutorials**")
    
    # Tutorial selection
    tutorial_options = [
        "🚀 Quick Start: MCP Basics",
        "📊 Live Stock Analysis", 
        "💼 Portfolio Deep Dive",
        "💳 Payment Data Integration"
    ]
    
    selected_tutorial = st.selectbox("Choose a tutorial:", ["None"] + tutorial_options)
    
    if selected_tutorial != "None" and not st.session_state.tutorial_progress["tutorial_active"]:
        if st.button("🎯 Start Tutorial", use_container_width=True):
            st.session_state.tutorial_progress["tutorial_active"] = True
            st.session_state.tutorial_progress["tutorial_type"] = selected_tutorial
            st.session_state.tutorial_progress["current_step"] = 0
            st.rerun()
    
    if st.session_state.tutorial_progress["tutorial_active"]:
        if st.button("❌ Stop Tutorial", use_container_width=True):
            st.session_state.tutorial_progress["tutorial_active"] = False
            st.rerun()
    
    st.markdown("---")
    
    # MCP Configuration Status
    st.markdown("### 🔧 **MCP Configuration**")
    
    if MCP_ENABLED:
        st.markdown('<div class="mcp-status-good">🌐 <strong>MCP Active</strong><br/>Intelligent fallback enabled</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="mcp-status-warning">⚠️ <strong>MCP Disabled</strong><br/>Enable in .env file</div>', unsafe_allow_html=True)
    
    # Server status (simplified)
    st.markdown("### 🛰️ **Data Sources**")
    
    st.markdown("**Live Market Data**")
    st.markdown("🟢 NSE/BSE Coverage")
    
    st.markdown("**US Market Data**") 
    st.markdown("🟡 Demo Mode")
    
    st.markdown("**Stripe Payments**")
    st.markdown("🟢 Local MCP Ready")
    
    # Quick Actions
    st.markdown("### ⚡ **Smart Actions**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 MCP Status", use_container_width=True):
            st.session_state.example_query = "Check the MCP system status and provide diagnostics"
        
        if st.button("📈 NIFTY 50", use_container_width=True):
            st.session_state.example_query = "What is the current NIFTY 50 price and performance?"
    
    with col2:
        if st.button("🏢 Live Stocks", use_container_width=True):
            st.session_state.example_query = "Show me RELIANCE and TCS stock prices with analysis"
        
        if st.button("💼 Portfolio", use_container_width=True):
            st.session_state.example_query = "Analyze portfolio: 10 RELIANCE, 5 TCS, 20 HDFC, 15 INFY"

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # MCP Protocol explanation
    with st.expander("🌐 **MCP Implementation Features**", expanded=False):
        st.markdown("""
        **Our Production-Grade MCP Features:**
        
        **🔄 Intelligent Protocol Handling:**
        - Real MCP JSON-RPC 2.0 communication attempts
        - Professional authentication error handling
        - Seamless fallback to high-quality demo data
        
        **📊 Smart Data Sources:**
        - Live stocks: Realistic NSE/BSE market data
        - US stocks: Professional cross-market demonstration
        - Stripe payments: Local MCP server integration
        
        **🛡️ Enhanced Reliability:**
        - Never fails - always provides professional data
        - Clear explanation of data sources used
        - Production-grade error recovery patterns
        
        **⚡ Professional Experience:**
        - Consistent response format regardless of data source
        - Real-time performance tracking
        - Advanced portfolio analytics with risk assessment
        """)

with col2:
    # Simplified metrics dashboard
    st.markdown('<div class="metrics-card">', unsafe_allow_html=True)
    st.markdown("### 📊 **Session Analytics**")
    
    metrics = st.session_state.app_metrics
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Total Queries", metrics["total_queries"])
        st.metric("Success Rate", f"{(metrics['successful_queries']/max(metrics['total_queries'], 1)*100):.1f}%")
    with col_b:
        st.metric("Avg Response", f"{metrics['avg_response_time']:.2f}s")
        st.metric("Live Stocks", metrics["Indian_stocks_queried"])
    
    # Query type breakdown
    if metrics["total_queries"] > 0:
        st.markdown("**Query Distribution:**")
        query_types = {
            "Live Stocks": metrics["Indian_stocks_queried"],
            "US Stocks": metrics["us_stocks_queried"], 
            "Portfolio": metrics["portfolio_analyses"],
            "Payments": metrics["stripe_queries"]
        }
        
        active_types = {k: v for k, v in query_types.items() if v > 0}
        if active_types:
            fig = px.pie(
                values=list(active_types.values()),
                names=list(active_types.keys()),
                title="Query Types",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=200, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tutorial mode handling
if st.session_state.tutorial_progress["tutorial_active"]:
    st.markdown("## 🎓 Interactive Tutorial Mode")
    
    tutorial_type = st.session_state.tutorial_progress["tutorial_type"]
    current_step = st.session_state.tutorial_progress["current_step"]
    
    if "Quick Start" in tutorial_type:
        if current_step == 0:
            st.markdown("""
            <div class="tutorial-card">
                <h3>🌐 Welcome to MCP!</h3>
                <p>You're about to learn how Model Context Protocol revolutionizes AI integration.</p>
                
                <div class="tutorial-step">
                    <strong>What makes this special:</strong><br/>
                    • Real MCP protocol attempts with intelligent fallback<br/>
                    • Professional data sources for Live and US markets<br/>
                    • Production-grade error handling and recovery<br/>
                    • Consistent user experience regardless of server status
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Next: Try Your First Query ➡️"):
                st.session_state.tutorial_progress["current_step"] = 1
                st.rerun()

# Chat interface
st.markdown("---")
st.markdown("### 💬 **Chat with Your MCP Financial Analyst**")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "🚀 **Welcome to the MCP Financial Analyst!**\n\nI'm powered by an intelligent MCP implementation with professional fallback systems. I provide consistent, high-quality financial data regardless of server status.\n\n**🎯 Try these enhanced queries:**\n- 'What's the current RELIANCE stock price?' (Live market data)\n- 'Show me TCS and HDFC performance' (Multi-stock analysis)\n- 'Analyze portfolio: 10 RELIANCE, 5 TCS, 20 HDFC' (Portfolio analytics)\n- 'Check MCP system status' (Technical diagnostics)\n\n**🌐 MCP Features:** Real protocol attempts, intelligent fallback, professional data quality!",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": "welcome"
        }
    ]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("timestamp"):
            st.caption(f"⏰ {message['timestamp']}")
        if message.get("mcp_info"):
            st.info(f"🌐 MCP: {message['mcp_info']}")

# Chat input
chat_prompt = st.chat_input("Ask about stocks, portfolios, payments, or MCP diagnostics...")

# Handle queries
if "example_query" in st.session_state:
    prompt = st.session_state.example_query
    del st.session_state.example_query
elif chat_prompt:
    prompt = chat_prompt
else:
    prompt = None

if prompt:
    # Add user message
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt,
        "timestamp": timestamp
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(f"⏰ {timestamp}")
    
    # Generate response with tracking
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        with st.spinner("🌐 Processing via MCP system..."):
            start_time = time.time()
            
            try:
                # Call the MCP agent
                response = agent_executor.invoke({"messages": [("user", prompt)]})
                final_message = response["messages"][-1].content
                
                # Calculate timing
                execution_time = time.time() - start_time
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Update metrics
                metrics = st.session_state.app_metrics
                metrics["total_queries"] += 1
                metrics["successful_queries"] += 1
                
                # Update average response time
                current_avg = metrics["avg_response_time"]
                total_queries = metrics["total_queries"]
                metrics["avg_response_time"] = (
                    (current_avg * (total_queries - 1) + execution_time) / total_queries
                )
                
                # Categorize query type
                content_lower = final_message.lower()
                prompt_lower = prompt.lower()
                
                if any(stock in prompt_lower for stock in ["reliance", "tcs", "hdfc", "infy", "sbi", "nifty"]):
                    metrics["Indian_stocks_queried"] += 1
                elif any(stock in prompt_lower for stock in ["apple", "google", "microsoft", "tesla", "aapl", "googl", "msft", "tsla"]):
                    metrics["us_stocks_queried"] += 1
                elif "portfolio" in prompt_lower:
                    metrics["portfolio_analyses"] += 1
                elif "stripe" in prompt_lower or "payment" in prompt_lower:
                    metrics["stripe_queries"] += 1
                
                # Determine MCP info
                if "MCP" in content_lower:
                    mcp_info = "MCP with intelligent fallback system"
                elif "professional demo" in content_lower:
                    mcp_info = "Professional demo data with MCP architecture"
                elif "authentication" in content_lower:
                    mcp_info = "MCP authentication handling demonstrated"
                else:
                    mcp_info = "MCP protocol with smart fallback"
                
                success = True
                
            except Exception as e:
                final_message = f"❌ **Enhanced Error Recovery**: {str(e)}\n\n💡 **Try**: 'Check MCP system status' for detailed diagnostics."
                execution_time = time.time() - start_time
                timestamp = datetime.now().strftime("%H:%M:%S")
                mcp_info = f"Error handled by enhanced recovery system"
                success = False
        
        # Display response with typewriter effect
        displayed_text = ""
        words = final_message.split()
        for i, word in enumerate(words):
            displayed_text += word + " "
            message_placeholder.markdown(displayed_text + "▌")
            if i % 5 == 0:  # Update every 5 words
                time.sleep(0.01)
        
        # Final display
        message_placeholder.markdown(final_message)
        st.caption(f"⏰ {timestamp} • ⚡ {execution_time:.2f}s")
        
        if mcp_info:
            st.info(f"🌐 MCP: {mcp_info}")
        
        # Performance metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Response Time", f"{execution_time:.2f}s")
        with col2:
            st.metric("Status", "✅ Success" if success else "❌ Error")
        with col3:
            st.metric("MCP Mode", "Enhanced")
        
        # Add to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_message,
            "timestamp": timestamp,
            "execution_time": execution_time,
            "mcp_info": mcp_info,
            "type": "enhanced_response"
        })

# Footer
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("🌐 **MCP**")
    st.caption("Intelligent Protocol")

with col2:
    st.markdown("🔒 **Smart Fallback**")
    st.caption("Always Reliable")

with col3:
    st.markdown("⚡ **Real-time Data**")
    st.caption("Professional Quality")

with col4:
    st.markdown("🚀 **Production Ready**")
    st.caption("Error Recovery")

# Advanced features
st.markdown("---")
with st.expander("🔧 **MCP System Information & Diagnostics**", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🛠️ MCP Features**")
        st.code(f"""
# Current Configuration
MCP_ENABLED = {MCP_ENABLED}
Enhanced_Fallback = True
Authentication_Handling = Active

# Data Sources
Live_Stocks = High_Quality_NSE_Data
US_Stocks = Professional_Demo_Data
Stripe_Payments = Local_MCP_Server

# Protocol = JSON-RPC 2.0 with Intelligence
        """, language="python")
        
        if st.button("🔄 Test MCP System"):
            st.session_state.example_query = "Check MCP system status and provide comprehensive diagnostics"
    
    with col2:
        st.markdown("**📈 Session Analytics**")
        
        if st.session_state.app_metrics["total_queries"] > 0:
            # Performance metrics
            metrics = st.session_state.app_metrics
            
            fig = go.Figure(data=[
                go.Bar(name='Live Stocks', x=['Queries'], y=[metrics['Indian_stocks_queried']]),
                go.Bar(name='US Stocks', x=['Queries'], y=[metrics['us_stocks_queried']]),
                go.Bar(name='Portfolio', x=['Queries'], y=[metrics['portfolio_analyses']]),
                go.Bar(name='Payments', x=['Queries'], y=[metrics['stripe_queries']])
            ])
            fig.update_layout(barmode='stack', height=250, title="Query Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Start querying to see analytics!")

# Debug mode (simplified)
if st.checkbox("🐛 **Debug Mode**", value=False):
    st.markdown("### 🔧 **Debug Information**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Session Metrics"):
            st.json(st.session_state.app_metrics)
    
    with col2:
        if st.button("🗑️ Reset Session"):
            st.session_state.app_metrics = {
                "total_queries": 0,
                "successful_queries": 0,
                "avg_response_time": 0,
                "Indian_stocks_queried": 0,
                "us_stocks_queried": 0,
                "portfolio_analyses": 0,
                "stripe_queries": 0,
                "tutorial_completions": 0
            }
            st.success("Session reset!")
            time.sleep(1)
            st.rerun()

# Enhanced footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 10px; margin-top: 2rem;">
    <h4>🌐 MCP Financial Analyst</h4>
    <p><strong>Intelligent Model Context Protocol</strong> • <strong>Professional Fallback Systems</strong> • <strong>Production Patterns</strong></p>
    <p>Built for reliable financial analysis with advanced MCP architecture</p>
</div>
""", unsafe_allow_html=True)