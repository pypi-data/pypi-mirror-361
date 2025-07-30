from .server import main as async_main
import asyncio

def main():
    """Entry point that handles the async main function."""
    asyncio.run(async_main())

# Optionally expose other important items at package level
__all__ = ['main']