"""
Entry point for the Agentic Ops Orchestrator API.

Exposes the LangGraph agent over HTTP, plus the health check
endpoint, and the endpoints the ops dashboard needs: the pending
queue and today's stats. Every submitted request is logged to
requests_log so the dashboard reflects real activity.
"""

import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from langgraph.types import Command
from app.agents.graph import graph
from app.models.schemas import SubmitRequestIn, SubmitRequestOut, DecisionIn, DecisionOut
from app.models.taxonomy import TAXONOMY, RequestType
from app.tools.db import init_db
from app.tools.request_log import log_new_request, resolve_request, get_pending_requests, get_stats
from fastapi.middleware.cors import CORSMiddleware
from app.tools.request_log import log_new_request, resolve_request, get_pending_requests, get_stats, get_request_history


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensures the database schema exists every time the app starts."""
    init_db()
    yield


app = FastAPI(title="Agentic Ops Orchestrator", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # portfolio project, fine to allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Simple endpoint to confirm the API is up and responding."""
    return {"status": "ok", "service": "agentic-ops-orchestrator"}


@app.post("/requests", response_model=SubmitRequestOut)
def submit_request(payload: SubmitRequestIn):
    """
    Submits a new customer request to the agent. Logs it either way,
    then returns immediately if low-risk, or pauses for approval.
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    state = graph.invoke(
        {"customer_id": payload.customer_id, "message": payload.message},
        config=config,
    )

    request_type = state.get("request_type")
    ai_recommendation = TAXONOMY[RequestType(request_type)]["ai_recommendation"] if request_type else ""

    if "__interrupt__" in state:
        pending = state["__interrupt__"][0].value
        log_new_request(
            thread_id, payload.customer_id, payload.message,
            request_type, state.get("risk_tier"), state.get("tool_args", {}),
            ai_recommendation, status="pending",
        )
        return SubmitRequestOut(thread_id=thread_id, status="pending_approval", pending_review=pending, trace=state.get("trace", []))

    log_new_request(
        thread_id, payload.customer_id, payload.message,
        request_type, state.get("risk_tier"), state.get("tool_args", {}),
        ai_recommendation, status="approved",
    )
    resolve_request(thread_id, "approved")
    return SubmitRequestOut(thread_id=thread_id, status="completed", result=state.get("tool_result"), trace=state.get("trace", []))


@app.post("/requests/{thread_id}/decision", response_model=DecisionOut)
def submit_decision(thread_id: str, payload: DecisionIn):
    """Resumes a paused request with a human's approval decision."""
    config = {"configurable": {"thread_id": thread_id}}

    state = graph.invoke(Command(resume=payload.approved), config=config)

    if "tool_result" not in state and payload.approved:
        raise HTTPException(status_code=500, detail="Approved but no tool result was produced.")

    resolve_request(thread_id, "approved" if payload.approved else "rejected")
    return DecisionOut(thread_id=thread_id, status="completed", result=state.get("tool_result", {}), trace=state.get("trace", []))


@app.get("/requests/pending")
def pending_requests():
    """Returns every request currently waiting for human review, for the dashboard's queue."""
    return get_pending_requests()


@app.get("/requests/stats")
def request_stats():
    """Returns today's counts, for the dashboard's stat cards."""
    return get_stats()




@app.get("/requests/history")
def request_history():
    """Returns every resolved request, for the Request History tab."""
    return get_request_history()