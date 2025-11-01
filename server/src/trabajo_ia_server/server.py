"""
Trabajo IA MCP Server - Main server implementation.

FastMCP server providing FRED data access through MCP protocol.
"""
from typing import Optional
import sys

from mcp.server.fastmcp import FastMCP

from trabajo_ia_server.config import config
from trabajo_ia_server.tools.fred.fetch_series import fetch_series_observations
from trabajo_ia_server.utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize FastMCP server
mcp = FastMCP(config.SERVER_NAME)


@mcp.tool("fetch_fred_series")
def fetch_fred_series(
    series_id: str,
    observation_start: Optional[str] = None,
    observation_end: Optional[str] = None
) -> str:
    """
    Fetch historical observations for a FRED economic data series.

    This tool retrieves time-series data from the Federal Reserve Economic Data (FRED)
    database maintained by the Federal Reserve Bank of St. Louis.

    Args:
        series_id: FRED series identifier (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')
            - GDP: Gross Domestic Product
            - UNRATE: Unemployment Rate
            - CPIAUCSL: Consumer Price Index
        observation_start: Start date in 'YYYY-MM-DD' format (optional)
        observation_end: End date in 'YYYY-MM-DD' format (optional)

    Returns:
        JSON string containing:
        - data: List of observations with date and value
        - metadata: Information about the fetch (dates, counts, ranges)

    Examples:
        >>> fetch_fred_series("GDP")
        >>> fetch_fred_series("UNRATE", "2020-01-01", "2023-12-31")
    """
    logger.info(f"Fetching FRED series: {series_id}")
    return fetch_series_observations(series_id, observation_start, observation_end)


def main():
    """
    Main entry point for the MCP server.

    Validates configuration and starts the FastMCP server with stdio transport.
    """
    try:
        # Validate configuration before starting
        config.validate()
        logger.info(f"Starting {config.SERVER_NAME} v{config.SERVER_VERSION}")

        # Run server with stdio transport
        mcp.run(transport='stdio')

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
