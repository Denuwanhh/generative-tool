import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import FastMCP

from db_config import DBConfig
from query_generator import QueryGenerator
from executor import CodeExecutor

# Configure standard logging to stderr since the MCP server communicates via stdio (stdout)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Load environment variables on startup
current_dir = Path(__file__).resolve().parent
env_path = current_dir / ".env"
if not env_path.exists():
    env_path = Path(".env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    logger.warning(".env file not found, relying on system environment variables.")

# Initialize FastMCP Server
mcp = FastMCP("Database Natural Language Query Server")

@mcp.tool()
def query_database(user_query: str) -> str:
    """Run a plain-English natural language query against the connected database and return the result as structured XML.

    Args:
        user_query: The database query request in plain English (e.g. 'Show a list of all expense items').
    """
    logger.info(f"MCP Tool 'query_database' called with query: '{user_query}'")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL is missing in the environment.")
        return "<error>DATABASE_URL is not set in server environment variables</error>"
        
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY is missing in the environment.")
        return "<error>ANTHROPIC_API_KEY is not set in server environment variables</error>"

    try:
        # Step 1: Extract DB DDL using DBConfig
        logger.info("Extracting database DDL structure.")
        db_config = DBConfig(database_url)
        ddl_string = db_config.get_db_ddl()
        
        # Step 2: Request the python query code from LLM using QueryGenerator
        generator = QueryGenerator(api_key)
        query_code = generator.generate_query_code(ddl_string, user_query)
        
        # Step 3: Run the code using CodeExecutor
        executor = CodeExecutor()
        result = executor.execute(query_code)
        
        return str(result) if result is not None else "<error>No result returned by query execution</error>"
    except Exception as e:
        logger.error(f"Error executing natural language query: {e}")
        return f"<error>{str(e)}</error>"

if __name__ == "__main__":
    logger.info("Starting Database Query MCP Server...")
    mcp.run()
