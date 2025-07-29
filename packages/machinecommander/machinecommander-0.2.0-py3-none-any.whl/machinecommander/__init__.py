from . import mcp_server

def main():
    """Main entry point for the package."""
    mcp_server.main()

# Optionally expose other important items at package level
__all__ = ['main']