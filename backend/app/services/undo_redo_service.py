"""
Undo/Redo Service - Track and reverse data operations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import logging
import pandas as pd
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)


class UndoRedoService:
    """Manage undo/redo operations for data transformations"""
    
    # In-memory storage (in production, use Redis or database)
    _operation_stacks: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    
    @classmethod
    def _get_stack_key(cls, user_id: int, file_id: int) -> str:
        """Generate unique key for operation stack"""
        return f"{user_id}_{file_id}"
    
    @classmethod
    def _ensure_stack_exists(cls, stack_key: str):
        """Ensure operation stack exists for user/file"""
        if stack_key not in cls._operation_stacks:
            cls._operation_stacks[stack_key] = {
                "undo_stack": [],
                "redo_stack": []
            }
    
    @classmethod
    def record_operation(
        cls,
        user_id: int,
        file_id: int,
        file_path: str,
        operation_type: str,
        parameters: Dict[str, Any],
        previous_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record an operation for undo/redo
        
        Args:
            user_id: User ID
            file_id: File ID
            file_path: Path to the file
            operation_type: Type of operation (rename_column, delete_column, etc.)
            parameters: Operation parameters
            previous_state: State before operation (for reversal)
        """
        try:
            stack_key = cls._get_stack_key(user_id, file_id)
            cls._ensure_stack_exists(stack_key)
            
            # Create backup of file before operation
            backup_path = cls._create_backup(file_path, file_id)
            
            operation = {
                "operation_type": operation_type,
                "file_id": file_id,
                "file_path": file_path,
                "parameters": parameters,
                "previous_state": previous_state,
                "backup_path": backup_path,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "can_undo": True
            }
            
            # Add to undo stack
            cls._operation_stacks[stack_key]["undo_stack"].append(operation)
            
            # Clear redo stack when new operation is recorded
            cls._operation_stacks[stack_key]["redo_stack"] = []
            
            # Keep only last 50 operations
            if len(cls._operation_stacks[stack_key]["undo_stack"]) > 50:
                # Remove oldest backup
                oldest = cls._operation_stacks[stack_key]["undo_stack"].pop(0)
                cls._cleanup_backup(oldest.get("backup_path"))
            
            logger.info(f"Recorded operation: {operation_type} for file {file_id}")
            return {
                "recorded": True,
                "operation_type": operation_type,
                "can_undo": True,
                "can_redo": False
            }
            
        except Exception as e:
            logger.error(f"Error recording operation: {e}")
            raise
    
    @classmethod
    def undo(
        cls,
        user_id: int,
        file_id: int
    ) -> Dict[str, Any]:
        """Undo the last operation"""
        try:
            stack_key = cls._get_stack_key(user_id, file_id)
            cls._ensure_stack_exists(stack_key)
            
            undo_stack = cls._operation_stacks[stack_key]["undo_stack"]
            redo_stack = cls._operation_stacks[stack_key]["redo_stack"]
            
            if not undo_stack:
                return {
                    "success": False,
                    "message": "No operations to undo"
                }
            
            # Pop last operation
            operation = undo_stack.pop()
            
            # Restore from backup
            if operation.get("backup_path"):
                backup_path = Path(operation["backup_path"])
                if backup_path.exists():
                    shutil.copy2(backup_path, operation["file_path"])
                    logger.info(f"Restored file from backup: {backup_path}")
            
            # Move to redo stack
            redo_stack.append(operation)
            
            return {
                "success": True,
                "operation_type": operation["operation_type"],
                "parameters": operation["parameters"],
                "can_undo": len(undo_stack) > 0,
                "can_redo": True
            }
            
        except Exception as e:
            logger.error(f"Error undoing operation: {e}")
            raise
    
    @classmethod
    def redo(
        cls,
        user_id: int,
        file_id: int
    ) -> Dict[str, Any]:
        """Redo the last undone operation"""
        try:
            stack_key = cls._get_stack_key(user_id, file_id)
            cls._ensure_stack_exists(stack_key)
            
            undo_stack = cls._operation_stacks[stack_key]["undo_stack"]
            redo_stack = cls._operation_stacks[stack_key]["redo_stack"]
            
            if not redo_stack:
                return {
                    "success": False,
                    "message": "No operations to redo"
                }
            
            # Pop last undone operation
            operation = redo_stack.pop()
            
            # Re-apply the operation
            cls._reapply_operation(operation)
            
            # Move back to undo stack
            undo_stack.append(operation)
            
            return {
                "success": True,
                "operation_type": operation["operation_type"],
                "parameters": operation["parameters"],
                "can_undo": True,
                "can_redo": len(redo_stack) > 0
            }
            
        except Exception as e:
            logger.error(f"Error redoing operation: {e}")
            raise
    
    @classmethod
    def get_history(
        cls,
        user_id: int,
        file_id: int
    ) -> Dict[str, Any]:
        """Get operation history"""
        stack_key = cls._get_stack_key(user_id, file_id)
        cls._ensure_stack_exists(stack_key)
        
        undo_stack = cls._operation_stacks[stack_key]["undo_stack"]
        redo_stack = cls._operation_stacks[stack_key]["redo_stack"]
        
        return {
            "undo_operations": [
                {
                    "operation_type": op["operation_type"],
                    "parameters": op["parameters"],
                    "timestamp": op["timestamp"]
                }
                for op in undo_stack
            ],
            "redo_operations": [
                {
                    "operation_type": op["operation_type"],
                    "parameters": op["parameters"],
                    "timestamp": op["timestamp"]
                }
                for op in redo_stack
            ],
            "can_undo": len(undo_stack) > 0,
            "can_redo": len(redo_stack) > 0
        }
    
    @classmethod
    def clear_history(
        cls,
        user_id: int,
        file_id: int
    ) -> Dict[str, Any]:
        """Clear operation history"""
        stack_key = cls._get_stack_key(user_id, file_id)
        
        if stack_key in cls._operation_stacks:
            # Cleanup all backups
            for operation in cls._operation_stacks[stack_key]["undo_stack"]:
                cls._cleanup_backup(operation.get("backup_path"))
            for operation in cls._operation_stacks[stack_key]["redo_stack"]:
                cls._cleanup_backup(operation.get("backup_path"))
            
            # Clear stacks
            cls._operation_stacks[stack_key] = {
                "undo_stack": [],
                "redo_stack": []
            }
        
        return {"cleared": True}
    
    @classmethod
    def _create_backup(cls, file_path: str, file_id: int) -> str:
        """Create a backup of the file"""
        try:
            file_path_obj = Path(file_path)
            backup_dir = file_path_obj.parent / "backups" / str(file_id)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
            backup_filename = f"backup_{timestamp}_{file_path_obj.name}"
            backup_path = backup_dir / backup_filename
            
            shutil.copy2(file_path, backup_path)
            
            return str(backup_path)
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return ""
    
    @classmethod
    def _cleanup_backup(cls, backup_path: Optional[str]):
        """Remove backup file"""
        if backup_path:
            try:
                Path(backup_path).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Error cleaning up backup {backup_path}: {e}")
    
    @classmethod
    def _reapply_operation(cls, operation: Dict[str, Any]):
        """Re-apply an operation (for redo)"""
        try:
            file_path = operation["file_path"]
            operation_type = operation["operation_type"]
            parameters = operation["parameters"]
            
            df = pd.read_csv(file_path)
            
            if operation_type == "rename_column":
                old_name = parameters.get("old_name")
                new_name = parameters.get("new_name")
                if old_name in df.columns:
                    df.rename(columns={old_name: new_name}, inplace=True)
            
            elif operation_type == "delete_column":
                column_name = parameters.get("column_name")
                if column_name in df.columns:
                    df.drop(columns=[column_name], inplace=True)
            
            elif operation_type == "cast_column":
                column_name = parameters.get("column_name")
                target_type = parameters.get("target_type")
                if column_name in df.columns:
                    if target_type == "int":
                        df[column_name] = pd.to_numeric(df[column_name], errors='coerce').astype('Int64')
                    elif target_type == "float":
                        df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
                    elif target_type == "string":
                        df[column_name] = df[column_name].astype(str)
                    elif target_type == "datetime":
                        df[column_name] = pd.to_datetime(df[column_name], errors='coerce')
                    elif target_type == "bool":
                        df[column_name] = df[column_name].astype(bool)
            
            elif operation_type == "derive_column":
                new_column = parameters.get("new_column")
                formula = parameters.get("formula")
                if new_column and formula:
                    df[new_column] = df.eval(formula)
            
            # Save modified dataframe
            df.to_csv(file_path, index=False)
            
        except Exception as e:
            logger.error(f"Error re-applying operation: {e}")
            raise
