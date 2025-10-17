"""
SQL Generator - Natural Language to SQL
Converts natural language queries to SQL for database querying
"""
from typing import Dict, Any, List, Optional
import logging
from app.services.groq_provider import GroqProvider

logger = logging.getLogger(__name__)


class SQLGenerator:
    """Generate SQL from natural language"""
    
    def __init__(self, api_key: Optional[str] = None):
        from app.core.config import settings
        if not api_key:
            api_key = getattr(settings, 'GROQ_API_KEY', None)
        
        self.provider = GroqProvider(api_key, "llama-3.3-70b-versatile")
    
    async def generate_sql(
        self,
        query: str,
        schema: Dict[str, List[str]],
        dialect: str = "postgresql"
    ) -> Dict[str, Any]:
        """
        Generate SQL from natural language
        
        Args:
            query: Natural language query
            schema: Database schema {table_name: [column_names]}
            dialect: SQL dialect (postgresql, mysql, sqlite)
        
        Returns:
            Dict with sql, explanation, and confidence
        """
        try:
            schema_str = self._format_schema(schema)
            
            prompt = f"""You are an expert SQL generator. Convert the natural language query to {dialect} SQL.

Database Schema:
{schema_str}

User Query: {query}

Generate a valid SQL query. Return ONLY the SQL query, no explanations.
Use proper {dialect} syntax and best practices."""

            messages = [
                {"role": "system", "content": "You are an expert SQL generator. Return only valid SQL queries."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.provider.generate_completion(messages, temperature=0.1, max_tokens=500)
            
            sql = self._extract_sql(response)
            
            return {
                "sql": sql,
                "explanation": f"Generated SQL query for: {query}",
                "dialect": dialect,
                "confidence": 0.9 if sql else 0.0
            }
        
        except Exception as e:
            logger.error(f"SQL generation error: {e}")
            return {
                "sql": "",
                "explanation": f"Error: {str(e)}",
                "dialect": dialect,
                "confidence": 0.0
            }
    
    def _format_schema(self, schema: Dict[str, List[str]]) -> str:
        """Format schema for prompt"""
        lines = []
        for table, columns in schema.items():
            lines.append(f"Table: {table}")
            lines.append(f"Columns: {', '.join(columns)}")
            lines.append("")
        return "\n".join(lines)
    
    def _extract_sql(self, response: str) -> str:
        """Extract SQL from response"""
        # Remove markdown code blocks
        if "```sql" in response:
            response = response.split("```sql")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        return response.strip()
