import asyncio
import json
from typing import AsyncIterator

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from graph import resume_with_actions, run_query

from ..models import (
    ActionApprovalRequest,
    ActionApprovalResponse,
    ChatRequest,
    ChatResponse,
    ProposedAction,
)

router = APIRouter()


def _serialize_history(history) -> list[dict]:
    return [{"role": m.role, "content": m.content} for m in history]


def _to_proposed_actions(raw: list[dict]) -> list[ProposedAction]:
    actions: list[ProposedAction] = []
    for a in raw or []:
        actions.append(
            ProposedAction(
                id=str(a.get("id", "")),
                type=str(a.get("type", "")),
                description=str(a.get("description", "")),
                reason=str(a.get("reason", "")),
                params=a.get("params", {}) or {},
            )
        )
    return actions


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    workflow = request.app.state.workflow
    history = _serialize_history(payload.chat_history)

    result = await asyncio.to_thread(
        run_query, workflow, payload.query, payload.thread_id, history
    )

    return ChatResponse(
        response=result.get("response", ""),
        agents_consulted=result.get("agents_to_call", []) or [],
        proposed_actions=_to_proposed_actions(result.get("proposed_actions", [])),
        thread_id=payload.thread_id,
    )


def _sse_event(event: str, data) -> dict:
    return {"event": event, "data": json.dumps(data)}


@router.post("/chat/stream")
async def chat_stream(request: Request, payload: ChatRequest):
    """
    Stream the chat response. We do not stream raw LLM tokens (the workflow has
    multiple internal nodes), but we emit progress events as soon as work
    completes so the UI feels responsive:
      - status: workflow stage updates
      - agents: which agents were consulted
      - response: full assistant text (single chunk for now)
      - actions: any proposed actions
      - done: end of stream
    """
    workflow = request.app.state.workflow
    history = _serialize_history(payload.chat_history)

    async def event_generator() -> AsyncIterator[dict]:
        yield _sse_event("status", {"stage": "thinking"})

        try:
            result = await asyncio.to_thread(
                run_query, workflow, payload.query, payload.thread_id, history
            )
        except Exception as exc:  # noqa: BLE001
            yield _sse_event("error", {"message": str(exc)})
            return

        agents = result.get("agents_to_call", []) or []
        if agents:
            yield _sse_event("agents", {"agents": agents})

        response_text = result.get("response", "")
        # Chunked emission so the UI can render progressively.
        chunk_size = 80
        for i in range(0, len(response_text), chunk_size):
            yield _sse_event("token", {"text": response_text[i : i + chunk_size]})
            await asyncio.sleep(0.01)

        proposed = _to_proposed_actions(result.get("proposed_actions", []))
        if proposed:
            yield _sse_event(
                "actions",
                {"actions": [a.model_dump() for a in proposed]},
            )

        yield _sse_event(
            "done",
            {
                "thread_id": payload.thread_id,
                "agents_consulted": agents,
                "response": response_text,
            },
        )

    return EventSourceResponse(event_generator())


@router.post("/chat/actions", response_model=ActionApprovalResponse)
async def approve_actions(
    request: Request, payload: ActionApprovalRequest
) -> ActionApprovalResponse:
    workflow = request.app.state.workflow
    result = await asyncio.to_thread(
        resume_with_actions, workflow, payload.thread_id, payload.approved_action_ids
    )
    return ActionApprovalResponse(action_results=result.get("action_results", []) or [])
