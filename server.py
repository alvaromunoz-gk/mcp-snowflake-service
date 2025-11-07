#!/usr/bin/env python
import os
import asyncio
import logging
import json
import time
import snowflake.connector
from dotenv import load_dotenv
import mcp.server.stdio
from mcp.server import Server
from mcp.types import Tool, TextContent
from typing import Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('snowflake_server')

load_dotenv()

class SnowflakeConnection:
    """
    Snowflake database connection management class
    """
    def __init__(self):
        # Initialize configuration
        self.config = {
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": os.getenv("SNOWFLAKE_PASSWORD"),
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        }
        self.conn: Optional[snowflake.connector.SnowflakeConnection] = None
        logger.info(f"Initialized with config (excluding password): {json.dumps({k:v for k,v in self.config.items() if k != 'password'})}")
    
    def ensure_connection(self) -> snowflake.connector.SnowflakeConnection:
        """
        Ensure database connection is available, create new connection if it doesn't exist or is disconnected
        """
        try:
            # Check if connection needs to be re-established
            if self.conn is None:
                logger.info("Creating new Snowflake connection...")
                self.conn = snowflake.connector.connect(
                    **self.config,
                    client_session_keep_alive=True,
                    network_timeout=15,
                    login_timeout=15
                )
                self.conn.cursor().execute("ALTER SESSION SET TIMEZONE = 'UTC'")
                logger.info("New connection established and configured")
            
            # Test if connection is valid
            try:
                self.conn.cursor().execute("SELECT 1")
            except:
                logger.info("Connection lost, reconnecting...")
                self.conn = None
                return self.ensure_connection()
                
            return self.conn
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            raise

    def execute_read_query(self, query: str) -> list[dict[str, Any]]:
        """
        Execute a read-only SQL query and return results
        
        Args:
            query (str): SQL query statement (SELECT, SHOW, DESCRIBE, etc.)
            
        Returns:
            list[dict[str, Any]]: List of query results
            
        Raises:
            ValueError: If query contains write operations
        """
        # Validate that query is read-only
        write_keywords = ['INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TRUNCATE', 'MERGE', 'COPY']
        query_upper = query.strip().upper()
        if any(query_upper.startswith(keyword) for keyword in write_keywords):
            raise ValueError(f"Read query cannot contain write operations. Use execute_write_query for: {query[:50]}...")
        
        start_time = time.time()
        logger.info(f"Executing read query: {query[:200]}...")  # Log only first 200 characters
        
        try:
            conn = self.ensure_connection()
            with conn.cursor() as cursor:
                cursor.execute(query)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    results = [dict(zip(columns, row)) for row in rows]
                    logger.info(f"Read query returned {len(results)} rows in {time.time() - start_time:.2f}s")
                    return results
                return []
                
        except snowflake.connector.errors.ProgrammingError as e:
            logger.error(f"SQL Error: {str(e)}")
            logger.error(f"Error Code: {getattr(e, 'errno', 'unknown')}")
            raise
        except Exception as e:
            logger.error(f"Query error: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            raise

    def execute_write_query(self, query: str) -> dict[str, Any]:
        """
        Execute a write SQL query (INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, etc.)
        
        Args:
            query (str): SQL query statement (INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, etc.)
            
        Returns:
            dict[str, Any]: Result containing affected_rows
            
        Raises:
            ValueError: If query is not a write operation
        """
        # Validate that query is a write operation
        write_keywords = ['INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TRUNCATE', 'MERGE', 'COPY']
        query_upper = query.strip().upper()
        if not any(query_upper.startswith(keyword) for keyword in write_keywords):
            raise ValueError(f"Write query must start with a write operation keyword. Use execute_read_query for: {query[:50]}...")
        
        start_time = time.time()
        logger.info(f"Executing write query: {query[:200]}...")  # Log only first 200 characters
        
        try:
            conn = self.ensure_connection()
            with conn.cursor() as cursor:
                cursor.execute("BEGIN")
                try:
                    cursor.execute(query)
                    conn.commit()
                    affected_rows = cursor.rowcount
                    logger.info(f"Write query executed in {time.time() - start_time:.2f}s, affected {affected_rows} rows")
                    return {"affected_rows": affected_rows, "status": "success"}
                except Exception as e:
                    conn.rollback()
                    raise
                
        except snowflake.connector.errors.ProgrammingError as e:
            logger.error(f"SQL Error: {str(e)}")
            logger.error(f"Error Code: {getattr(e, 'errno', 'unknown')}")
            raise
        except Exception as e:
            logger.error(f"Query error: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            raise

    def close(self):
        """
        Close database connection
        """
        if self.conn:
            try:
                self.conn.close()
                logger.info("Connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}")
            finally:
                self.conn = None

class SnowflakeServer(Server):
    """
    Snowflake MCP server class, handles client interactions
    """
    def __init__(self):
        super().__init__(name="snowflake-server")
        self.db = SnowflakeConnection()
        logger.info("SnowflakeServer initialized")

        @self.list_tools()
        async def handle_tools():
            """
            Return list of available tools
            """
            return [
                Tool(
                    name="execute_read_query",
                    description="Execute a read-only SQL query on Snowflake (SELECT, SHOW, DESCRIBE, etc.). Returns query results.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Read-only SQL query to execute (SELECT, SHOW, DESCRIBE, etc.)"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="execute_write_query",
                    description="Execute a write SQL query on Snowflake (INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, etc.). Returns affected rows count.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Write SQL query to execute (INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, etc.)"
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]

        @self.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            """
            Handle tool call requests
            
            Args:
                name (str): Tool name
                arguments (dict): Tool arguments
                
            Returns:
                list[TextContent]: Execution results
            """
            if name == "execute_read_query":
                start_time = time.time()
                try:
                    result = self.db.execute_read_query(arguments["query"])
                    execution_time = time.time() - start_time
                    
                    return [TextContent(
                        type="text",
                        text=f"Read query results (execution time: {execution_time:.2f}s):\n{json.dumps(result, indent=2, default=str)}"
                    )]
                except Exception as e:
                    error_message = f"Error executing read query: {str(e)}"
                    logger.error(error_message)
                    return [TextContent(
                        type="text",
                        text=error_message
                    )]
            elif name == "execute_write_query":
                start_time = time.time()
                try:
                    result = self.db.execute_write_query(arguments["query"])
                    execution_time = time.time() - start_time
                    
                    return [TextContent(
                        type="text",
                        text=f"Write query completed (execution time: {execution_time:.2f}s):\n{json.dumps(result, indent=2)}"
                    )]
                except Exception as e:
                    error_message = f"Error executing write query: {str(e)}"
                    logger.error(error_message)
                    return [TextContent(
                        type="text",
                        text=error_message
                    )]
            else:
                error_message = f"Unknown tool: {name}"
                logger.error(error_message)
                return [TextContent(
                    type="text",
                    text=error_message
                )]

    def __del__(self):
        """
        Clean up resources, close database connection
        """
        if hasattr(self, 'db'):
            self.db.close()

async def main():
    """
    Main function, starts server and handles requests
    """
    try:
        server = SnowflakeServer()
        initialization_options = server.create_initialization_options()
        logger.info("Starting server")
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                initialization_options
            )
    except Exception as e:
        logger.critical(f"Server failed: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Server shutting down")

if __name__ == "__main__":
    asyncio.run(main())