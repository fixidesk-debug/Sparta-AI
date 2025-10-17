@echo off
echo ========================================
echo SPARTA AI - Database Connectors Setup
echo ========================================
echo.

cd backend

echo Installing database connector packages...
echo.

pip install psycopg2-binary>=2.9.0
pip install PyMySQL>=1.0.0
pip install pymongo>=4.0.0
pip install google-cloud-bigquery>=3.0.0
pip install snowflake-connector-python>=3.0.0
pip install databricks-sql-connector>=2.0.0
pip install vertica-python>=1.3.0
pip install pyarrow>=10.0.0

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Installed connectors for:
echo - PostgreSQL
echo - MySQL
echo - MongoDB
echo - Google BigQuery
echo - Snowflake
echo - Databricks
echo - Vertica
echo.
echo Note: For SQL Server, you need to install ODBC Driver 17
echo Download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
echo.
echo See DATABASE_CONNECTORS_GUIDE.md for usage instructions
echo.
pause
