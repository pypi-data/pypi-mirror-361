import argparse
from .server import mcp

def main():
    """MCP Stock: Return stock prices."""
    parser = argparse.ArgumentParser(
        description="Gives you the ability to return stock price for a given symbol/ticker"
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()