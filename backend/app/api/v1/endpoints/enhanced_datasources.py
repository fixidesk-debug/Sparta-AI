"""
Enhanced Data Sources API Endpoints
Support for multiple database and cloud data warehouse connections
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import pandas as pd
import tempfile
import os

from app.db.session import get_db
from app.core.security import get_current_user
from app.services.enhanced_data_connectors import EnhancedDataConnectors
from app.db.models import File as FileModel, User

router = APIRouter()


class DataSourceConfig(BaseModel):
    """Configuration for data source connection"""
    name: str = Field(..., description="Friendly name for the connection")
    type: str = Field(..., description="Type of connector (postgresql, mysql, bigquery, etc.)")
    config: Dict[str, Any] = Field(..., description="Connection configuration")
    description: Optional[str] = Field(None, description="Optional description")


class QueryRequest(BaseModel):
    """Query request for data sources"""
    query: Optional[str] = Field(None, description="SQL query or filter")
    collection: Optional[str] = Field(None, description="Collection name (for MongoDB)")
    limit: int = Field(1000, description="Maximum rows to return", ge=1, le=100000)
    projection: Optional[Dict[str, int]] = Field(None, description="Fields to include/exclude (MongoDB)")


class SaveDataRequest(BaseModel):
    """Request to save queried data as a file"""
    datasource: DataSourceConfig
    query_request: QueryRequest
    filename: str = Field(..., description="Name for the saved file")


@router.get("/connectors")
async def list_connectors():
    """List all supported data connectors"""
    connectors = []
    for connector_type in EnhancedDataConnectors.SUPPORTED_CONNECTORS:
        info = EnhancedDataConnectors.get_connector_info(connector_type)
        if info:
            connectors.append({
                'type': connector_type,
                **info
            })
    
    return {
        "connectors": connectors,
        "count": len(connectors)
    }


@router.get("/connectors/{connector_type}")
async def get_connector_info(connector_type: str):
    """Get detailed information about a specific connector"""
    if connector_type not in EnhancedDataConnectors.SUPPORTED_CONNECTORS:
        raise HTTPException(status_code=404, detail=f"Connector '{connector_type}' not found")
    
    info = EnhancedDataConnectors.get_connector_info(connector_type)
    if not info:
        raise HTTPException(status_code=404, detail=f"No information available for '{connector_type}'")
    
    return {
        'type': connector_type,
        **info
    }


@router.post("/test")
async def test_connection(
    datasource: DataSourceConfig,
    current_user: Dict = Depends(get_current_user)
):
    """
    Test connection to a data source
    
    Returns success status and any error messages
    """
    try:
        if datasource.type not in EnhancedDataConnectors.SUPPORTED_CONNECTORS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported connector type: {datasource.type}"
            )
        
        result = EnhancedDataConnectors.test_connection(
            connector_type=datasource.type,
            config=datasource.config
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connect")
async def connect_datasource(
    datasource: DataSourceConfig,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect to a data source and validate connection
    
    This endpoint tests the connection and returns connection details.
    In production, you might want to save connection configs securely.
    """
    try:
        # Validate connector type
        if datasource.type not in EnhancedDataConnectors.SUPPORTED_CONNECTORS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported connector type: {datasource.type}"
            )
        
        # Test connection
        test_result = EnhancedDataConnectors.test_connection(
            connector_type=datasource.type,
            config=datasource.config
        )
        
        if not test_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Connection failed: {test_result.get('message')}"
            )
        
        # TODO: In production, save connection config to database (encrypted)
        # For now, return success
        return {
            "connected": True,
            "name": datasource.name,
            "type": datasource.type,
            "description": datasource.description,
            "message": test_result.get("message"),
            "connector_info": EnhancedDataConnectors.get_connector_info(datasource.type)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tables")
async def list_tables(
    datasource: DataSourceConfig,
    current_user: Dict = Depends(get_current_user)
):
    """
    List all tables/collections in a data source
    
    Returns list of table names available in the connected database
    """
    try:
        if datasource.type not in EnhancedDataConnectors.SUPPORTED_CONNECTORS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported connector type: {datasource.type}"
            )
        
        tables = EnhancedDataConnectors.list_tables(
            connector_type=datasource.type,
            config=datasource.config
        )
        
        return {
            "tables": tables,
            "count": len(tables),
            "datasource": datasource.name,
            "type": datasource.type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def query_datasource(
    datasource: DataSourceConfig,
    query_request: QueryRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Execute a query on a data source and return results
    
    Supports SQL queries for relational databases and filters for NoSQL
    """
    try:
        if datasource.type not in EnhancedDataConnectors.SUPPORTED_CONNECTORS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported connector type: {datasource.type}"
            )
        
        df = None
        
        # Route to appropriate connector
        if datasource.type == 'postgresql':
            df = EnhancedDataConnectors.connect_postgresql(
                host=datasource.config['host'],
                port=datasource.config['port'],
                database=datasource.config['database'],
                username=datasource.config['username'],
                password=datasource.config['password'],
                query=query_request.query,
                ssl_mode=datasource.config.get('ssl_mode', 'prefer')
            )
            
        elif datasource.type == 'mysql':
            df = EnhancedDataConnectors.connect_mysql(
                host=datasource.config['host'],
                port=datasource.config['port'],
                database=datasource.config['database'],
                username=datasource.config['username'],
                password=datasource.config['password'],
                query=query_request.query,
                charset=datasource.config.get('charset', 'utf8mb4')
            )
            
        elif datasource.type == 'sqlserver':
            df = EnhancedDataConnectors.connect_sqlserver(
                host=datasource.config['host'],
                port=datasource.config['port'],
                database=datasource.config['database'],
                username=datasource.config['username'],
                password=datasource.config['password'],
                query=query_request.query,
                driver=datasource.config.get('driver', 'ODBC Driver 17 for SQL Server')
            )
            
        elif datasource.type == 'mongodb':
            import json
            query_dict = None
            if query_request.query:
                try:
                    query_dict = json.loads(query_request.query)
                except:
                    query_dict = {}
            
            df = EnhancedDataConnectors.connect_mongodb(
                host=datasource.config['host'],
                port=datasource.config['port'],
                database=datasource.config['database'],
                collection=query_request.collection or datasource.config.get('collection'),
                username=datasource.config.get('username'),
                password=datasource.config.get('password'),
                query=query_dict,
                limit=query_request.limit,
                projection=query_request.projection
            )
            
        elif datasource.type == 'bigquery':
            df = EnhancedDataConnectors.connect_bigquery(
                project_id=datasource.config['project_id'],
                query=query_request.query,
                credentials_json=datasource.config.get('credentials_json'),
                location=datasource.config.get('location', 'US')
            )
            
        elif datasource.type == 'snowflake':
            df = EnhancedDataConnectors.connect_snowflake(
                account=datasource.config['account'],
                warehouse=datasource.config['warehouse'],
                database=datasource.config['database'],
                schema=datasource.config['schema'],
                username=datasource.config['username'],
                password=datasource.config['password'],
                query=query_request.query,
                role=datasource.config.get('role')
            )
            
        elif datasource.type == 'databricks':
            df = EnhancedDataConnectors.connect_databricks(
                server_hostname=datasource.config['server_hostname'],
                http_path=datasource.config['http_path'],
                access_token=datasource.config['access_token'],
                query=query_request.query,
                catalog=datasource.config.get('catalog'),
                schema=datasource.config.get('schema')
            )
            
        elif datasource.type == 'supabase':
            df = EnhancedDataConnectors.connect_supabase(
                host=datasource.config['host'],
                database=datasource.config['database'],
                username=datasource.config['username'],
                password=datasource.config['password'],
                query=query_request.query,
                port=datasource.config.get('port', 5432)
            )
            
        elif datasource.type == 'vertica':
            df = EnhancedDataConnectors.connect_vertica(
                host=datasource.config['host'],
                port=datasource.config['port'],
                database=datasource.config['database'],
                username=datasource.config['username'],
                password=datasource.config['password'],
                query=query_request.query
            )
            
        elif datasource.type == 'sqlite':
            df = EnhancedDataConnectors.connect_sqlite(
                database_path=datasource.config['database_path'],
                query=query_request.query
            )
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Connector '{datasource.type}' not implemented"
            )
        
        if df is not None:
            # Limit results
            limited_df = df.head(query_request.limit)
            
            # Convert to JSON-serializable format
            data = limited_df.to_dict('records')
            columns = list(df.columns)
            
            # Get data types
            dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
            
            return {
                "success": True,
                "data": data,
                "columns": columns,
                "dtypes": dtypes,
                "total_rows": len(df),
                "returned_rows": len(data),
                "datasource": datasource.name,
                "type": datasource.type
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch data")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


@router.post("/query/save")
async def save_query_results(
    save_request: SaveDataRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute a query and save results as a file in the system
    
    This allows users to query external data sources and save them
    for analysis within SPARTA AI
    """
    try:
        # First, execute the query
        datasource = save_request.datasource
        query_request = save_request.query_request
        
        # Execute query (reuse logic from query endpoint)
        df = None
        
        if datasource.type == 'postgresql':
            df = EnhancedDataConnectors.connect_postgresql(
                host=datasource.config['host'],
                port=datasource.config['port'],
                database=datasource.config['database'],
                username=datasource.config['username'],
                password=datasource.config['password'],
                query=query_request.query
            )
        elif datasource.type == 'mysql':
            df = EnhancedDataConnectors.connect_mysql(
                host=datasource.config['host'],
                port=datasource.config['port'],
                database=datasource.config['database'],
                username=datasource.config['username'],
                password=datasource.config['password'],
                query=query_request.query
            )
        # Add other connectors as needed...
        
        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="Query returned no data")
        
        # Save to temporary CSV file
        temp_dir = tempfile.gettempdir()
        filename = save_request.filename if save_request.filename.endswith('.csv') else f"{save_request.filename}.csv"
        file_path = os.path.join(temp_dir, filename)
        df.to_csv(file_path, index=False)
        
        # TODO: Save file to database and user's files
        # For now, return file info
        
        return {
            "success": True,
            "message": "Data saved successfully",
            "filename": filename,
            "rows": len(df),
            "columns": len(df.columns),
            "file_path": file_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save query results: {str(e)}")


@router.post("/preview")
async def preview_data(
    datasource: DataSourceConfig,
    table_name: str,
    limit: int = 100,
    current_user: Dict = Depends(get_current_user)
):
    """
    Preview data from a specific table/collection
    
    Returns a sample of rows for quick inspection
    """
    try:
        # Build a simple SELECT query based on connector type
        if datasource.type in ['postgresql', 'mysql', 'sqlserver', 'sqlite', 'supabase', 'vertica']:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
        elif datasource.type in ['bigquery']:
            query = f"SELECT * FROM `{table_name}` LIMIT {limit}"
        elif datasource.type in ['snowflake', 'databricks']:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
        elif datasource.type == 'mongodb':
            # For MongoDB, use the query endpoint with collection
            query_req = QueryRequest(collection=table_name, limit=limit)
            return await query_datasource(datasource, query_req, current_user)
        else:
            raise HTTPException(status_code=400, detail=f"Preview not supported for {datasource.type}")
        
        # Execute query
        query_req = QueryRequest(query=query, limit=limit)
        return await query_datasource(datasource, query_req, current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")
