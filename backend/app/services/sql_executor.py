"""
SQL Query Executor using DuckDB
"""
import duckdb
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class SQLExecutor:
    """Execute SQL queries on data files using DuckDB"""
    
    def __init__(self):
        self.connections: Dict[str, duckdb.DuckDBPyConnection] = {}
    
    def load_file_to_db(self, file_path: str, table_name: str = "data") -> duckdb.DuckDBPyConnection:
        """Load a file into DuckDB and return connection"""
        conn = duckdb.connect(":memory:")
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            if file_path.suffix.lower() == '.csv':
                conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_path}')")
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                # Read with pandas first, then register
                df = pd.read_excel(file_path)
                conn.register(table_name, df)
            elif file_path.suffix.lower() == '.json':
                df = pd.read_json(file_path)
                conn.register(table_name, df)
            elif file_path.suffix.lower() == '.parquet':
                conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_parquet('{file_path}')")
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            logger.info(f"Loaded {file_path} into table '{table_name}'")
            return conn
            
        except Exception as e:
            logger.error(f"Failed to load file: {e}")
            raise
    
    def execute_query(self, file_path: str, query: str) -> Dict[str, Any]:
        """Execute SQL query on file data"""
        conn = None
        try:
            conn = self.load_file_to_db(file_path)
            
            # Execute query
            result = conn.execute(query).fetchall()
            columns = [desc[0] for desc in conn.description]
            
            # Convert to list of dicts
            data = [dict(zip(columns, row)) for row in result]
            
            return {
                "success": True,
                "data": data,
                "columns": columns,
                "row_count": len(data)
            }
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "columns": [],
                "row_count": 0
            }
        finally:
            if conn:
                conn.close()
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate SQL query syntax"""
        conn = None
        try:
            conn = duckdb.connect(":memory:")
            # Create a dummy table for validation
            conn.execute("CREATE TABLE data (id INTEGER, name VARCHAR, value DOUBLE)")
            
            # Try to prepare the query
            conn.execute(f"EXPLAIN {query}")
            
            return {
                "valid": True,
                "message": "Query syntax is valid"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "message": str(e)
            }
        finally:
            if conn:
                conn.close()


sql_executor = SQLExecutor()
