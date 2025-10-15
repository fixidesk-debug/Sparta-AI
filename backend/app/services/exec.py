from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import File
import pandas as pd
from .code_executor import CodeExecutor

async def execute_code_safely(
    code: str,
    language: str,
    file_id: Optional[int],
    user_id: int,
    db: Session
) -> Dict[str, Any]:
    """
    Execute code in a safe sandboxed environment using CodeExecutor.
    """
    
    if language != "python":
        return {
            "output": "",
            "error": "Only Python code execution is currently supported",
            "execution_time": 0.0
        }
    
    try:
        # Prepare execution context
        context = {}
        
        # Load file data if provided
        if file_id:
            file = db.query(File).filter(
                File.id == file_id,
                File.user_id == user_id
            ).first()
            
            if file:
                file_path: str = str(file.file_path)
                df = pd.read_csv(file_path)
                context['df'] = df
        
        # Use secure CodeExecutor
        executor = CodeExecutor(timeout_seconds=30, max_memory_mb=512)
        result = executor.execute(code, context)
        
        return {
            "output": result['output'],
            "error": result['error'],
            "execution_time": result['execution_time'],
            "images": result.get('images', []),
            "plotly_figures": result.get('plotly_figures', [])
        }
        
    except Exception as e:
        return {
            "output": "",
            "error": str(e),
            "execution_time": 0.0
        }
