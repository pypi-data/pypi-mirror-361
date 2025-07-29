# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server implementation that integrates Google's Gemini CLI to provide AI second opinions and validation within development workflows. The integration allows for automatic consultation with Gemini when uncertainty is detected or when explicitly requested.

## Common Commands

### Setup and Installation
```bash
# Install and setup Gemini CLI integration
bash setup-gemini-integration.sh

# Authenticate with Gemini (run once interactively)
gemini
```

### Running the MCP Server

#### Using uvx (Recommended - no installation needed)
```bash
# Run directly with uvx
uvx gemini-mcp-server

# Run with specific project root
uvx gemini-mcp-server --project-root /path/to/project

# Show help
uvx gemini-mcp-server --help
```

#### Local Development
```bash
# Install package in development mode
uv pip install -e .

# Run the server
gemini-mcp-server --project-root .
```

### Testing Gemini CLI
```bash
# Test Gemini CLI directly
gemini -p "Your query here"
gemini -m gemini-2.5-flash -p "Query with specific model"
```

## Architecture

### Package Structure

The project is now packaged as a Python module that can be run with `uvx`:

```
gemini-mcp-server/
├── gemini_mcp/
│   ├── __init__.py             # Package initialization
│   ├── __main__.py             # CLI entry point
│   ├── gemini_integration.py   # Gemini integration logic
│   └── server.py               # MCP server implementation
├── pyproject.toml              # Package configuration for uv/pip
├── README.md                   # User documentation
└── CLAUDE.md                   # This file
```

### Core Components

**gemini_mcp/gemini_integration.py**
- `GeminiIntegration` class: Main integration handler with singleton pattern
- Automatic uncertainty detection through regex patterns
- Rate limiting and timeout management
- Consultation logging and statistics tracking
- Support for both structured comparison mode and simple queries

**gemini_mcp/server.py**
- `MCPServer` class: MCP server implementation
- Exposes three tools:
  - `consult_gemini`: Get second opinions from Gemini
  - `gemini_status`: Check integration status and statistics
  - `toggle_gemini_auto_consult`: Enable/disable automatic consultation
- Configuration loading from file and environment variables

**gemini_mcp/__main__.py**
- CLI entry point for the package
- Argument parsing and server initialization
- Enables `uvx gemini-mcp-server` and `python -m gemini_mcp` usage

### Configuration

Configuration is managed through `gemini-config.json` with environment variable overrides:
- `GEMINI_ENABLED`: Enable/disable integration
- `GEMINI_AUTO_CONSULT`: Auto-consultation on uncertainty detection
- `GEMINI_CLI_COMMAND`: CLI command (default: "gemini")
- `GEMINI_TIMEOUT`: Command timeout in seconds
- `GEMINI_RATE_LIMIT`: Delay between consultations
- `GEMINI_MODEL`: Model to use (default: "gemini-2.5-flash")

### Key Design Patterns

1. **Singleton Pattern**: The `get_integration()` function ensures a single instance across all tool calls for consistent rate limiting and state management.

2. **Uncertainty Detection**: Three categories of patterns trigger automatic consultation:
   - Uncertainty patterns (e.g., "I'm not sure", "possibly")
   - Complex decision patterns (e.g., "multiple approaches", "trade-offs")
   - Critical operation patterns (e.g., "production", "security")

3. **Structured Query Format**: Consultations can include context and request structured responses with analysis, recommendations, concerns, and alternatives.

## Development Tips

- The MCP server uses asyncio for handling concurrent operations
- Rate limiting is enforced globally through the singleton pattern
- Gemini CLI output is captured via subprocess with configurable timeout
- All consultations are logged with timestamps and execution times
- The integration gracefully handles authentication errors with helpful tips