"""
Data Source Connectors - Connect to various data sources
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import logging
from sqlalchemy import create_engine, text
import pymongo
import pymysql

logger = logging.getLogger(__name__)


class DataConnectors:
    """Connect to various data sources and fetch data"""
    
    @staticmethod
    def connect_postgresql(
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        query: str
    ) -> pd.DataFrame:
        """Connect to PostgreSQL and execute query"""
        try:
            connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            engine = create_engine(connection_string)
            
            df = pd.read_sql_query(query, engine)
            engine.dispose()
            
            logger.info(f"Fetched {len(df)} rows from PostgreSQL")
            return df
            
        except Exception as e:
            logger.error(f"PostgreSQL connection error: {e}")
            raise
    
    @staticmethod
    def connect_mysql(
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        query: str
    ) -> pd.DataFrame:
        """Connect to MySQL and execute query"""
        try:
            connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            engine = create_engine(connection_string)
            
            df = pd.read_sql_query(query, engine)
            engine.dispose()
            
            logger.info(f"Fetched {len(df)} rows from MySQL")
            return df
            
        except Exception as e:
            logger.error(f"MySQL connection error: {e}")
            raise
    
    @staticmethod
    def connect_mongodb(
        host: str,
        port: int,
        database: str,
        collection: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
        limit: int = 10000
    ) -> pd.DataFrame:
        """Connect to MongoDB and fetch data"""
        try:
            if username and password:
                connection_string = f"mongodb://{username}:{password}@{host}:{port}/"
            else:
                connection_string = f"mongodb://{host}:{port}/"
            
            client = pymongo.MongoClient(connection_string)
            db = client[database]
            coll = db[collection]
            
            # Execute query
            query = query or {}
            cursor = coll.find(query).limit(limit)
            
            # Convert to DataFrame
            data = list(cursor)
            df = pd.DataFrame(data)
            
            # Remove MongoDB _id if present
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)
            
            client.close()
            
            logger.info(f"Fetched {len(df)} rows from MongoDB")
            return df
            
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            raise
    
    @staticmethod
    def connect_sqlite(
        database_path: str,
        query: str
    ) -> pd.DataFrame:
        """Connect to SQLite and execute query"""
        try:
            connection_string = f"sqlite:///{database_path}"
            engine = create_engine(connection_string)
            
            df = pd.read_sql_query(query, engine)
            engine.dispose()
            
            logger.info(f"Fetched {len(df)} rows from SQLite")
            return df
            
        except Exception as e:
            logger.error(f"SQLite connection error: {e}")
            raise
    
    @staticmethod
    def test_connection(
        connector_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test database connection"""
        try:
            if connector_type == 'postgresql':
                connection_string = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    result.fetchone()
                engine.dispose()
                
            elif connector_type == 'mysql':
                connection_string = f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    result.fetchone()
                engine.dispose()
                
            elif connector_type == 'mongodb':
                if config.get('username') and config.get('password'):
                    connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/"
                else:
                    connection_string = f"mongodb://{config['host']}:{config['port']}/"
                
                client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=5000)
                client.server_info()  # Will raise exception if cannot connect
                client.close()
                
            elif connector_type == 'sqlite':
                connection_string = f"sqlite:///{config['database_path']}"
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    result.fetchone()
                engine.dispose()
            
            else:
                raise ValueError(f"Unknown connector type: {connector_type}")
            
            return {
                "success": True,
                "message": "Connection successful",
                "connector_type": connector_type
            }
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                "success": False,
                "message": str(e),
                "connector_type": connector_type
            }
    
    @staticmethod
    def list_tables(
        connector_type: str,
        config: Dict[str, Any]
    ) -> List[str]:
        """List available tables/collections"""
        try:
            if connector_type in ['postgresql', 'mysql']:
                if connector_type == 'postgresql':
                    connection_string = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
                else:
                    connection_string = f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
                
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    if connector_type == 'postgresql':
                        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
                    else:
                        result = conn.execute(text("SHOW TABLES"))
                    tables = [row[0] for row in result]
                engine.dispose()
                return tables
                
            elif connector_type == 'mongodb':
                if config.get('username') and config.get('password'):
                    connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/"
                else:
                    connection_string = f"mongodb://{config['host']}:{config['port']}/"
                
                client = pymongo.MongoClient(connection_string)
                db = client[config['database']]
                collections = db.list_collection_names()
                client.close()
                return collections
                
            elif connector_type == 'sqlite':
                connection_string = f"sqlite:///{config['database_path']}"
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                    tables = [row[0] for row in result]
                engine.dispose()
                return tables
            
            return []
            
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            raise
    
    @staticmethod
    def get_table_schema(
        connector_type: str,
        config: Dict[str, Any],
        table_name: str
    ) -> List[Dict[str, Any]]:
        """Get schema information for a table"""
        try:
            if connector_type in ['postgresql', 'mysql']:
                if connector_type == 'postgresql':
                    connection_string = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
                    query = f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = '{table_name}'
                    """
                else:
                    connection_string = f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
                    query = f"DESCRIBE {table_name}"
                
                engine = create_engine(connection_string)
                df = pd.read_sql_query(query, engine)
                engine.dispose()
                
                schema = df.to_dict('records')
                return schema
                
            elif connector_type == 'mongodb':
                if config.get('username') and config.get('password'):
                    connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/"
                else:
                    connection_string = f"mongodb://{config['host']}:{config['port']}/"
                
                client = pymongo.MongoClient(connection_string)
                db = client[config['database']]
                coll = db[table_name]
                
                # Sample document to infer schema
                sample = coll.find_one()
                if sample:
                    schema = [
                        {'field': key, 'type': type(value).__name__}
                        for key, value in sample.items()
                    ]
                else:
                    schema = []
                
                client.close()
                return schema
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting table schema: {e}")
            raise
