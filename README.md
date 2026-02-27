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

2. **Set up Snowflake credentials** - Create a `.env` file in the project root:
```env
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_WAREHOUSE=your_warehouse
```

   **Account identifier:** Use the exact value from Snowflake (e.g. from the Snowsight URL or Admin > Accounts). Common formats: `orgname-accountname` or `accountlocator.region` (e.g. `xy12345.us-east-1`).

3. **Verify connection** (optional):
```bash
python test_connection.py
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

### Troubleshooting

**Error: `250003 (08001): 404 Not Found` on login**

The Snowflake login URL is wrong, usually due to an incorrect `SNOWFLAKE_ACCOUNT` value.

1. Run `python test_connection.py` from the project root to see the URL being used and get hints.
2. In Snowflake (Snowsight), open the account selector or copy the URL when logged in. Use that account identifier in `.env`.
3. Try without the region suffix (e.g. `AMPXXYB-BXB87131` instead of `AMPXXYB-BXB87131.us-east-1`) or use the org-account format shown in Admin > Accounts.

**MCP doesn’t see your `.env`**

If the server is started by Cursor/Claude from a different working directory, `.env` may not be found. Either run the server from the project directory or use environment variables in your MCP config instead of a `.env` file.

### Security Note

For read-only access you have two options:
- Use a Snowflake user with read-only permissions. Write operations will automatically fail at the database level.
- Disable execute_write_query tool, this will also reject any of the next operations -> ['INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TRUNCATE', 'MERGE', 'COPY']

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the [MIT License](LICENSE).
