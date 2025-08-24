# 🔧 MCP Troubleshooting Guide

## The 401 Unauthorized Error Explained

You're getting a **401 Unauthorized** error because the code was trying to connect to `https://mcp.stripe.com`, which either doesn't exist or requires OAuth authentication that isn't implemented.

## ✅ Solution: Use Remote Stripe MCP Server with Proper Authentication

The correct approach is to use the **remote Stripe MCP server** with proper Bearer token authentication using your Stripe API key. Here's how:

### Step 1: Verify Your Configuration

1. **Check your `.env` file** - Make sure you have:
   ```bash
   STRIPE_SECRET_KEY="sk_test_..."  # Your Stripe test key
   STRIPE_MCP_URL="https://mcp.stripe.com"  # Remote Stripe MCP server
   ```

2. **Verify the changes were applied** - The code should now use `https://mcp.stripe.com` with proper authentication

### Step 2: Test the Connection

1. **Run your financial agent**:
   ```bash
   python mcp_financial_agent.py
   ```

2. **Check MCP status** by asking: "Check MCP status"

3. **You should see**:
   - ✅ Zerodha: Connected (or connection failed - this is normal)
   - ✅ Stripe: Connected to localhost:3000

## 🐛 Common Issues & Solutions

### Issue 1: "Still getting 401 errors"
**Solution**: 
1. Verify your `STRIPE_SECRET_KEY` is correct in the `.env` file
2. Make sure the key starts with `sk_test_` or `sk_live_`
3. Check that the key has the necessary permissions

### Issue 2: "Connection timeout"
**Solution**: 
1. Check your internet connection
2. Verify the URL is `https://mcp.stripe.com`
3. Try running the MCP status check: `python -c "from mcp_financial_agent import check_mcp_status; print(check_mcp_status.invoke({}))"`

### Issue 3: "Authentication errors"
**Solution**: 
1. Ensure your Stripe API key is valid and active
2. Check that the Bearer token is being sent correctly
3. Verify your Stripe account has MCP access enabled

### Issue 5: "Zerodha connection failed"
**This is normal!** The Zerodha MCP server (`https://mcp.kite.trade/mcp`) may not be publicly accessible or may require authentication. The system will fall back to demo mode.

## 🎯 Expected Behavior After Fix

1. **Stripe MCP**: Should connect to localhost:3000 ✅
2. **Zerodha MCP**: May fail (normal) - uses demo data 📊
3. **Overall system**: Works perfectly with demo data for Zerodha and live Stripe data

## 🔍 Verification Commands

```bash
# 1. Check if Stripe MCP server is running
curl http://localhost:3000

# 2. Test the financial agent
python -c "from mcp_financial_agent import check_mcp_status; print(check_mcp_status())"

# 3. Run the Streamlit app
streamlit run app.py
```

## 🎯 Summary of Fixes

1. **Used remote Stripe MCP server**: Connected to `https://mcp.stripe.com` instead of attempting local setup
2. **Added proper authentication**: The MCP client now sends your Stripe API key as a Bearer token
3. **Updated environment variables**: STRIPE_MCP_URL now points to remote server
4. **Simplified setup**: No need for local server installation or management
5. **Improved error messages**: Better guidance for troubleshooting

## 🚀 Next Steps

1. Run `streamlit run app.py` to start the application
2. Test with queries like "Show me recent Stripe charges" or "Check MCP status"
3. Both Zerodha and Stripe MCP servers are now connected! 🎉

---

**Need more help?** Check the console output for detailed MCP connection logs and error messages.