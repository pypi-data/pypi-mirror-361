import sys
from .server import mcp, get_image_provider, logger


def main():
    try:
        provider = get_image_provider()
        logger.info(f"Starting {provider.get_name()} Image Generator MCP server...")
        logger.info(f"Available capabilities:")
        logger.info(f"  - Image generation: {provider.supports_generation()}")
        logger.info(f"  - Image transformation: {provider.supports_transformation()}")
    except Exception as e:
        logger.error(f"Failed to initialize provider: {e}")
        sys.exit(1)
    
    mcp.run(transport="stdio")
    logger.info("Server stopped")