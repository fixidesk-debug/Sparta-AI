# Database Connectors Guide - SPARTA AI

## Overview
SPARTA AI now supports connections to **10+ external data sources**, allowing you to analyze data from various databases and cloud data warehouses without uploading files.

## Supported Data Sources

### 🗄️ SQL Databases
1. **PostgreSQL** - Open-source relational database
2. **MySQL** - Popular open-source database
3. **Microsoft SQL Server** - Enterprise database system
4. **SQLite** - Lightweight file-based database
5. **Supabase** - PostgreSQL-based cloud database

### 📊 NoSQL Databases
6. **MongoDB** - Document-oriented database

### ☁️ Cloud Data Warehouses
7. **Google BigQuery** - Serverless data warehouse
8. **Snowflake** - Cloud data platform
9. **Databricks** - Unified analytics platform

### 📈 Analytics Databases
10. **Vertica** - High-performance analytics database

---

## Installation

### 1. Install Required Packages

```bash
cd backend
pip install -r requirements_connectors.txt
```

### 2. Install Database Drivers (if needed)

#### For SQL Server (Windows):
Download and install [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

#### For SQL Server (Linux):
```bash
# Ubuntu/Debian
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

---

## API Endpoints

All endpoints are available under `/api/v1/connectors/`

### 1. List Available Connectors
```http
GET /api/v1/connectors/connectors
```

**Response:**
```json
{
  "connectors": [
    {
      "type": "postgresql",
      "name": "PostgreSQL",
      "type": "SQL Database",
      "required_fields": ["host", "port", "database", "username", "password"],
      "default_port": 5432
    },
    ...
  ],
  "count": 10
}
```

### 2. Get Connector Information
```http
GET /api/v1/connectors/connectors/{connector_type}
```

### 3. Test Connection
```http
POST /api/v1/connectors/test
```

**Request Body:**
```json
{
  "name": "My PostgreSQL DB",
  "type": "postgresql",
  "config": {
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "username": "user",
    "password": "password"
  }
}
```

### 4. Connect to Data Source
```http
POST /api/v1/connectors/connect
```

### 5. List Tables/Collections
```http
POST /api/v1/connectors/tables
```

### 6. Query Data Source
```http
POST /api/v1/connectors/query
```

**Request Body:**
```json
{
  "datasource": {
    "name": "My Database",
    "type": "postgresql",
    "config": { ... }
  },
  "query_request": {
    "query": "SELECT * FROM users LIMIT 100",
    "limit": 1000
  }
}
```

### 7. Preview Table Data
```http
POST /api/v1/connectors/preview?table_name=users&limit=100
```

### 8. Save Query Results
```http
POST /api/v1/connectors/query/save
```

---

## Connection Examples

### PostgreSQL
```json
{
  "name": "Production PostgreSQL",
  "type": "postgresql",
  "config": {
    "host": "db.example.com",
    "port": 5432,
    "database": "analytics",
    "username": "analyst",
    "password": "secure_password",
    "ssl_mode": "require"
  }
}
```

### MySQL
```json
{
  "name": "MySQL Database",
  "type": "mysql",
  "config": {
    "host": "mysql.example.com",
    "port": 3306,
    "database": "sales",
    "username": "user",
    "password": "password",
    "charset": "utf8mb4"
  }
}
```

### MongoDB
```json
{
  "name": "MongoDB Cluster",
  "type": "mongodb",
  "config": {
    "host": "mongodb.example.com",
    "port": 27017,
    "database": "analytics",
    "username": "user",
    "password": "password",
    "collection": "events"
  }
}
```

### Google BigQuery
```json
{
  "name": "BigQuery Warehouse",
  "type": "bigquery",
  "config": {
    "project_id": "my-project-123",
    "credentials_json": "{...service account JSON...}",
    "dataset_id": "analytics",
    "location": "US"
  }
}
```

### Snowflake
```json
{
  "name": "Snowflake DW",
  "type": "snowflake",
  "config": {
    "account": "xy12345.us-east-1",
    "warehouse": "COMPUTE_WH",
    "database": "ANALYTICS",
    "schema": "PUBLIC",
    "username": "analyst",
    "password": "password",
    "role": "ANALYST_ROLE"
  }
}
```

### Databricks
```json
{
  "name": "Databricks Lakehouse",
  "type": "databricks",
  "config": {
    "server_hostname": "dbc-abc123.cloud.databricks.com",
    "http_path": "/sql/1.0/warehouses/abc123",
    "access_token": "dapi...",
    "catalog": "main",
    "schema": "default"
  }
}
```

### Microsoft SQL Server
```json
{
  "name": "SQL Server",
  "type": "sqlserver",
  "config": {
    "host": "sqlserver.example.com",
    "port": 1433,
    "database": "Analytics",
    "username": "sa",
    "password": "password",
    "driver": "ODBC Driver 17 for SQL Server"
  }
}
```

### Supabase
```json
{
  "name": "Supabase DB",
  "type": "supabase",
  "config": {
    "host": "db.xxxx.supabase.co",
    "port": 5432,
    "database": "postgres",
    "username": "postgres",
    "password": "your-password"
  }
}
```

### Vertica
```json
{
  "name": "Vertica Analytics",
  "type": "vertica",
  "config": {
    "host": "vertica.example.com",
    "port": 5433,
    "database": "analytics",
    "username": "dbadmin",
    "password": "password"
  }
}
```

### SQLite
```json
{
  "name": "Local SQLite",
  "type": "sqlite",
  "config": {
    "database_path": "/path/to/database.db"
  }
}
```

---

## Usage Workflow

### 1. Test Connection
First, test if your connection credentials work:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/connectors/test",
    json={
        "name": "My Database",
        "type": "postgresql",
        "config": {
            "host": "localhost",
            "port": 5432,
            "database": "mydb",
            "username": "user",
            "password": "password"
        }
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

print(response.json())
# {"success": true, "message": "Successfully connected to postgresql"}
```

### 2. List Available Tables
```python
response = requests.post(
    "http://localhost:8000/api/v1/connectors/tables",
    json={
        "name": "My Database",
        "type": "postgresql",
        "config": {...}
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

tables = response.json()["tables"]
print(f"Found {len(tables)} tables: {tables}")
```

### 3. Query Data
```python
response = requests.post(
    "http://localhost:8000/api/v1/connectors/query",
    json={
        "datasource": {
            "name": "My Database",
            "type": "postgresql",
            "config": {...}
        },
        "query_request": {
            "query": "SELECT * FROM users WHERE created_at > '2024-01-01'",
            "limit": 1000
        }
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

data = response.json()
print(f"Retrieved {data['returned_rows']} rows")
print(f"Columns: {data['columns']}")
print(f"Data: {data['data'][:5]}")  # First 5 rows
```

### 4. Preview Table
```python
response = requests.post(
    "http://localhost:8000/api/v1/connectors/preview",
    params={"table_name": "users", "limit": 10},
    json={
        "name": "My Database",
        "type": "postgresql",
        "config": {...}
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

---

## Security Best Practices

### 1. **Never Hardcode Credentials**
- Use environment variables
- Store credentials in secure vaults (AWS Secrets Manager, Azure Key Vault, etc.)
- Implement credential encryption at rest

### 2. **Use Read-Only Accounts**
- Create database users with SELECT-only permissions
- Restrict access to specific schemas/tables

### 3. **Enable SSL/TLS**
- Always use encrypted connections for production databases
- Set `ssl_mode='require'` for PostgreSQL
- Use SSL certificates for MySQL

### 4. **Implement Rate Limiting**
- Limit query frequency per user
- Set maximum row limits
- Implement query timeouts

### 5. **Audit Logging**
- Log all connection attempts
- Track queries executed
- Monitor for suspicious activity

---

## Frontend Integration

### Example React Component

```typescript
import React, { useState } from 'react';

const DatabaseConnector = () => {
  const [connectorType, setConnectorType] = useState('postgresql');
  const [config, setConfig] = useState({
    host: '',
    port: 5432,
    database: '',
    username: '',
    password: ''
  });
  const [testResult, setTestResult] = useState(null);

  const testConnection = async () => {
    const response = await fetch('/api/v1/connectors/test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        name: 'Test Connection',
        type: connectorType,
        config: config
      })
    });
    
    const result = await response.json();
    setTestResult(result);
  };

  return (
    <div>
      <h2>Connect to Database</h2>
      <select value={connectorType} onChange={(e) => setConnectorType(e.target.value)}>
        <option value="postgresql">PostgreSQL</option>
        <option value="mysql">MySQL</option>
        <option value="mongodb">MongoDB</option>
        <option value="bigquery">BigQuery</option>
        <option value="snowflake">Snowflake</option>
      </select>
      
      {/* Config inputs */}
      <input 
        placeholder="Host" 
        value={config.host}
        onChange={(e) => setConfig({...config, host: e.target.value})}
      />
      
      <button onClick={testConnection}>Test Connection</button>
      
      {testResult && (
        <div className={testResult.success ? 'success' : 'error'}>
          {testResult.message}
        </div>
      )}
    </div>
  );
};
```

---

## Troubleshooting

### Common Issues

#### 1. Connection Timeout
- **Cause**: Firewall blocking connection, wrong host/port
- **Solution**: Check firewall rules, verify host and port are correct

#### 2. Authentication Failed
- **Cause**: Wrong username/password, insufficient permissions
- **Solution**: Verify credentials, check user permissions

#### 3. SSL/TLS Errors
- **Cause**: SSL required but not configured
- **Solution**: Add `ssl_mode='require'` or install SSL certificates

#### 4. Driver Not Found (SQL Server)
- **Cause**: ODBC driver not installed
- **Solution**: Install ODBC Driver 17 for SQL Server

#### 5. Module Not Found
- **Cause**: Connector package not installed
- **Solution**: Run `pip install -r requirements_connectors.txt`

---

## Performance Tips

1. **Use LIMIT clauses** - Always limit query results
2. **Create indexes** - Index frequently queried columns
3. **Use connection pooling** - Reuse database connections
4. **Cache results** - Cache frequently accessed data
5. **Optimize queries** - Use EXPLAIN to analyze query performance

---

## Next Steps

1. ✅ Install connector packages
2. ✅ Test connection to your database
3. ✅ List available tables
4. ✅ Query and analyze data
5. ✅ Integrate with AI chat for natural language queries

---

## Support

For issues or questions:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Check logs in `logs/sparta_ai.log`

---

## Future Enhancements

Coming soon:
- **Redis** - In-memory data store
- **Elasticsearch** - Search and analytics engine
- **ClickHouse** - OLAP database
- **Apache Cassandra** - Distributed NoSQL
- **Amazon Redshift** - AWS data warehouse
- **Azure Synapse** - Azure analytics service
