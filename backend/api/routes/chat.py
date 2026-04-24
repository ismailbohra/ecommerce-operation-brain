import asyncio
import json
from typing import AsyncIterator

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from db import Database
from graph import resume_with_actions, run_query

from ..models import (
    ActionApprovalRequest,
    ActionApprovalResponse,
    ChatRequest,
    ChatResponse,
    ProposedAction,
)

router = APIRouter()
db = Database()


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


async def _ensure_session(session_id: str, first_message: str):
    """Create session if it doesn't exist yet; set title from first message."""
    if not await db.session_exists(session_id):
        title = first_message[:60].strip() or "New Chat"
        await db.create_session(session_id, title)


async def _persist_exchange(
    session_id: str,
    user_text: str,
    assistant_text: str,
    agents: list[str],
    proposed_actions: list[ProposedAction],
):
    """Save user + assistant messages to the session."""
    await db.save_message(session_id, "user", user_text)
    await db.save_message(
        session_id,
        "assistant",
        assistant_text,
        agents=agents,
        actions=[a.model_dump() for a in proposed_actions]
        if proposed_actions
        else None,
    )
    await db.update_session_timestamp(session_id)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    workflow = request.app.state.workflow
    history = _serialize_history(payload.chat_history)

    await _ensure_session(payload.thread_id, payload.query)

    result = await asyncio.to_thread(
        run_query, workflow, payload.query, payload.thread_id, history
    )

    agents = result.get("agents_to_call", []) or []
    response_text = result.get("response", "")
    proposed = _to_proposed_actions(result.get("proposed_actions", []))

    await _persist_exchange(
        payload.thread_id, payload.query, response_text, agents, proposed
    )

    return ChatResponse(
        response=response_text,
        agents_consulted=agents,
        proposed_actions=proposed,
        thread_id=payload.thread_id,
    )


def _sse_event(event: str, data) -> dict:
    return {"event": event, "data": json.dumps(data)}


@router.post("/chat/stream")
async def chat_stream(request: Request, payload: ChatRequest):
    """
    Stream the chat response with real-time per-agent progress events.

    SSE event types emitted (in order):
      status       – initial "thinking" stage
      router_start – router LLM call started
      router_done  – router chose agents
      agents_start – parallel agent execution started
      agent_start  – individual agent started     { name }
      agent_done   – individual agent finished    { name }
      agents_done  – all agents finished
      synthesis_start / synthesis_done
      action_start  / action_done                 { count }
      agents       – final list of consulted agents
      token        – response text chunk
      actions      – proposed actions (if any)
      done         – end of stream
    """
    workflow = request.app.state.workflow
    history = _serialize_history(payload.chat_history)

    await _ensure_session(payload.thread_id, payload.query)

    async def event_generator() -> AsyncIterator[dict]:
        yield _sse_event("status", {"stage": "thinking"})

        # Per-request queue for progress events emitted by workflow nodes.
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        # Wrap the workflow so we can put a sentinel when it finishes.
        async def _run_and_signal():
            try:
                return await asyncio.to_thread(
                    run_query,
                    workflow,
                    payload.query,
                    payload.thread_id,
                    history,
                    queue,
                    loop,
                )
            finally:
                # Sentinel tells the drain loop the stream is done.
                await queue.put(None)

        task = asyncio.create_task(_run_and_signal())

        # Drain progress events until the sentinel arrives.
        while True:
            item = await queue.get()
            if item is None:
                break
            yield _sse_event(item["type"], {k: v for k, v in item.items() if k != "type"})

        # Collect the workflow result (re-raises any exception from the task).
        try:
            result = await task
        except Exception as exc:
            yield _sse_event("error", {"message": str(exc)})
            return

        agents = result.get("agents_to_call", []) or []
        if agents:
            yield _sse_event("agents", {"agents": agents})

        response_text = result.get("response", "")
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

        await _persist_exchange(
            payload.thread_id, payload.query, response_text, agents, proposed
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
    action_results = result.get("action_results", []) or []

    # Persist action results to the last assistant message's action_results
    await db.save_message(
        payload.thread_id,
        "assistant",
        "\n".join(action_results),
        agents=[],
        action_results=action_results,
    )
    await db.update_session_timestamp(payload.thread_id)

    return ActionApprovalResponse(action_results=action_results)
