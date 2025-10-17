from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4
from datetime import datetime


BASE_DIR = Path("data") / "notebooks"


def _ensure_user_dir(user_id: int) -> Path:
    p = BASE_DIR / str(user_id)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _notebook_path(user_id: int, notebook_id: str) -> Path:
    return _ensure_user_dir(user_id) / f"{notebook_id}.json"


def create_notebook(user_id: int, title: str = "Untitled", cells: Optional[List[Dict[str, Any]]] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    nb_id = str(uuid4())
    created = _now_iso()
    cells = cells or []
    # ensure cell ids
    for c in cells:
        if "id" not in c:
            c["id"] = str(uuid4())
        c.setdefault("outputs", [])
        c.setdefault("metadata", {})
    nb = {
        "id": nb_id,
        "owner_id": user_id,
        "title": title,
        "metadata": metadata or {},
        "created_at": created,
        "updated_at": created,
        "cells": cells,
    }
    save_notebook(user_id, nb_id, nb)
    return nb


def load_notebook(user_id: int, notebook_id: str) -> Optional[Dict[str, Any]]:
    p = _notebook_path(user_id, notebook_id)
    if not p.exists():
        return None
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_notebook(user_id: int, notebook_id: str, notebook: Dict[str, Any]) -> None:
    p = _notebook_path(user_id, notebook_id)
    tmp = p.with_suffix(".json.tmp")
    notebook["updated_at"] = _now_iso()
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(notebook, fh, ensure_ascii=False, indent=2)
    tmp.replace(p)


def delete_notebook(user_id: int, notebook_id: str) -> bool:
    p = _notebook_path(user_id, notebook_id)
    if p.exists():
        p.unlink()
        return True
    return False


def list_notebooks(user_id: int) -> List[Dict[str, Any]]:
    p = _ensure_user_dir(user_id)
    out: List[Dict[str, Any]] = []
    for f in p.glob("*.json"):
        try:
            with f.open("r", encoding="utf-8") as fh:
                nb = json.load(fh)
                # produce a brief summary for listing
                out.append({
                    "id": nb.get("id"),
                    "title": nb.get("title"),
                    "created_at": nb.get("created_at"),
                    "updated_at": nb.get("updated_at"),
                    "cell_count": len(nb.get("cells", [])),
                })
        except Exception:
            continue
    return out
