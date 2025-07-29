# open-stocks-mcp

**🚧 UNDER CONSTRUCTION 🚧**

An MCP (Model Context Protocol) server providing access to stock market data through open-source APIs like Robin Stocks.

## Project Intent

This project aims to create a standardized interface for LLM applications to access stock market data, portfolio information, and trading capabilities through the Model Context Protocol.

### Planned Features
- Real-time stock price data
- Portfolio management tools  
- Market analysis capabilities
- Historical data access
- Trading alerts and notifications

## Status

- ✅ **Foundation**: MCP server scaffolding complete
- ✅ **Infrastructure**: CI/CD, testing, and publishing pipeline established
- ✅ **Package**: Published to PyPI as `open-stocks-mcp` (v0.3.0)
- ✅ **Authentication**: Robin Stocks authentication with device verification support
- ✅ **Containerization**: Production-ready Docker deployment with security features
- ✅ **Communication**: Server/client MCP communication verified working
- ✅ **Core Tools**: 56 MCP tools implemented across 10 categories
- ✅ **Advanced Data**: Market intelligence, dividend tracking, and system monitoring
- ✅ **Phase 3**: Options trading, watchlist management, account features, and user profiles
- 📋 **Next**: Trading capabilities and order placement

## Installation

Install the Open Stocks MCP server via pip:

```bash
pip install open-stocks-mcp
```

For development installation from source:

```bash
git clone https://github.com/Open-Agent-Tools/open-stocks-mcp.git
cd open-stocks-mcp
uv pip install -e .
```

## Credential Management

The Open Stocks MCP server uses Robin Stocks for market data access, which requires Robinhood account credentials.

### Setting Up Credentials

1. Create a `.env` file in your project root:

```bash
ROBINHOOD_USERNAME=your_email@example.com
ROBINHOOD_PASSWORD=your_password
```

2. Secure your credentials:
   - Never commit the `.env` file to version control
   - Ensure proper file permissions: `chmod 600 .env`
   - Consider using a password manager or secure credential storage

### Device Verification and MFA

The Open Stocks MCP server includes enhanced authentication that handles Robinhood's device verification requirements:

**Device Verification Process:**
- When logging in for the first time, Robinhood may require device verification
- Check your Robinhood mobile app for verification prompts
- Approve the device when prompted
- The server will automatically handle the verification workflow

**Multi-Factor Authentication (MFA):**
- If your account has MFA enabled, you'll receive a push notification in the Robinhood mobile app
- Keep your mobile app accessible during the login process
- The server supports both SMS and app-based verification methods

**Troubleshooting Authentication:**
- **"Device verification required"**: Check your mobile app and approve the device
- **"Interactive verification required"**: Ensure you have access to your mobile device
- **Session persistence**: Authentication sessions are cached to reduce verification frequency

## Starting the MCP Server Locally

### Via Command Line

Start the server in stdio transport mode (for MCP clients):

```bash
# Using the installed package
open-stocks-mcp-server --transport stdio

# For development with auto-reload
uv run open-stocks-mcp-server --transport stdio
```

### Testing the Server

Use the MCP Inspector for interactive testing:

```bash
# Run the inspector with the server (mcp CLI required)
uv run mcp dev src/open_stocks_mcp/server/app.py
```

Note: The `mcp` command is installed with the `mcp[cli]` package dependency.

## Adding the MCP Client to an ADK Agent

To integrate Open Stocks MCP with your ADK (Agent Development Kit) agent:

### 1. Update MCP Settings

Add the server to your MCP settings configuration (typically in `mcp_settings.json` or similar):

```json
{
  "mcpServers": {
    "open-stocks": {
      "command": "open-stocks-mcp-server",
      "args": ["--transport", "stdio"],
      "env": {}
    }
  }
}
```

### 2. Claude Desktop Integration

