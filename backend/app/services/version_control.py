"""
Version Control - Analysis Version History
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import logging
import shutil
from pathlib import Path
import hashlib
import difflib

logger = logging.getLogger(__name__)


class VersionControl:
    """Manage file and analysis versions with full functionality"""
    
    @staticmethod
    def create_file_version(
        file_path: str,
        file_id: int,
        description: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a snapshot version of a file"""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Create versions directory
            versions_dir = file_path_obj.parent / "versions" / str(file_id)
            versions_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate version metadata
            timestamp = datetime.now(timezone.utc)
            version_name = timestamp.strftime("%Y%m%d_%H%M%S")
            
            # Calculate file hash for integrity
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Create version filename
            version_filename = f"v_{version_name}_{file_path_obj.name}"
            version_path = versions_dir / version_filename
            
            # Copy file to version
            shutil.copy2(file_path, version_path)
            
            # Save metadata
            metadata = {
                "version_name": version_name,
                "original_filename": file_path_obj.name,
                "file_id": file_id,
                "user_id": user_id,
                "description": description or "Auto-saved version",
                "file_hash": file_hash,
                "file_size": file_path_obj.stat().st_size,
                "created_at": timestamp.isoformat(),
                "version_path": str(version_path)
            }
            
            # Save metadata JSON
            metadata_path = versions_dir / f"{version_filename}.meta.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Created version {version_name} for file {file_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error creating file version: {e}")
            raise
    
    @staticmethod
    def list_file_versions(file_id: int, file_path: str) -> List[Dict[str, Any]]:
        """List all versions of a file"""
        try:
            file_path_obj = Path(file_path)
            versions_dir = file_path_obj.parent / "versions" / str(file_id)
            
            if not versions_dir.exists():
                return []
            
            versions = []
            for meta_file in sorted(versions_dir.glob("*.meta.json"), reverse=True):
                try:
                    with open(meta_file, 'r') as f:
                        metadata = json.load(f)
                        versions.append(metadata)
                except Exception as e:
                    logger.warning(f"Error reading metadata {meta_file}: {e}")
            
            return versions
            
        except Exception as e:
            logger.error(f"Error listing file versions: {e}")
            return []
    
    @staticmethod
    def restore_file_version(
        file_id: int,
        file_path: str,
        version_name: str,
        create_backup: bool = True
    ) -> Dict[str, Any]:
        """Restore a file to a specific version"""
        try:
            file_path_obj = Path(file_path)
            versions_dir = file_path_obj.parent / "versions" / str(file_id)
            
            # Find version file
            version_files = list(versions_dir.glob(f"v_{version_name}_*"))
            version_files = [f for f in version_files if not f.name.endswith('.meta.json')]
            
            if not version_files:
                raise FileNotFoundError(f"Version {version_name} not found")
            
            version_path = version_files[0]
            
            # Create backup of current file before restoring
            if create_backup and file_path_obj.exists():
                backup_metadata = VersionControl.create_file_version(
                    file_path,
                    file_id,
                    description="Auto-backup before restore"
                )
            
            # Restore version
            shutil.copy2(version_path, file_path)
            
            logger.info(f"Restored file {file_id} to version {version_name}")
            return {
                "restored": True,
                "version_name": version_name,
                "file_path": str(file_path),
                "backup_created": create_backup
            }
            
        except Exception as e:
            logger.error(f"Error restoring file version: {e}")
            raise
    
    @staticmethod
    def compare_file_versions(
        file_id: int,
        file_path: str,
        version1_name: str,
        version2_name: str
    ) -> Dict[str, Any]:
        """Compare two file versions"""
        try:
            file_path_obj = Path(file_path)
            versions_dir = file_path_obj.parent / "versions" / str(file_id)
            
            # Find version files
            v1_files = list(versions_dir.glob(f"v_{version1_name}_*"))
            v1_files = [f for f in v1_files if not f.name.endswith('.meta.json')]
            
            v2_files = list(versions_dir.glob(f"v_{version2_name}_*"))
            v2_files = [f for f in v2_files if not f.name.endswith('.meta.json')]
            
            if not v1_files or not v2_files:
                raise FileNotFoundError("One or both versions not found")
            
            # Read file contents
            with open(v1_files[0], 'r', encoding='utf-8', errors='ignore') as f:
                content1 = f.readlines()
            
            with open(v2_files[0], 'r', encoding='utf-8', errors='ignore') as f:
                content2 = f.readlines()
            
            # Generate diff
            diff = list(difflib.unified_diff(
                content1,
                content2,
                fromfile=f"Version {version1_name}",
                tofile=f"Version {version2_name}",
                lineterm=''
            ))
            
            # Count changes
            additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
            deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
            
            return {
                "version1": version1_name,
                "version2": version2_name,
                "diff": diff[:500],  # Limit diff size
                "additions": additions,
                "deletions": deletions,
                "total_changes": additions + deletions
            }
            
        except Exception as e:
            logger.error(f"Error comparing file versions: {e}")
            raise
    
    @staticmethod
    def delete_file_version(
        file_id: int,
        file_path: str,
        version_name: str
    ) -> Dict[str, Any]:
        """Delete a specific file version"""
        try:
            file_path_obj = Path(file_path)
            versions_dir = file_path_obj.parent / "versions" / str(file_id)
            
            # Find and delete version file
            version_files = list(versions_dir.glob(f"v_{version_name}_*"))
            
            deleted_count = 0
            for version_file in version_files:
                version_file.unlink()
                deleted_count += 1
            
            logger.info(f"Deleted version {version_name} for file {file_id}")
            return {
                "deleted": True,
                "version_name": version_name,
                "files_deleted": deleted_count
            }
            
        except Exception as e:
            logger.error(f"Error deleting file version: {e}")
            raise
