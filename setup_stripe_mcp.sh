#!/bin/bash

# Setup script for Stripe MCP Server
# This script helps you start the local Stripe MCP server for the AI Financial Analyst

echo "🚀 Setting up Stripe MCP Server for AI Financial Analyst"
echo "================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys."
    exit 1
fi

# Load environment variables
source .env

# Check if Stripe secret key is set
if [ -z "$STRIPE_SECRET_KEY" ]; then
    echo "❌ Error: STRIPE_SECRET_KEY not found in .env file!"
    echo "Please add your Stripe secret key to the .env file:"
    echo "STRIPE_SECRET_KEY=\"sk_test_...\""
    exit 1
fi

echo "✅ Found Stripe secret key: ${STRIPE_SECRET_KEY:0:12}..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed!"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js is installed: $(node --version)"

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo "❌ Error: npx is not available!"
    echo "Please install npm/npx or update your Node.js installation."
    exit 1
fi

echo "✅ npx is available"

# Start the Stripe MCP server
echo "🔄 Starting Stripe MCP server on http://localhost:3000..."
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Stripe MCP server with MCP Inspector for HTTP mode
# This enables HTTP access on port 3000 instead of stdio mode
echo "📡 Using MCP Inspector for HTTP transport..."
npx @modelcontextprotocol/inspector npx -y @stripe/mcp --tools=all --api-key="$STRIPE_SECRET_KEY"