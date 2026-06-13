from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.schema import CreateTable
import logging

logger = logging.getLogger(__name__)

class DBConfig:
    """Handles connection to the database and generation of schema DDL."""

    def __init__(self, database_url: str):
        self.database_url = database_url

    def get_db_ddl(self) -> str:
        """Uses SQLAlchemy to connect, reflect tables across schemas, and return full DDL."""
        try:
            # Create standard SQLAlchemy engine with read-only execution options
            engine = create_engine(self.database_url, execution_options={"postgresql_readonly": True})
            
            # Inspect schemas
            inspector = inspect(engine)
            schemas = [
                s for s in inspector.get_schema_names() 
                if s not in ('information_schema', 'pg_catalog', 'pg_toast')
            ]
            
            # Reflect all tables in the schemas
            metadata = MetaData()
            for schema in schemas:
                metadata.reflect(bind=engine, schema=schema)
            
            # Generate DDL for each table
            ddl_statements = []
            for table in metadata.sorted_tables:
                # Compile table DDL using the engine's dialect
                table_ddl = str(CreateTable(table).compile(engine))
                ddl_statements.append(table_ddl.strip() + ";\n")
            
            return "\n".join(ddl_statements)
            
        except Exception as e:
            logger.error(f"Error extracting DB schema DDL: {e}")
            raise RuntimeError(f"Database schema extraction failed: {e}") from e
