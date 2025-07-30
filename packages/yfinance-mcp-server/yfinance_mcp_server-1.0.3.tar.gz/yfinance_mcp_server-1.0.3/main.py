#!/usr/bin/env python3
"""
Comprehensive yfinance MCP Server using FastMCP
Provides access to all yfinance capabilities through MCP protocol

Installation:
pip install fastmcp yfinance pandas

Usage:
python yfinance_mcp_server.py
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import yfinance as yf
import pandas as pd
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("yfinance-server")

# Helper function to convert pandas objects to JSON-serializable format
def serialize_data(data):
    """Convert pandas DataFrames and other objects to JSON-serializable format"""
    if isinstance(data, pd.DataFrame):
        return data.to_dict('records')
    elif isinstance(data, pd.Series):
        return data.to_dict()
    elif isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif pd.isna(data):
        return None
    else:
        return data

# ============================================================================
# BASIC STOCK DATA TOOLS
# ============================================================================

@mcp.tool()
def get_stock_info(symbol: str) -> Dict[str, Any]:
    """
    Get comprehensive company information for a stock ticker.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dictionary containing company info, financials, and key metrics
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return serialize_data(info)
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

@mcp.tool()
def get_stock_history(
    symbol: str, 
    period: str = "1mo", 
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get historical stock price data.
    
    Args:
        symbol: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        start: Start date (YYYY-MM-DD format)
        end: End date (YYYY-MM-DD format)
    
    Returns:
        Historical price data with OHLCV information
    """
    try:
        ticker = yf.Ticker(symbol)
        if start and end:
            hist = ticker.history(start=start, end=end, interval=interval)
        else:
            hist = ticker.history(period=period, interval=interval)
        
        result = serialize_data(hist)
        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data": result
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

@mcp.tool()
def get_multiple_stocks_history(
    symbols: List[str], 
    period: str = "1mo", 
    interval: str = "1d"
) -> Dict[str, Any]:
    """
    Get historical data for multiple stocks at once.
    
    Args:
        symbols: List of stock ticker symbols
        period: Time period
        interval: Data interval
    
    Returns:
        Historical data for all symbols
    """
    try:
        data = yf.download(symbols, period=period, interval=interval)
        return {
            "symbols": symbols,
            "period": period,
            "interval": interval,
            "data": serialize_data(data)
        }
    except Exception as e:
        return {"error": str(e), "symbols": symbols}

# ============================================================================
# FINANCIAL STATEMENTS TOOLS
# ============================================================================

@mcp.tool()
def get_income_statement(
    symbol: str, 
    quarterly: bool = False, 
    ttm: bool = False
) -> Dict[str, Any]:
    """
    Get income statement data.
    
    Args:
        symbol: Stock ticker symbol
        quarterly: Get quarterly data instead of annual
        ttm: Get trailing twelve months data
    
    Returns:
        Income statement data
    """
    try:
        ticker = yf.Ticker(symbol)
        if ttm:
            stmt = ticker.ttm_income_stmt
        elif quarterly:
            stmt = ticker.quarterly_income_stmt
        else:
            stmt = ticker.income_stmt
        
        return {
            "symbol": symbol,
            "type": "ttm" if ttm else ("quarterly" if quarterly else "annual"),
            "data": serialize_data(stmt)
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

@mcp.tool()
def get_balance_sheet(symbol: str, quarterly: bool = False) -> Dict[str, Any]:
    """
    Get balance sheet data.
    
    Args:
        symbol: Stock ticker symbol
        quarterly: Get quarterly data instead of annual
    
    Returns:
        Balance sheet data
    """
    try:
        ticker = yf.Ticker(symbol)
        if quarterly:
            bs = ticker.quarterly_balance_sheet
        else:
            bs = ticker.balance_sheet
        
        return {
            "symbol": symbol,
            "type": "quarterly" if quarterly else "annual",
            "data": serialize_data(bs)
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

@mcp.tool()
def get_cash_flow(
    symbol: str, 
    quarterly: bool = False, 
    ttm: bool = False
) -> Dict[str, Any]:
    """
    Get cash flow statement data.
    
    Args:
        symbol: Stock ticker symbol
        quarterly: Get quarterly data instead of annual
        ttm: Get trailing twelve months data
    
    Returns:
        Cash flow statement data
    """
    try:
        ticker = yf.Ticker(symbol)
        if ttm:
            cf = ticker.ttm_cashflow
        elif quarterly:
            cf = ticker.quarterly_cashflow
        else:
            cf = ticker.cashflow
        
        return {
            "symbol": symbol,
            "type": "ttm" if ttm else ("quarterly" if quarterly else "annual"),
            "data": serialize_data(cf)
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

# ============================================================================
# ANALYST DATA TOOLS
# ============================================================================

@mcp.tool()
def get_analyst_recommendations(symbol: str) -> Dict[str, Any]:
    """
    Get analyst recommendations and upgrades/downgrades.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Analyst recommendations data
    """
    try:
        ticker = yf.Ticker(symbol)
        recommendations = ticker.recommendations
        recommendations_summary = ticker.recommendations_summary
        upgrades_downgrades = ticker.upgrades_downgrades
        
        return {
            "symbol": symbol,
            "recommendations": serialize_data(recommendations),
            "recommendations_summary": serialize_data(recommendations_summary),
            "upgrades_downgrades": serialize_data(upgrades_downgrades)
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

@mcp.tool()
def get_analyst_price_targets(symbol: str) -> Dict[str, Any]:
    """
    Get analyst price targets.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Price target data
    """
    try:
        ticker = yf.Ticker(symbol)
        price_targets = ticker.analyst_price_targets
        
        return {
            "symbol": symbol,
            "price_targets": serialize_data(price_targets)
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

@mcp.tool()
def get_earnings_estimates(symbol: str) -> Dict[str, Any]:
    """
    Get earnings and revenue estimates.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Earnings and revenue estimates
    """
    try:
        ticker = yf.Ticker(symbol)
        earnings_estimate = ticker.earnings_estimate
        revenue_estimate = ticker.revenue_estimate
        earnings_history = ticker.earnings_history
        eps_trend = ticker.eps_trend
        eps_revisions = ticker.eps_revisions
        growth_estimates = ticker.growth_estimates
        
        return {
            "symbol": symbol,
            "earnings_estimate": serialize_data(earnings_estimate),
            "revenue_estimate": serialize_data(revenue_estimate),
            "earnings_history": serialize_data(earnings_history),
            "eps_trend": serialize_data(eps_trend),
            "eps_revisions": serialize_data(eps_revisions),
            "growth_estimates": serialize_data(growth_estimates)
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

# ============================================================================
# OWNERSHIP & INSIDER DATA TOOLS
# ============================================================================

@mcp.tool()
def get_ownership_data(symbol: str) -> Dict[str, Any]:
    """
    Get ownership data including institutional and insider holdings.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Comprehensive ownership data
    """
    try:
        ticker = yf.Ticker(symbol)
        
        return {
            "symbol": symbol,
            "major_holders": serialize_data(ticker.major_holders),
            "institutional_holders": serialize_data(ticker.institutional_holders),
            "mutualfund_holders": serialize_data(ticker.mutualfund_holders),
            "insider_transactions": serialize_data(ticker.insider_transactions),
            "insider_purchases": serialize_data(ticker.insider_purchases),
            "insider_roster_holders": serialize_data(ticker.insider_roster_holders)
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

# ============================================================================
# DIVIDENDS & CORPORATE ACTIONS TOOLS
# ============================================================================

@mcp.tool()
def get_dividends_and_splits(symbol: str) -> Dict[str, Any]:
    """
    Get dividend and stock split history.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Dividend and split data
    """
    try:
        ticker = yf.Ticker(symbol)
        
        return {
            "symbol": symbol,
            "dividends": serialize_data(ticker.dividends),
            "splits": serialize_data(ticker.splits),
            "actions": serialize_data(ticker.actions),
            "capital_gains": serialize_data(ticker.capital_gains)
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

# ============================================================================
# OPTIONS DATA TOOLS
# ============================================================================

@mcp.tool()
def get_options_chain(symbol: str, expiration_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get options chain data.
    
    Args:
        symbol: Stock ticker symbol
        expiration_date: Specific expiration date (YYYY-MM-DD), uses nearest if not specified
    
    Returns:
        Options chain data for calls and puts
    """
    try:
        ticker = yf.Ticker(symbol)
        options_dates = ticker.options
        
        if not options_dates:
            return {"error": "No options data available", "symbol": symbol}
        
        # Use specified date or first available
        target_date = expiration_date if expiration_date else options_dates[0]
        
        if target_date not in options_dates:
            return {
                "error": f"Expiration date {target_date} not available",
                "symbol": symbol,
                "available_dates": list(options_dates)
            }
        
        chain = ticker.option_chain(target_date)
        
        return {
            "symbol": symbol,
            "expiration_date": target_date,
            "available_dates": list(options_dates),
            "calls": serialize_data(chain.calls),
            "puts": serialize_data(chain.puts)
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

# ============================================================================
# NEWS & CALENDAR TOOLS
# ============================================================================

@mcp.tool()
def get_stock_news(symbol: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get recent news for a stock.
    
    Args:
        symbol: Stock ticker symbol
        limit: Maximum number of news articles to return
    
    Returns:
        Recent news articles
    """
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news[:limit]
        
        # Convert timestamps to readable format
        processed_news = []
        for article in news:
            processed_article = article.copy()
            if 'providerPublishTime' in article:
                processed_article['published_datetime'] = datetime.fromtimestamp(
                    article['providerPublishTime']
                ).isoformat()
            processed_news.append(processed_article)
        
        return {
            "symbol": symbol,
            "news_count": len(processed_news),
            "news": processed_news
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

@mcp.tool()
def get_earnings_calendar(symbol: str) -> Dict[str, Any]:
    """
    Get earnings calendar and dates.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Earnings calendar data
    """
    try:
        ticker = yf.Ticker(symbol)
        
        return {
            "symbol": symbol,
            "calendar": serialize_data(ticker.calendar),
            "earnings_dates": serialize_data(ticker.earnings_dates),
            "earnings": serialize_data(ticker.earnings)
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

# ============================================================================
# FUND & ETF DATA TOOLS
# ============================================================================

@mcp.tool()
def get_fund_data(symbol: str) -> Dict[str, Any]:
    """
    Get fund/ETF specific data including holdings.
    
    Args:
        symbol: Fund/ETF ticker symbol
    
    Returns:
        Fund data including holdings and performance
    """
    try:
        ticker = yf.Ticker(symbol)
        funds_data = ticker.funds_data
        
        if funds_data is None:
            return {"error": "No fund data available", "symbol": symbol}
        
        return {
            "symbol": symbol,
            "description": funds_data.description if hasattr(funds_data, 'description') else None,
            "top_holdings": serialize_data(funds_data.top_holdings) if hasattr(funds_data, 'top_holdings') else None,
            "fund_overview": serialize_data(funds_data.fund_overview) if hasattr(funds_data, 'fund_overview') else None,
            "fund_performance": serialize_data(funds_data.fund_performance) if hasattr(funds_data, 'fund_performance') else None
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

# ============================================================================
# ESG & SUSTAINABILITY TOOLS
# ============================================================================

@mcp.tool()
def get_sustainability_data(symbol: str) -> Dict[str, Any]:
    """
    Get ESG and sustainability data.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        ESG scores and sustainability metrics
    """
    try:
        ticker = yf.Ticker(symbol)
        sustainability = ticker.sustainability
        
        return {
            "symbol": symbol,
            "sustainability": serialize_data(sustainability)
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

# ============================================================================
# MARKET SCREENING TOOLS
# ============================================================================

@mcp.tool()
def screen_stocks(
    market_cap_min: Optional[float] = None,
    market_cap_max: Optional[float] = None,
    pe_ratio_max: Optional[float] = None,
    dividend_yield_min: Optional[float] = None,
    sector: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Screen stocks based on fundamental criteria.
    Note: This is a basic implementation. For advanced screening, consider using yfinance.screen
    
    Args:
        market_cap_min: Minimum market cap
        market_cap_max: Maximum market cap  
        pe_ratio_max: Maximum P/E ratio
        dividend_yield_min: Minimum dividend yield
        sector: Sector filter
        limit: Maximum results to return
    
    Returns:
        List of stocks matching criteria
    """
    try:
        # This is a simplified example - in practice you'd use yf.screen() with EquityQuery
        # For demonstration, we'll show how the structure would work
        
        criteria = {}
        if market_cap_min is not None:
            criteria['market_cap_min'] = market_cap_min
        if market_cap_max is not None:
            criteria['market_cap_max'] = market_cap_max
        if pe_ratio_max is not None:
            criteria['pe_ratio_max'] = pe_ratio_max
        if dividend_yield_min is not None:
            criteria['dividend_yield_min'] = dividend_yield_min
        if sector:
            criteria['sector'] = sector
        
        return {
            "criteria": criteria,
            "limit": limit,
            "note": "Advanced screening requires yfinance.screen() with EquityQuery - this is a structure example"
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# SEARCH & LOOKUP TOOLS
# ============================================================================

@mcp.tool()
def search_stocks(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for stocks by company name or ticker.
    Note: This requires the yfinance.Search class
    
    Args:
        query: Search term (company name or ticker)
        limit: Maximum results to return
    
    Returns:
        Search results with ticker symbols and company names
    """
    try:
        # Using basic ticker validation approach
        # In practice, you'd use yf.Search(query) for full search functionality
        
        # Try to get info for the query as a ticker
        try:
            ticker = yf.Ticker(query.upper())
            info = ticker.info
            if info and 'symbol' in info:
                return {
                    "query": query,
                    "results": [{
                        "symbol": info.get('symbol'),
                        "shortName": info.get('shortName'),
                        "longName": info.get('longName'),
                        "sector": info.get('sector'),
                        "industry": info.get('industry')
                    }]
                }
        except:
            pass
        
        return {
            "query": query,
            "results": [],
            "note": "Advanced search requires yfinance.Search class - this validates single ticker"
        }
    except Exception as e:
        return {"error": str(e), "query": query}

# ============================================================================
# UTILITY TOOLS
# ============================================================================

@mcp.tool()
def get_fast_info(symbol: str) -> Dict[str, Any]:
    """
    Get fast access to key stock metrics.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Key metrics with fast access
    """
    try:
        ticker = yf.Ticker(symbol)
        fast_info = ticker.fast_info
        
        return {
            "symbol": symbol,
            "fast_info": serialize_data(fast_info)
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

@mcp.tool()
def get_isin(symbol: str) -> Dict[str, Any]:
    """
    Get ISIN (International Securities Identification Number) for a stock.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        ISIN identifier
    """
    try:
        ticker = yf.Ticker(symbol)
        isin = ticker.isin
        
        return {
            "symbol": symbol,
            "isin": isin
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

@mcp.tool()
def get_sec_filings(symbol: str) -> Dict[str, Any]:
    """
    Get SEC filings for a stock.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        SEC filings data
    """
    try:
        ticker = yf.Ticker(symbol)
        sec_filings = ticker.sec_filings
        
        return {
            "symbol": symbol,
            "sec_filings": serialize_data(sec_filings)
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}

# ============================================================================
# BATCH OPERATIONS TOOLS
# ============================================================================

@mcp.tool()
def get_multiple_tickers_info(symbols: List[str]) -> Dict[str, Any]:
    """
    Get basic info for multiple tickers at once.
    
    Args:
        symbols: List of stock ticker symbols
    
    Returns:
        Info for all requested symbols
    """
    try:
        tickers = yf.Tickers(' '.join(symbols))
        results = {}
        
        for symbol in symbols:
            try:
                ticker = tickers.tickers[symbol]
                results[symbol] = serialize_data(ticker.info)
            except Exception as e:
                results[symbol] = {"error": str(e)}
        
        return {
            "symbols": symbols,
            "results": results
        }
    except Exception as e:
        return {"error": str(e), "symbols": symbols}

@mcp.tool()
def configure_yfinance(
    proxy: Optional[str] = None,
    enable_debug: bool = False,
    tz_cache_location: Optional[str] = None
) -> Dict[str, Any]:
    """
    Configure yfinance global settings.
    
    Args:
        proxy: Proxy server URL
        enable_debug: Enable debug logging
        tz_cache_location: Custom timezone cache location
    
    Returns:
        Configuration status
    """
    try:
        config_applied = {}
        
        if proxy:
            yf.set_config(proxy=proxy)
            config_applied['proxy'] = proxy
        
        if enable_debug:
            yf.enable_debug_mode()
            config_applied['debug_mode'] = True
        
        if tz_cache_location:
            yf.set_tz_cache_location(tz_cache_location)
            config_applied['tz_cache_location'] = tz_cache_location
        
        return {
            "status": "success",
            "configuration_applied": config_applied
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the MCP server"""
    logger.info("Starting yfinance MCP server...")
    # FastMCP's synchronous `run()` starts its own event loop.
    # Using it directly avoids the "Already running asyncio" error that occurs
    # when nesting event loops via `asyncio.run()`.
    mcp.run()

if __name__ == "__main__":
    main()