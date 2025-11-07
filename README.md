A Model Context Protocol (MCP) server that provides Claude access to Snowflake databases.

![GitHub Stars](https://img.shields.io/github/stars/datawiz168/mcp-snowflake-service?style=social)
[![Smithery Badge](https://smithery.ai/badge/@datawiz168/mcp-service-snowflake)](https://smithery.ai/server/@datawiz168/mcp-service-snowflake)

This server implements the Model Context Protocol to allow Claude to:
- Execute SQL queries on Snowflake databases
- Automatically handle database connection lifecycle (connect, reconnect on timeout, close)
- Handle query results and errors
- Perform database operations safely

## Installation

### Installing via Smithery

To install mcp-service-snowflake for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@datawiz168/mcp-service-snowflake):

```bash
npx -y @smithery/cli install @datawiz168/mcp-service-snowflake --client claude
```

### Manual Installation
1. Clone this repository
```bash
git clone https://github.com/datawiz168/mcp-snowflake-service.git
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

## Configuration

### MCP Client Configuration Example

Add the following configuration to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "snowflake": {
      "command": "C:\\Users\\K\\anaconda3\\envs\\regular310\\python.exe",
      "args": ["D:\\tools\\mcp-snowflake\\server.py"]
    }
  }
}
```

Configuration parameters:
- `command`: Full path to your Python interpreter. Please modify this according to your Python installation location.
- `args`: Full path to the server script. Please modify this according to where you cloned the repository.

Example paths for different operating systems:

Windows:
```json
{
  "mcpServers": {
    "snowflake": {
      "command": "C:\\Users\\YourUsername\\anaconda3\\python.exe",
      "args": ["C:\\Path\\To\\mcp-snowflake\\server.py"]
    }
  }
}
```

MacOS/Linux:
```json
{
  "mcpServers": {
    "snowflake": {
      "command": "/usr/bin/python3",
      "args": ["/path/to/mcp-snowflake/server.py"]
    }
  }
}
```

### Snowflake Configuration

Create a `.env` file in the project root directory and add the following configuration:

```env
SNOWFLAKE_USER=your_username      # Your username
SNOWFLAKE_PASSWORD=your_password  # Your password
SNOWFLAKE_ACCOUNT=NRB18479.US-WEST-2    # Example: NRB18479.US-WEST-2
SNOWFLAKE_DATABASE=your_database  # Your database
SNOWFLAKE_WAREHOUSE=your_warehouse # Your warehouse
```

## Connection Management

The server provides automatic connection management features:

- Automatic connection initialization
  - Creates connection when first query is received
  - Validates connection parameters

- Connection maintenance
  - Keeps track of connection state
  - Handles connection timeouts
  - Automatically reconnects if connection is lost

- Connection cleanup
  - Properly closes connections when server stops
  - Releases resources appropriately

## Usage

The server will start automatically with the Claude Desktop client. No manual startup is required. Once the server is running, Claude will be able to execute Snowflake queries.

For development testing, you can start the server manually using:

```bash
python server.py
```

Note: Manual server startup is not needed for normal use. The Claude Desktop client will automatically manage server startup and shutdown based on the configuration.

## Features

- Secure Snowflake database access
- Robust error handling and reporting
- Automatic connection management
- Query execution and result processing

## Development

To contribute code or report issues:

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## notes
mcp‑server‑snowflake controls database access rights precisely by way of database users. If you only need to read data, just assign a user with read‑only database permissions.

## License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the [MIT License](LICENSE).
