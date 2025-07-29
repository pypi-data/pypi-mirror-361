"""
Gemini MCP Server - MCP Server with Google Gemini CLI integration
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .gemini_integration import GeminiIntegration, get_integration
from .server import MCPServer

__all__ = ["GeminiIntegration", "get_integration", "MCPServer"]