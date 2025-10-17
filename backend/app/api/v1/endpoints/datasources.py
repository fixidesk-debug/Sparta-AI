"""
Data Sources API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import pandas as pd

from app.db.session import get_db
from app.core.security import get_current_user
from app.services.data_connectors import DataConnectors

router = APIRouter()


class DataSourceConfig(BaseModel):
    name: str
    type: str  # postgresql, mysql, mongodb, sqlite
    config: Dict[str, Any]


class QueryRequest(BaseModel):
    query: Optional[str] = None
    collection: Optional[str] = None
    limit: int = 1000


@router.post("/test")
async def test_connection(
    datasource: DataSourceConfig,
    current_user: Dict = Depends(get_current_user)
):
    """Test connection to a data source"""
    try:
        result = DataConnectors.test_connection(
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
    """Connect to a data source and test connection"""
    try:
        # Test connection first
        test_result = DataConnectors.test_connection(
            connector_type=datasource.type,
            config=datasource.config
        )
        
        if not test_result.get("success"):
            raise HTTPException(status_code=400, detail=test_result.get("message"))
        
        # In production, save connection config to database
        return {
            "connected": True,
            "datasource_id": 1,  # Would be from database
            "name": datasource.name,
            "type": datasource.type,
            "message": "Connection successful"
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
    """List tables/collections in a data source"""
    try:
        tables = DataConnectors.list_tables(
            connector_type=datasource.type,
            config=datasource.config
        )
        return {
            "tables": tables,
            "count": len(tables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schema")
async def get_schema(
    datasource: DataSourceConfig,
    table_name: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get schema for a table/collection"""
    try:
        schema = DataConnectors.get_table_schema(
            connector_type=datasource.type,
            config=datasource.config,
            table_name=table_name
        )
        return {
            "table_name": table_name,
            "schema": schema
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def query_datasource(
    datasource: DataSourceConfig,
    query_request: QueryRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Execute a query on a data source"""
    try:
        df = None
        
        if datasource.type == 'postgresql':
            df = DataConnectors.connect_postgresql(
                host=datasource.config['host'],
                port=datasource.config['port'],
                database=datasource.config['database'],
                username=datasource.config['username'],
                password=datasource.config['password'],
                query=query_request.query
            )
        elif datasource.type == 'mysql':
            df = DataConnectors.connect_mysql(
                host=datasource.config['host'],
                port=datasource.config['port'],
                database=datasource.config['database'],
                username=datasource.config['username'],
                password=datasource.config['password'],
                query=query_request.query
            )
        elif datasource.type == 'mongodb':
            df = DataConnectors.connect_mongodb(
                host=datasource.config['host'],
                port=datasource.config['port'],
                database=datasource.config['database'],
                collection=query_request.collection or datasource.config.get('collection'),
                username=datasource.config.get('username'),
                password=datasource.config.get('password'),
                limit=query_request.limit
            )
        elif datasource.type == 'sqlite':
            df = DataConnectors.connect_sqlite(
                database_path=datasource.config['database_path'],
                query=query_request.query
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported datasource type: {datasource.type}")
        
        if df is not None:
            # Convert to JSON-serializable format
            data = df.head(query_request.limit).to_dict('records')
            columns = list(df.columns)
            
            return {
                "data": data,
                "columns": columns,
                "row_count": len(df),
                "returned_rows": len(data)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch data")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
