from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.api.v1.endpoints.exec import get_current_user
from app.db.models import User
from app.services.data_catalog import (
    create_dataset,
    load_dataset,
    save_dataset,
    delete_dataset,
    list_datasets,
    add_version,
    search_datasets,
)

router = APIRouter()


class DatasetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    file_path: Optional[str] = None


class VersionCreate(BaseModel):
    file_path: str
    metadata: Optional[Dict[str, Any]] = None


@router.post("/", status_code=201)
def create_ds(payload: DatasetCreate, current_user: User = Depends(get_current_user)):
    ds = create_dataset(user_id=current_user.id, name=payload.name, description=payload.description, tags=payload.tags, file_path=payload.file_path)
    return ds


@router.get("/")
def list_ds(current_user: User = Depends(get_current_user)):
    return {"datasets": list_datasets(current_user.id)}


@router.get("/search")
def search_ds(q: Optional[str] = None, tags: Optional[str] = None, current_user: User = Depends(get_current_user)):
    tag_list = tags.split(",") if tags else None
    return {"datasets": search_datasets(current_user.id, query=q, tags=tag_list)}


@router.get("/{dataset_id}")
def get_ds(dataset_id: str, current_user: User = Depends(get_current_user)):
    ds = load_dataset(current_user.id, dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return ds


@router.post("/{dataset_id}/versions", status_code=201)
def add_ds_version(dataset_id: str, payload: VersionCreate, current_user: User = Depends(get_current_user)):
    try:
        v = add_version(current_user.id, dataset_id, payload.file_path, payload.metadata)
        return v
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")


@router.delete("/{dataset_id}", status_code=204)
def delete_ds(dataset_id: str, current_user: User = Depends(get_current_user)):
    ok = delete_dataset(current_user.id, dataset_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {}
