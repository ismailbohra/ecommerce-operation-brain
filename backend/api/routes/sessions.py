import json

from fastapi import APIRouter, HTTPException

from db import Database

from ..models import (
    CreateSessionRequest,
    RenameSessionRequest,
    SessionDetail,
    SessionListItem,
    SessionMessage,
)

router = APIRouter()
db = Database()


def _fmt_session(row: dict) -> SessionListItem:
    return SessionListItem(
        id=str(row["id"]),
        title=row["title"],
        created_at=row["created_at"].isoformat()
        if hasattr(row["created_at"], "isoformat")
        else str(row["created_at"]),
        updated_at=row["updated_at"].isoformat()
        if hasattr(row["updated_at"], "isoformat")
        else str(row["updated_at"]),
    )


def _fmt_message(row: dict) -> SessionMessage:
    def _load(val):
        if val is None:
            return None
        if isinstance(val, str):
            return json.loads(val)
        return val  # already parsed by asyncpg JSONB

    agents = _load(row.get("agents")) or []
    actions = _load(row.get("actions"))
    action_results = _load(row.get("action_results"))

    return SessionMessage(
        id=str(row["id"]),
        role=row["role"],
        content=row["content"],
        agents=agents,
        actions=actions,
        action_results=action_results,
        created_at=row["created_at"].isoformat()
        if hasattr(row["created_at"], "isoformat")
        else str(row["created_at"]),
    )


@router.get("/sessions", response_model=list[SessionListItem])
async def list_sessions():
    rows = await db.get_sessions()
    return [_fmt_session(r) for r in rows]


@router.post("/sessions", response_model=SessionListItem, status_code=201)
async def create_session(payload: CreateSessionRequest):
    row = await db.create_session(payload.session_id, payload.title)
    return _fmt_session(row)


@router.get("/sessions/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str):
    session = await db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = await db.get_messages(session_id)
    return SessionDetail(
        id=str(session["id"]),
        title=session["title"],
        created_at=session["created_at"].isoformat()
        if hasattr(session["created_at"], "isoformat")
        else str(session["created_at"]),
        updated_at=session["updated_at"].isoformat()
        if hasattr(session["updated_at"], "isoformat")
        else str(session["updated_at"]),
        messages=[_fmt_message(m) for m in messages],
    )


@router.patch("/sessions/{session_id}", response_model=SessionListItem)
async def rename_session(session_id: str, payload: RenameSessionRequest):
    session = await db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.update_session_title(session_id, payload.title.strip() or "New Chat")
    updated = await db.get_session(session_id)
    return _fmt_session(updated)


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str):
    session = await db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete_session(session_id)
