"""Main entry point for GIS MCP Server."""

import asyncio
import logging

from src.gis_mcp_server.server import main as server_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        asyncio.run(server_main())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
