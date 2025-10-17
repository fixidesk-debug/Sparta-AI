"""
Enhanced Data Source Connectors - Support for Multiple Data Sources
Supports: PostgreSQL, MySQL, MongoDB, SQLite, BigQuery, Snowflake, 
         Databricks, SQL Server, Supabase, Vertica
"""
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import logging
from sqlalchemy import create_engine, text
import json

logger = logging.getLogger(__name__)


class EnhancedDataConnectors:
    """Enhanced connector for multiple data sources"""
    
    SUPPORTED_CONNECTORS = [
        'postgresql', 'mysql', 'mongodb', 'sqlite', 'bigquery', 
        'snowflake', 'databricks', 'sqlserver', 'supabase', 'vertica'
    ]
    
    # ==================== SQL Databases ====================
    
    @staticmethod
    def connect_postgresql(
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        query: str,
        ssl_mode: str = 'prefer'
    ) -> pd.DataFrame:
        """Connect to PostgreSQL database"""
        try:
            connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}?sslmode={ssl_mode}"
            engine = create_engine(connection_string)
            df = pd.read_sql_query(query, engine)
            engine.dispose()
            logger.info(f"PostgreSQL: Fetched {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"PostgreSQL error: {e}")
            raise
    
    @staticmethod
    def connect_mysql(
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        query: str,
        charset: str = 'utf8mb4'
    ) -> pd.DataFrame:
        """Connect to MySQL database"""
        try:
            connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset={charset}"
            engine = create_engine(connection_string)
            df = pd.read_sql_query(query, engine)
            engine.dispose()
            logger.info(f"MySQL: Fetched {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"MySQL error: {e}")
            raise
    
    @staticmethod
    def connect_sqlserver(
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        query: str,
        driver: str = 'ODBC Driver 17 for SQL Server'
    ) -> pd.DataFrame:
        """Connect to Microsoft SQL Server"""
        try:
            import urllib.parse
            params = urllib.parse.quote_plus(
                f"DRIVER={{{driver}}};SERVER={host},{port};DATABASE={database};UID={username};PWD={password}"
            )
            connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
            engine = create_engine(connection_string)
            df = pd.read_sql_query(query, engine)
            engine.dispose()
            logger.info(f"SQL Server: Fetched {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"SQL Server error: {e}")
            raise
    
    @staticmethod
    def connect_sqlite(
        database_path: str,
        query: str
    ) -> pd.DataFrame:
        """Connect to SQLite database"""
        try:
            connection_string = f"sqlite:///{database_path}"
            engine = create_engine(connection_string)
            df = pd.read_sql_query(query, engine)
            engine.dispose()
            logger.info(f"SQLite: Fetched {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"SQLite error: {e}")
            raise
    
    # ==================== NoSQL Databases ====================
    
    @staticmethod
    def connect_mongodb(
        host: str,
        port: int,
        database: str,
        collection: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
        limit: int = 10000,
        projection: Optional[Dict[str, int]] = None
    ) -> pd.DataFrame:
        """Connect to MongoDB"""
        try:
            import pymongo
            
            if username and password:
                connection_string = f"mongodb://{username}:{password}@{host}:{port}/"
            else:
                connection_string = f"mongodb://{host}:{port}/"
            
            client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            db = client[database]
            coll = db[collection]
            
            query = query or {}
            cursor = coll.find(query, projection).limit(limit)
            data = list(cursor)
            df = pd.DataFrame(data)
            
            if '_id' in df.columns:
                df['_id'] = df['_id'].astype(str)
            
            client.close()
            logger.info(f"MongoDB: Fetched {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"MongoDB error: {e}")
            raise
    
    # ==================== Cloud Data Warehouses ====================
    
    @staticmethod
    def connect_bigquery(
        project_id: str,
        query: str,
        credentials_json: Optional[str] = None,
        location: str = 'US'
    ) -> pd.DataFrame:
        """Connect to Google BigQuery"""
        try:
            from google.cloud import bigquery
            from google.oauth2 import service_account
            
            if credentials_json:
                credentials = service_account.Credentials.from_service_account_info(
                    json.loads(credentials_json)
                )
                client = bigquery.Client(
                    project=project_id,
                    credentials=credentials,
                    location=location
                )
            else:
                client = bigquery.Client(project=project_id, location=location)
            
            df = client.query(query).to_dataframe()
            logger.info(f"BigQuery: Fetched {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"BigQuery error: {e}")
            raise
    
    @staticmethod
    def connect_snowflake(
        account: str,
        warehouse: str,
        database: str,
        schema: str,
        username: str,
        password: str,
        query: str,
        role: Optional[str] = None
    ) -> pd.DataFrame:
        """Connect to Snowflake"""
        try:
            import snowflake.connector
            
            conn_params = {
                'account': account,
                'user': username,
                'password': password,
                'warehouse': warehouse,
                'database': database,
                'schema': schema
            }
            
            if role:
                conn_params['role'] = role
            
            conn = snowflake.connector.connect(**conn_params)
            df = pd.read_sql(query, conn)
            conn.close()
            logger.info(f"Snowflake: Fetched {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Snowflake error: {e}")
            raise
    
    @staticmethod
    def connect_databricks(
        server_hostname: str,
        http_path: str,
        access_token: str,
        query: str,
        catalog: Optional[str] = None,
        schema: Optional[str] = None
    ) -> pd.DataFrame:
        """Connect to Databricks"""
        try:
            from databricks import sql
            
            connection = sql.connect(
                server_hostname=server_hostname,
                http_path=http_path,
                access_token=access_token
            )
            
            cursor = connection.cursor()
            
            # Set catalog and schema if provided
            if catalog:
                cursor.execute(f"USE CATALOG {catalog}")
            if schema:
                cursor.execute(f"USE SCHEMA {schema}")
            
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            
            cursor.close()
            connection.close()
            logger.info(f"Databricks: Fetched {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Databricks error: {e}")
            raise
    
    @staticmethod
    def connect_supabase(
        host: str,
        database: str,
        username: str,
        password: str,
        query: str,
        port: int = 5432
    ) -> pd.DataFrame:
        """Connect to Supabase (PostgreSQL-based)"""
        try:
            # Supabase uses PostgreSQL
            connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}?sslmode=require"
            engine = create_engine(connection_string)
            df = pd.read_sql_query(query, engine)
            engine.dispose()
            logger.info(f"Supabase: Fetched {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Supabase error: {e}")
            raise
    
    @staticmethod
    def connect_vertica(
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        query: str
    ) -> pd.DataFrame:
        """Connect to Vertica"""
        try:
            import vertica_python
            
            conn_info = {
                'host': host,
                'port': port,
                'database': database,
                'user': username,
                'password': password
            }
            
            connection = vertica_python.connect(**conn_info)
            df = pd.read_sql(query, connection)
            connection.close()
            logger.info(f"Vertica: Fetched {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Vertica error: {e}")
            raise
    
    # ==================== Connection Testing ====================
    
    @staticmethod
    def test_connection(
        connector_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test connection to any supported data source"""
        try:
            if connector_type == 'postgresql':
                connection_string = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                engine.dispose()
                
            elif connector_type == 'mysql':
                connection_string = f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                engine.dispose()
                
            elif connector_type == 'sqlserver':
                import urllib.parse
                driver = config.get('driver', 'ODBC Driver 17 for SQL Server')
                params = urllib.parse.quote_plus(
                    f"DRIVER={{{driver}}};SERVER={config['host']},{config['port']};DATABASE={config['database']};UID={config['username']};PWD={config['password']}"
                )
                connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                engine.dispose()
                
            elif connector_type == 'mongodb':
                import pymongo
                if config.get('username') and config.get('password'):
                    connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/"
                else:
                    connection_string = f"mongodb://{config['host']}:{config['port']}/"
                client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=5000)
                client.server_info()
                client.close()
                
            elif connector_type == 'bigquery':
                from google.cloud import bigquery
                from google.oauth2 import service_account
                
                if config.get('credentials_json'):
                    credentials = service_account.Credentials.from_service_account_info(
                        json.loads(config['credentials_json'])
                    )
                    client = bigquery.Client(
                        project=config['project_id'],
                        credentials=credentials
                    )
                else:
                    client = bigquery.Client(project=config['project_id'])
                
                # Test with simple query
                client.query("SELECT 1").result()
                
            elif connector_type == 'snowflake':
                import snowflake.connector
                conn = snowflake.connector.connect(
                    account=config['account'],
                    user=config['username'],
                    password=config['password'],
                    warehouse=config['warehouse'],
                    database=config['database'],
                    schema=config['schema']
                )
                conn.cursor().execute("SELECT 1")
                conn.close()
                
            elif connector_type == 'databricks':
                from databricks import sql
                connection = sql.connect(
                    server_hostname=config['server_hostname'],
                    http_path=config['http_path'],
                    access_token=config['access_token']
                )
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                connection.close()
                
            elif connector_type == 'supabase':
                connection_string = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 5432)}/{config['database']}?sslmode=require"
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                engine.dispose()
                
            elif connector_type == 'vertica':
                import vertica_python
                connection = vertica_python.connect(
                    host=config['host'],
                    port=config['port'],
                    database=config['database'],
                    user=config['username'],
                    password=config['password']
                )
                connection.cursor().execute("SELECT 1")
                connection.close()
                
            elif connector_type == 'sqlite':
                connection_string = f"sqlite:///{config['database_path']}"
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                engine.dispose()
            
            else:
                raise ValueError(f"Unsupported connector type: {connector_type}")
            
            return {
                "success": True,
                "message": f"Successfully connected to {connector_type}",
                "connector_type": connector_type
            }
            
        except Exception as e:
            logger.error(f"Connection test failed for {connector_type}: {e}")
            return {
                "success": False,
                "message": str(e),
                "connector_type": connector_type
            }
    
    # ==================== Metadata Operations ====================
    
    @staticmethod
    def list_tables(
        connector_type: str,
        config: Dict[str, Any]
    ) -> List[str]:
        """List tables/collections in data source"""
        try:
            if connector_type in ['postgresql', 'supabase']:
                connection_string = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config.get('port', 5432)}/{config['database']}"
                if connector_type == 'supabase':
                    connection_string += "?sslmode=require"
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
                    tables = [row[0] for row in result]
                engine.dispose()
                return tables
                
            elif connector_type == 'mysql':
                connection_string = f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    result = conn.execute(text("SHOW TABLES"))
                    tables = [row[0] for row in result]
                engine.dispose()
                return tables
                
            elif connector_type == 'sqlserver':
                import urllib.parse
                driver = config.get('driver', 'ODBC Driver 17 for SQL Server')
                params = urllib.parse.quote_plus(
                    f"DRIVER={{{driver}}};SERVER={config['host']},{config['port']};DATABASE={config['database']};UID={config['username']};PWD={config['password']}"
                )
                connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"))
                    tables = [row[0] for row in result]
                engine.dispose()
                return tables
                
            elif connector_type == 'mongodb':
                import pymongo
                if config.get('username') and config.get('password'):
                    connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/"
                else:
                    connection_string = f"mongodb://{config['host']}:{config['port']}/"
                client = pymongo.MongoClient(connection_string)
                db = client[config['database']]
                collections = db.list_collection_names()
                client.close()
                return collections
                
            elif connector_type == 'bigquery':
                from google.cloud import bigquery
                from google.oauth2 import service_account
                
                if config.get('credentials_json'):
                    credentials = service_account.Credentials.from_service_account_info(
                        json.loads(config['credentials_json'])
                    )
                    client = bigquery.Client(
                        project=config['project_id'],
                        credentials=credentials
                    )
                else:
                    client = bigquery.Client(project=config['project_id'])
                
                dataset_id = config.get('dataset_id')
                if dataset_id:
                    tables = list(client.list_tables(dataset_id))
                    return [table.table_id for table in tables]
                return []
                
            elif connector_type == 'snowflake':
                import snowflake.connector
                conn = snowflake.connector.connect(
                    account=config['account'],
                    user=config['username'],
                    password=config['password'],
                    warehouse=config['warehouse'],
                    database=config['database'],
                    schema=config['schema']
                )
                cursor = conn.cursor()
                cursor.execute("SHOW TABLES")
                tables = [row[1] for row in cursor.fetchall()]
                conn.close()
                return tables
                
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
            logger.error(f"Error listing tables for {connector_type}: {e}")
            raise
    
    @staticmethod
    def get_connector_info(connector_type: str) -> Dict[str, Any]:
        """Get information about a connector"""
        connector_info = {
            'postgresql': {
                'name': 'PostgreSQL',
                'type': 'SQL Database',
                'required_fields': ['host', 'port', 'database', 'username', 'password'],
                'optional_fields': ['ssl_mode'],
                'default_port': 5432
            },
            'mysql': {
                'name': 'MySQL',
                'type': 'SQL Database',
                'required_fields': ['host', 'port', 'database', 'username', 'password'],
                'optional_fields': ['charset'],
                'default_port': 3306
            },
            'sqlserver': {
                'name': 'Microsoft SQL Server',
                'type': 'SQL Database',
                'required_fields': ['host', 'port', 'database', 'username', 'password'],
                'optional_fields': ['driver'],
                'default_port': 1433
            },
            'mongodb': {
                'name': 'MongoDB',
                'type': 'NoSQL Database',
                'required_fields': ['host', 'port', 'database'],
                'optional_fields': ['username', 'password', 'collection'],
                'default_port': 27017
            },
            'bigquery': {
                'name': 'Google BigQuery',
                'type': 'Cloud Data Warehouse',
                'required_fields': ['project_id'],
                'optional_fields': ['credentials_json', 'dataset_id', 'location'],
                'default_port': None
            },
            'snowflake': {
                'name': 'Snowflake',
                'type': 'Cloud Data Warehouse',
                'required_fields': ['account', 'warehouse', 'database', 'schema', 'username', 'password'],
                'optional_fields': ['role'],
                'default_port': None
            },
            'databricks': {
                'name': 'Databricks',
                'type': 'Cloud Data Platform',
                'required_fields': ['server_hostname', 'http_path', 'access_token'],
                'optional_fields': ['catalog', 'schema'],
                'default_port': None
            },
            'supabase': {
                'name': 'Supabase',
                'type': 'Database (PostgreSQL)',
                'required_fields': ['host', 'database', 'username', 'password'],
                'optional_fields': ['port'],
                'default_port': 5432
            },
            'vertica': {
                'name': 'Vertica',
                'type': 'Analytics Database',
                'required_fields': ['host', 'port', 'database', 'username', 'password'],
                'optional_fields': [],
                'default_port': 5433
            },
            'sqlite': {
                'name': 'SQLite',
                'type': 'File-based Database',
                'required_fields': ['database_path'],
                'optional_fields': [],
                'default_port': None
            }
        }
        
        return connector_info.get(connector_type, {})
