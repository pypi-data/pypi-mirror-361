# Gemini MCP Server

MCP (Model Context Protocol) Server with Google Gemini CLI integration for AI second opinions and validation in development workflows.

## Features

- 🤖 **AI Second Opinions**: Get alternative perspectives from Google's Gemini AI
- 🔍 **Automatic Uncertainty Detection**: Triggers consultations when uncertainty is detected
- ⚡ **Rate Limiting**: Built-in rate limiting to prevent API abuse
- 🛡️ **Configurable Models**: Support for different Gemini models
- 📊 **Consultation Logging**: Track all AI consultations with timestamps

## Quick Start

### Using uvx (Recommended)

Run directly without installation:

```bash
# Run in current directory
uvx gemini-mcp-server

# Run with specific project root
uvx gemini-mcp-server --project-root /path/to/project
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/taehun-kmu/gemini-mcp-server
cd gemini-mcp-server

# Install with uv
uv pip install -e .

# Run the server
gemini-mcp-server
```

## Prerequisites

1. **Node.js 18+** - Required for Gemini CLI
2. **Python 3.8+** - Required for MCP server
3. **Gemini CLI** - Install and authenticate:

```bash
# Install Gemini CLI
npm install -g @google/gemini-cli

# Authenticate (run once)
gemini
```

## Configuration

Create a `gemini-config.json` file in your project root:

```json
{
  "enabled": true,
  "auto_consult": true,
  "cli_command": "gemini",
  "timeout": 60,
  "rate_limit_delay": 2.0,
  "model": "gemini-2.5-flash",
  "log_consultations": true
}
```

### Environment Variables

Override configuration with environment variables:

- `GEMINI_ENABLED`: Enable/disable integration
- `GEMINI_AUTO_CONSULT`: Enable/disable automatic consultation
- `GEMINI_CLI_COMMAND`: CLI command (default: "gemini")
- `GEMINI_TIMEOUT`: Command timeout in seconds
- `GEMINI_RATE_LIMIT`: Delay between consultations
- `GEMINI_MODEL`: Model to use (default: "gemini-2.5-flash")

## MCP Tools

The server exposes three MCP tools:

1. **consult_gemini**: Get second opinions from Gemini
   - `query`: The question or topic
   - `context`: Additional context
   - `comparison_mode`: Request structured comparison format

2. **gemini_status**: Check integration status and statistics

3. **toggle_gemini_auto_consult**: Enable/disable automatic consultation
   - `enable`: true/false or omit to toggle

## Claude Code Integration

Configure Claude Code to use this MCP server by adding to your MCP configuration:

```json
{
  "mcpServers": {
    "gemini": {
      "command": "uvx",
      "args": ["gemini-mcp-server"],
      "env": {
        "GEMINI_ENABLED": "true"
      }
    }
  }
}
```

Note: Add `"--project-root", "/path/to/project"` to args if you need to specify a different project directory.

## Development

### Project Structure

```
gemini-mcp-server/
├── gemini_mcp/
│   ├── __init__.py
│   ├── __main__.py         # CLI entry point
│   ├── gemini_integration.py  # Gemini integration logic
│   └── server.py           # MCP server implementation
├── pyproject.toml          # Package configuration
├── README.md              # This file
├── LICENSE                # MIT License
├── setup-gemini-integration.sh  # Setup script
└── gemini-config.json     # Example configuration
```

### Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black gemini_mcp
ruff check gemini_mcp
```

## License

MIT License - see LICENSE file for details.