#!/usr/bin/env python3
"""
Main entry point for the Gemini MCP Server
"""

import asyncio
import argparse
import sys
from pathlib import Path


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="MCP Server with Gemini Integration for AI second opinions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run server in current directory
  gemini-mcp-server
  
  # Run server with specific project root
  gemini-mcp-server --project-root /path/to/project
  
  # Show version
  gemini-mcp-server --version
        """,
    )

    parser.add_argument(
        "--project-root",
        type=str,
        default=".",
        help="Project root directory (default: current directory)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.0.1",
        help="Show version and exit",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to gemini-config.json file (default: <project-root>/gemini-config.json)",
    )

    args = parser.parse_args()

    # Import here to avoid circular imports
    from .server import MCPServer

    try:
        # Create and run server
        server = MCPServer(project_root=args.project_root)
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n✋ Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

