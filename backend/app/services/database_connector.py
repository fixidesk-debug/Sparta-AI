"""
Database Connector - Connect to External Databases
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """Connect to external databases"""
    
    SUPPORTED_DBS = ['postgresql', 'mysql', 'sqlite', 'mongodb']
    
    @staticmethod
    def connect_sql(
        db_type: str,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        query: str
    ) -> pd.DataFrame:
        """Connect to SQL database and execute query"""
        try:
            from sqlalchemy import create_engine
            
            if db_type == 'postgresql':
                conn_str = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            elif db_type == 'mysql':
                conn_str = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            elif db_type == 'sqlite':
                conn_str = f"sqlite:///{database}"
            else:
                raise ValueError(f"Unsupported database: {db_type}")
            
            engine = create_engine(conn_str)
            df = pd.read_sql(query, engine)
            engine.dispose()
            
            return df
            
        except Exception as e:
            logger.error(f"SQL connection error: {e}")
            raise
    
    @staticmethod
    def connect_mongodb(
        host: str,
        port: int,
        database: str,
        collection: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        query: Optional[Dict] = None
    ) -> pd.DataFrame:
        """Connect to MongoDB and fetch data"""
        try:
            from pymongo import MongoClient
            
            if username and password:
                client = MongoClient(f"mongodb://{username}:{password}@{host}:{port}/")
            else:
                client = MongoClient(f"mongodb://{host}:{port}/")
            
            db = client[database]
            coll = db[collection]
            
            cursor = coll.find(query or {})
            df = pd.DataFrame(list(cursor))
            
            client.close()
            return df
            
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            raise
    
    @staticmethod
    def test_connection(
        db_type: str,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """Test database connection"""
        try:
            if db_type in ['postgresql', 'mysql', 'sqlite']:
                from sqlalchemy import create_engine
                
                if db_type == 'postgresql':
                    conn_str = f"postgresql://{username}:{password}@{host}:{port}/{database}"
                elif db_type == 'mysql':
                    conn_str = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
                else:
                    conn_str = f"sqlite:///{database}"
                
                engine = create_engine(conn_str)
                conn = engine.connect()
                conn.close()
                engine.dispose()
                
            elif db_type == 'mongodb':
                from pymongo import MongoClient
                client = MongoClient(f"mongodb://{username}:{password}@{host}:{port}/", serverSelectionTimeoutMS=5000)
                client.server_info()
                client.close()
            
            return {"success": True, "message": "Connection successful"}
            
        except Exception as e:
            return {"success": False, "message": str(e)}