For Claude Desktop app, add to your configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "open-stocks": {
      "command": "open-stocks-mcp-server",
      "args": ["--transport", "stdio"]
    }
  }
}
```


### 3. Available Tools

Once connected, your agent will have access to 56 MCP tools across 10 categories:

**Account Management (8 tools):**
- `account_info` - Gets basic Robinhood account information
- `account_details` - Gets comprehensive account details including buying power and cash balances
- `portfolio` - Portfolio holdings and values
- `positions` - Current stock positions
- `portfolio_history` - Historical portfolio performance
- `build_holdings` - Comprehensive holdings with dividend information and performance metrics
- `build_user_profile` - Complete financial profile with equity, cash, and dividend totals
- `day_trades` - Pattern day trading tracking and buying power information

**Order Management (2 tools):**
- `stock_orders` - Stock order history and status
- `options_orders` - Options order history

**Stock Market Data (5 tools):**
- `stock_price` - Real-time stock prices
- `stock_info` - Company fundamentals
- `search_stocks_tool` - Search for stocks by symbol/name
- `market_hours` - Market status and hours
- `price_history` - Historical price data

**Advanced Market Data (10 tools):**
- `top_movers_sp500` - S&P 500 top movers
- `top_100_stocks` - Most popular stocks
- `top_movers` - Top 20 overall movers
- `stocks_by_tag` - Stocks by category (tech, biotech, etc.)
- `stock_ratings` - Analyst ratings
- `stock_earnings` - Earnings reports
- `stock_news` - Latest news stories
- `stock_splits` - Stock split history
- `stock_events` - Corporate events
- `stock_level2_data` - Level II market data (Gold)

**Dividend & Income (5 tools):**
- `dividends` - Complete dividend history
- `total_dividends` - Total dividends with yearly breakdown
- `dividends_by_instrument` - Dividends for specific stocks
- `interest_payments` - Interest from cash management
- `stock_loan_payments` - Stock lending income

**Options Trading (7 tools):**
- `options_chains` - Complete option chains for stocks
- `find_options` - Search tradable options with filters
- `option_market_data` - Greeks, open interest, and market data
- `option_historicals` - Historical option price data
- `aggregate_option_positions` - Aggregated positions by stock
- `all_option_positions` - All option positions ever held
- `open_option_positions` - Currently open option positions

**Watchlist Management (5 tools):**
- `all_watchlists` - All user-created watchlists
- `watchlist_by_name` - Contents of specific watchlist
- `add_to_watchlist` - Add symbols to watchlist
- `remove_from_watchlist` - Remove symbols from watchlist
- `watchlist_performance` - Performance metrics for watchlist

**Account Features & Notifications (7 tools):**
- `notifications` - Account notifications and alerts
- `latest_notification` - Most recent notification
- `margin_calls` - Margin call information
- `margin_interest` - Margin interest charges
- `subscription_fees` - Robinhood Gold fees
- `referrals` - Referral program information
- `account_features` - Comprehensive account features

**User Profile Management (7 tools):**
- `account_profile` - Trading account configuration
- `basic_profile` - Basic user information
- `investment_profile` - Risk assessment and objectives
- `security_profile` - Security settings
- `user_profile` - Comprehensive user profile
- `complete_profile` - Combined profile data
- `account_settings` - Account preferences

**System Tools (5 tools):**
- `list_tools` - List all available tools
- `session_status` - Authentication status
- `rate_limit_status` - Rate limiting information
- `metrics_summary` - Performance metrics
- `health_check` - System health status

## Docker Deployment

The Open Stocks MCP server includes production-ready Docker containerization with enhanced security features.

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/Open-Agent-Tools/open-stocks-mcp.git
cd open-stocks-mcp/examples/Docker

# Create credentials file
cp .env.example .env
# Edit .env with your Robinhood credentials

# Start the server
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop the server
docker-compose down
```

### Docker Features

**Security:**
- Non-root user execution (UID 1001)
- Health checks with automatic restart
- Resource limits and reservations
- Environment variable isolation

**Production Ready:**
- Automatic session persistence
- Device verification handling
- Comprehensive logging
- Port exposure (3001) for MCP clients

**See the [Docker Example README](examples/Docker/README.md) for complete documentation.**

## Current Functionality (v0.3.0)

### Enhanced Authentication System
- **Device Verification**: Automatic handling of Robinhood device verification workflows
- **Environment-based login**: Secure credential storage via `.env` files
- **Session persistence**: Cached authentication sessions to reduce verification frequency
- **MFA Support**: Full support for SMS, email, and mobile app verification methods
- **Error handling**: Intelligent error classification and user guidance

### Robin Stocks Integration
- **56 MCP Tools**: Complete suite of account, market data, options trading, watchlist management, and user profile tools
- **Async Support**: Non-blocking API calls using asyncio
- **Rate limiting**: Built-in protection against API rate limits
- **Error recovery**: Automatic session refresh and retry logic
- **Advanced Market Data**: S&P 500 movers, market intelligence, and analyst ratings
- **Income Tracking**: Comprehensive dividend and interest payment analysis
- **Portfolio Analytics**: Advanced holdings analysis with dividend information and day trading tracking
- **Options Trading**: Complete options chain analysis, market data, and position tracking
- **Watchlist Management**: Create and manage custom watchlists with performance tracking
- **Account Features**: Notifications, margin calls, subscription fees, and referral information
- **User Profiles**: Complete user profile management with security and investment preferences

## Testing

### Basic Tests
Run the basic test suite:

```bash
uv run pytest
```

### Login Flow Integration Tests
Test the complete login flow with real credentials from `.env`:

```bash
# Run all tests including integration tests
uv run pytest -m integration

# Run specific login flow tests
uv run pytest tests/test_server_login_flow.py -v

# Run without integration tests (no credentials needed)
uv run pytest -m "not integration"
```

**Note**: Integration tests require valid `ROBINHOOD_USERNAME` and `ROBINHOOD_PASSWORD` in your `.env` file. These tests mock the actual Robin Stocks API calls to avoid real authentication attempts.

### Test Categories
- **Unit tests**: Basic functionality without external dependencies
- **Integration tests**: Login flow tests using real credentials (but mocked API calls)
- **Slow tests**: Performance and stress tests (marked with `@pytest.mark.slow`)

For development with auto-reloading:

```bash
uv run pytest --watch
```

## License

Apache License 2.0 - see LICENSE file for details.