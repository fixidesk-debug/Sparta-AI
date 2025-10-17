from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.db.models import Dataset, DatasetVersion, File
from datetime import datetime, timezone

def create_dataset_db(db: Session, user_id: int, name: str, description: Optional[str] = None, tags: Optional[List[str]] = None, file_id: Optional[int] = None, file_path: Optional[str] = None) -> Dict[str, Any]:
    ds = Dataset(user_id=user_id, name=name, description=description or "", tags=tags or [])
    db.add(ds)
    db.commit()
    db.refresh(ds)
    if file_id or file_path:
        create_version_db(db, ds.id, file_id=file_id, file_path=file_path)
    return {"id": ds.id, "name": ds.name, "description": ds.description, "tags": ds.tags, "created_at": ds.created_at.isoformat(), "updated_at": ds.updated_at.isoformat()}


def get_dataset_db(db: Session, user_id: int, dataset_id: int) -> Optional[Dict[str, Any]]:
    ds = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == user_id).first()
    if not ds:
        return None
    versions = []
    for v in ds.versions:
        versions.append({"id": v.id, "file_id": v.file_id, "file_path": v.file_path, "metadata": v.meta, "created_at": v.created_at.isoformat()})
    return {"id": ds.id, "name": ds.name, "description": ds.description, "tags": ds.tags, "versions": versions, "created_at": ds.created_at.isoformat(), "updated_at": ds.updated_at.isoformat()}


def list_datasets_db(db: Session, user_id: int) -> List[Dict[str, Any]]:
    rows = db.query(Dataset).filter(Dataset.user_id == user_id).all()
    out = []
    for ds in rows:
        out.append({"id": ds.id, "name": ds.name, "description": ds.description, "tags": ds.tags or [], "created_at": ds.created_at.isoformat(), "updated_at": ds.updated_at.isoformat(), "version_count": len(ds.versions)})
    return out


def create_version_db(db: Session, dataset_id: int, file_id: Optional[int] = None, file_path: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    v = DatasetVersion(dataset_id=dataset_id, file_id=file_id, file_path=file_path, meta=metadata or {})
    db.add(v)
    db.commit()
    db.refresh(v)
    return {"id": v.id, "file_id": v.file_id, "file_path": v.file_path, "meta": v.meta, "created_at": v.created_at.isoformat()}


def search_datasets_db(db: Session, user_id: int, query: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    q = db.query(Dataset).filter(Dataset.user_id == user_id)
    if query:
        likeq = f"%{query}%"
        q = q.filter((Dataset.name.ilike(likeq)) | (Dataset.description.ilike(likeq)))
    results = q.all()
    out = []
    for ds in results:
        if tags:
            ds_tags = [t.lower() for t in (ds.tags or [])]
            if not all(t.lower() in ds_tags for t in tags):
                continue
        out.append({"id": ds.id, "name": ds.name, "description": ds.description, "tags": ds.tags or [], "created_at": ds.created_at.isoformat(), "updated_at": ds.updated_at.isoformat(), "version_count": len(ds.versions)})
    return out
