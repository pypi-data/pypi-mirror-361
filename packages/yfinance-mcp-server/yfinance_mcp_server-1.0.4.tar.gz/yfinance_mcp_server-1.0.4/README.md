# YFinance MCP Server

A fully-featured **Model Context Protocol (MCP)** server that exposes nearly all of Yahoo Finance’s capabilities through simple, typed MCP tools.  
Built with [FastMCP](https://gofastmcp.com) so you can plug it straight into any LLM workflow, agent framework, or the official MCP client SDK.

---

## Features

* 25+ tools covering:
  * Price history (single & multiple tickers)
  * Financial statements (income, balance sheet, cash-flow)
  * Analyst data (recommendations, price targets, earnings estimates)
  * Ownership & insider transactions
  * Dividends, splits & actions
  * Options chains
  * News & earnings calendar
  * Fund / ETF holdings
  * ESG & sustainability metrics
  * Stock screeners & search utilities
  * Batch operations & yfinance global configuration
* Pure-Python, zero external services required.
* Exposes both **STDIO** (default) and **HTTP/SSE** transports if you want to serve over the network.

---

## Requirements

* Python 3.10+
* **pipx** (for MCP client integration)

All dependencies are listed in `requirements.txt` (generated below).

```
pandas
yfinance
fastmcp
```

> If you already installed packages manually you can skip the next step.

### Installing pipx

If you don't have pipx installed, install it first:

**macOS:**
```bash
brew install pipx
```

**Linux/Ubuntu:**
```bash
sudo apt install pipx
# or
python3 -m pip install --user pipx
```

**Windows:**
```bash
python -m pip install --user pipx
```

After installation, ensure pipx is in your PATH:
```bash
pipx ensurepath
```

---

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install yfinance-mcp-server
```

### Option 2: Install from source

```bash
# 1) Clone the repository
git clone https://github.com/itsmejay80/yfinance-mcp-server.git
cd yfinance-mcp-server

# 2) (Optional) create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt
```

---

## Running the server

### If installed from PyPI:
```bash
yfinance-mcp-server
```

### If running from source:
```bash
python main.py
```

You should see a FastMCP banner like:

```
╭─ FastMCP 2.0 ─────────────────────────╮
│ 🖥️  Server name:     yfinance-server   │
│ 📦 Transport:       STDIO             │
│ …                                     │
╰───────────────────────────────────────╯
```

The server listens on **STDIO** by default (perfect for embedding inside other processes).  
To expose an HTTP endpoint instead:

```python
from fastmcp import FastMCP
from main import mcp  # reuse the configured server

if __name__ == "__main__":
    # Starts an HTTP server on http://0.0.0.0:8000
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

---

## Configuration for MCP Clients

### Cursor IDE

Add this to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "yfinance": {
      "command": "pipx",
      "args": [
        "run",
        "yfinance-mcp-server"
      ]
    }
  }
}
```

### Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "yfinance": {
      "command": "pipx",
      "args": [
        "run",
        "yfinance-mcp-server"
      ]
    }
  }
}
```

### Custom Configuration

If you installed from source or need custom paths:

```json
{
  "mcpServers": {
    "yfinance-server": {
      "command": "python",
      "args": ["/path/to/yfinance-mcp-server/main.py"],
      "cwd": "/path/to/yfinance-mcp-server"
    }
  }
}
```

---

## Consuming the tools

### From Python using the FastMCP client

```python
from fastmcp import FastMCPClient

client = FastMCPClient("http://localhost:8000")

# List available tools
for tool in client.list_tools():
    print(tool.name, "->", tool.description)

# Call a tool
resp = client.call_tool("get_stock_history", {
    "symbol": "AAPL",
    "period": "6mo",
    "interval": "1d"
})
print(resp)
```

### From the command line (stdio)

You can pipe JSON-RPC requests into the running process; most users will instead let an agent framework manage this. See FastMCP docs for details.

---

## Project structure

```text
MCPWorld/
├── main.py          # all tool definitions + entrypoint
├── requirements.txt # dependency list
└── README.md        # you are here
```

---

## Deployment

The server is self-contained—any platform that can run Python can host it.  
For one-command deployment, check out [FastMCP Cloud](https://fastmcp.cloud).

---

## License

This project is licensed under the MIT License (see `LICENSE` file, if included). Feel free to adapt or extend.
