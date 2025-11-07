A Model Context Protocol (MCP) server that allows Claude/Cursor to query Snowflake databases.

## Quick Start

### Installation

**Manual Installation**
```bash
git clone https://github.com/alvaromunoz-gk/mcp-snowflake-service.git
cd mcp-snowflake-service
pip install -r requirements.txt
```

### Configuration

1. **Configure the MCP**:
```json
{
  "mcpServers": {
    "snowflake": {
      "command": "/path/to/python3",
      "args": ["/path/to/mcp-snowflake-service/server.py"]
    }
  }
}
```

2. **Set up Snowflake credentials** - Create a `.env` file:
```env
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_WAREHOUSE=your_warehouse
```

## Usage

Once configured, restart Claude Desktop / Cursor and you can already ask to query your Snowflake database.

### Read Queries
Use `execute_read_query` for read-only operations:
- `SELECT` statements
- `SHOW` commands (databases, tables, etc.)
- `DESCRIBE` commands

**Example:** "Show me all databases" or "Select the first 10 rows from my_table"

### Write Queries
Use `execute_write_query` for data modifications:
- `INSERT`, `UPDATE`, `DELETE`
- `CREATE`, `DROP`, `ALTER`
- `TRUNCATE`, `MERGE`, `COPY`

**Example:** "Create a new database called test_db" or "Insert a new record into my_table"

### Security Note

For read-only access you have two options:
- Use a Snowflake user with read-only permissions. Write operations will automatically fail at the database level.
- Disable execute_write_query tool, this will also reject any of the next operations -> ['INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TRUNCATE', 'MERGE', 'COPY']

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the [MIT License](LICENSE).
