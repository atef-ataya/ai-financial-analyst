# 🤖 AI Financial Analyst

This project is an AI-powered financial analyst built with Python and LangGraph. The agent connects to real-world financial services to answer questions about stock market data and business revenue. 

## ✨ Features

- **Dual-Tool Integration:** Connects to two independent services:
  - **Alpha Vantage:** For real-time stock price data for publicly traded companies.
  - **Stripe:** For business revenue data, such as recent charges and payments.
- **Intelligent Tool Use:** Uses LangGraph to create a ReAct-style agent that can analyze a user's question and choose the correct tool to answer it.
- **Interactive UI:** A simple and clean user interface built with Streamlit for easy interaction.

## 🛠️ Tech Stack

- **Agent Framework:** LangGraph & LangChain
- **LLM:** OpenAI's GPT-4o
- **Web UI:** Streamlit
- **Financial APIs:** Alpha Vantage (Stocks), Stripe (Payments)
- **Language:** Python

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### 1. Prerequisites

- Python 3.9+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- An [Alpha Vantage API key](https://www.alphavantage.co/support/#api-key)
- A [Stripe account](https://dashboard.stripe.com/register) and its secret API key.

### 2. Installation

First, clone the repository to your local machine:

```bash
git clone [https://github.com/YourUsername/ai-financial-analyst.git](https://github.com/YourUsername/ai-financial-analyst.git)
cd ai-financial-analyst
```
