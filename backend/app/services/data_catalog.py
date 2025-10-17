from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4
from datetime import datetime

BASE_DIR = Path("data") / "catalog"


def _ensure_user_dir(user_id: int) -> Path:
    p = BASE_DIR / str(user_id)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _dataset_path(user_id: int, dataset_id: str) -> Path:
    return _ensure_user_dir(user_id) / f"{dataset_id}.json"


def create_dataset(user_id: int, name: str, description: Optional[str] = None, tags: Optional[List[str]] = None, file_path: Optional[str] = None) -> Dict[str, Any]:
    ds_id = str(uuid4())
    now = _now_iso()
    tags = tags or []
    dataset = {
        "id": ds_id,
        "owner_id": user_id,
        "name": name,
        "description": description or "",
        "tags": tags,
        "created_at": now,
        "updated_at": now,
        "versions": [],
    }
    if file_path:
        # initial version
        version = {"id": str(uuid4()), "file_path": file_path, "created_at": now, "metadata": {}}
        dataset["versions"].append(version)
    save_dataset(user_id, ds_id, dataset)
    return dataset


def load_dataset(user_id: int, dataset_id: str) -> Optional[Dict[str, Any]]:
    p = _dataset_path(user_id, dataset_id)
    if not p.exists():
        return None
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_dataset(user_id: int, dataset_id: str, dataset: Dict[str, Any]) -> None:
    p = _dataset_path(user_id, dataset_id)
    tmp = p.with_suffix(".json.tmp")
    dataset["updated_at"] = _now_iso()
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(dataset, fh, ensure_ascii=False, indent=2)
    tmp.replace(p)


def delete_dataset(user_id: int, dataset_id: str) -> bool:
    p = _dataset_path(user_id, dataset_id)
    if p.exists():
        p.unlink()
        return True
    return False


def list_datasets(user_id: int) -> List[Dict[str, Any]]:
    p = _ensure_user_dir(user_id)
    out: List[Dict[str, Any]] = []
    for f in p.glob("*.json"):
        try:
            with f.open("r", encoding="utf-8") as fh:
                ds = json.load(fh)
                out.append({
                    "id": ds.get("id"),
                    "name": ds.get("name"),
                    "description": ds.get("description"),
                    "tags": ds.get("tags", []),
                    "created_at": ds.get("created_at"),
                    "updated_at": ds.get("updated_at"),
                    "version_count": len(ds.get("versions", [])),
                })
        except Exception:
            continue
    return out


def add_version(user_id: int, dataset_id: str, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ds = load_dataset(user_id, dataset_id)
    if ds is None:
        raise FileNotFoundError("Dataset not found")
    now = _now_iso()
    version = {"id": str(uuid4()), "file_path": file_path, "created_at": now, "metadata": metadata or {}}
    ds.setdefault("versions", []).append(version)
    save_dataset(user_id, dataset_id, ds)
    return version


def search_datasets(user_id: int, query: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    all_ds = list_datasets(user_id)
    if not query and not tags:
        return all_ds
    out = []
    for ds_summary in all_ds:
        name = (ds_summary.get("name") or "").lower()
        desc = (ds_summary.get("description") or "").lower()
        tlist = [t.lower() for t in ds_summary.get("tags", [])]
        match = True
        if query:
            q = query.lower()
            if q not in name and q not in desc:
                match = False
        if tags:
            qtags = [t.lower() for t in tags]
            if not all(t in tlist for t in qtags):
                match = False
        if match:
            out.append(ds_summary)
    return out
