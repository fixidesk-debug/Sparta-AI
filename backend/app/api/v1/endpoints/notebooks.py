from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from app.api.v1.endpoints.exec import get_current_user, CodeExecutionResponse
from app.services.notebook_store import create_notebook, load_notebook, save_notebook, delete_notebook, list_notebooks
from app.services.code_executor import CodeExecutor
from app.services.notebook_db import NotebookDB
from uuid import uuid4
from app.db.models import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class CellCreate(BaseModel):
    type: str = Field("code")
    language: str = Field("python")
    source: str
    metadata: Optional[Dict[str, Any]] = None


class NotebookCreate(BaseModel):
    title: Optional[str] = Field("Untitled")
    metadata: Optional[Dict[str, Any]] = None
    cells: Optional[List[CellCreate]] = None


class ExecOptions(BaseModel):
    timeout_seconds: Optional[int] = Field(30, ge=1)
    max_memory_mb: Optional[int] = Field(512, ge=128)


@router.post("/", status_code=201)
def create_nb(payload: NotebookCreate, current_user: User = Depends(get_current_user)):
    nb = create_notebook(user_id=current_user.id, title=payload.title or "Untitled", cells=[c.dict() for c in (payload.cells or [])], metadata=payload.metadata)
    return nb


@router.get("/")
def list_nbs(current_user: User = Depends(get_current_user)):
    return {"notebooks": list_notebooks(current_user.id)}


@router.get("/{notebook_id}")
def get_nb(notebook_id: str, current_user: User = Depends(get_current_user)):
    nb = load_notebook(current_user.id, notebook_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return nb


@router.put("/{notebook_id}")
def update_nb(notebook_id: str, payload: NotebookCreate, current_user: User = Depends(get_current_user)):
    nb = load_notebook(current_user.id, notebook_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    # Replace title/metadata/cells if provided
    if payload.title is not None:
        nb["title"] = payload.title
    if payload.metadata is not None:
        nb["metadata"] = payload.metadata
    if payload.cells is not None:
        # assign ids if missing
        cells = [c.dict() for c in payload.cells]
        for c in cells:
            c.setdefault("id", None)
            c.setdefault("outputs", [])
            c.setdefault("metadata", {})
        nb["cells"] = cells
    save_notebook(current_user.id, notebook_id, nb)
    return nb


@router.delete("/{notebook_id}", status_code=204)
def delete_nb(notebook_id: str, current_user: User = Depends(get_current_user)):
    ok = delete_notebook(current_user.id, notebook_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return {}


@router.post("/{notebook_id}/cells/{cell_id}/run", response_model=CodeExecutionResponse)
def run_cell(notebook_id: str, cell_id: str, opts: ExecOptions = Depends(), current_user: User = Depends(get_current_user)):
    nb = load_notebook(current_user.id, notebook_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    cell = next((c for c in nb.get("cells", []) if c.get("id") == cell_id), None)
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")
    if cell.get("type") != "code":
        raise HTTPException(status_code=400, detail="Cell is not executable")

    executor = CodeExecutor(timeout_seconds=opts.timeout_seconds, max_memory_mb=opts.max_memory_mb)
    # prepare execution context with a db helper (read-only)
    context = {"db": NotebookDB(user_id=current_user.id)}
    try:
        result = executor.execute(code=cell.get("source", ""), context=context)
    except Exception as e:
        logger.exception("Execution failed")
        raise HTTPException(status_code=500, detail=str(e))

    # persist output into cell.outputs
    outputs = cell.setdefault("outputs", [])
    outputs.append(result)
    save_notebook(current_user.id, notebook_id, nb)
    return result


class CellUpdate(BaseModel):
    type: Optional[str] = None
    language: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MovePayload(BaseModel):
    position: int


@router.post("/{notebook_id}/cells", status_code=201)
def add_cell(notebook_id: str, payload: CellCreate, current_user: User = Depends(get_current_user)):
    nb = load_notebook(current_user.id, notebook_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    cell = payload.dict()
    cell_id = str(uuid4())
    cell["id"] = cell_id
    cell.setdefault("outputs", [])
    cell.setdefault("metadata", payload.metadata or {})
    nb.setdefault("cells", []).append(cell)
    save_notebook(current_user.id, notebook_id, nb)
    return cell


@router.patch("/{notebook_id}/cells/{cell_id}")
def update_cell(notebook_id: str, cell_id: str, payload: CellUpdate, current_user: User = Depends(get_current_user)):
    nb = load_notebook(current_user.id, notebook_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    cell = next((c for c in nb.get("cells", []) if c.get("id") == cell_id), None)
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")
    if payload.type is not None:
        cell["type"] = payload.type
    if payload.language is not None:
        cell["language"] = payload.language
    if payload.source is not None:
        cell["source"] = payload.source
    if payload.metadata is not None:
        cell["metadata"] = payload.metadata
    save_notebook(current_user.id, notebook_id, nb)
    return cell


@router.post("/{notebook_id}/cells/{cell_id}/move")
def move_cell(notebook_id: str, cell_id: str, payload: MovePayload, current_user: User = Depends(get_current_user)):
    nb = load_notebook(current_user.id, notebook_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    cells = nb.setdefault("cells", [])
    idx = next((i for i, c in enumerate(cells) if c.get("id") == cell_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Cell not found")
    cell = cells.pop(idx)
    # clamp position
    position = payload.position
    new_idx = max(0, min(position, len(cells)))
    cells.insert(new_idx, cell)
    save_notebook(current_user.id, notebook_id, nb)
    return {"cells": cells}


@router.delete("/{notebook_id}/cells/{cell_id}", status_code=204)
def delete_cell(notebook_id: str, cell_id: str, current_user: User = Depends(get_current_user)):
    nb = load_notebook(current_user.id, notebook_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    cells = nb.setdefault("cells", [])
    idx = next((i for i, c in enumerate(cells) if c.get("id") == cell_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Cell not found")
    cells.pop(idx)
    save_notebook(current_user.id, notebook_id, nb)
    return {}


@router.post("/{notebook_id}/run_all", response_model=List[CodeExecutionResponse])
def run_all(notebook_id: str, opts: ExecOptions = Depends(), current_user: User = Depends(get_current_user)):
    nb = load_notebook(current_user.id, notebook_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    results: List[CodeExecutionResponse] = []
    executor = CodeExecutor(timeout_seconds=opts.timeout_seconds, max_memory_mb=opts.max_memory_mb)
    for cell in nb.get("cells", []):
        if cell.get("type") != "code":
            continue
        try:
            res = executor.execute(code=cell.get("source", ""), context={"db": NotebookDB(user_id=current_user.id)})
        except Exception as e:
            res = {"success": False, "output": "", "error": str(e), "execution_time": 0.0, "images": [], "plotly_figures": [], "variables": {}, "timestamp": ""}
        cell.setdefault("outputs", []).append(res)
        results.append(res)
    save_notebook(current_user.id, notebook_id, nb)
    return results
