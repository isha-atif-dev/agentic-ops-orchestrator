"""
Entry point for the Agentic Ops Orchestrator API.

Exposes the LangGraph agent (app/agents/graph.py) over HTTP, plus
the health check endpoint used to confirm the service is running.

Two endpoints handle the human-in-the-loop flow: submitting a new
request (which may pause for approval) and submitting a decision
on a paused request (which resumes it).
"""

import uuid
from fastapi import FastAPI, HTTPException
from langgraph.types import Command
from app.agents.graph import graph
from app.models.schemas import SubmitRequestIn, SubmitRequestOut, DecisionIn, DecisionOut

app = FastAPI(title="Agentic Ops Orchestrator")


@app.get("/health")
def health_check():
    """Simple endpoint to confirm the API is up and responding."""
    return {"status": "ok", "service": "agentic-ops-orchestrator"}


@app.post("/requests", response_model=SubmitRequestOut)
def submit_request(payload: SubmitRequestIn):
    """
    Submits a new customer request to the agent. If the request is
    low-risk, it completes immediately. If it needs approval, the
    graph pauses and this returns the details a reviewer needs to
    see, along with the thread_id needed to submit a decision later.
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    state = graph.invoke(
        {"customer_id": payload.customer_id, "message": payload.message},
        config=config,
    )

    if "__interrupt__" in state:
        pending = state["__interrupt__"][0].value
        return SubmitRequestOut(thread_id=thread_id, status="pending_approval", pending_review=pending)

    return SubmitRequestOut(thread_id=thread_id, status="completed", result=state.get("tool_result"))


@app.post("/requests/{thread_id}/decision", response_model=DecisionOut)
def submit_decision(thread_id: str, payload: DecisionIn):
    """
    Resumes a paused request with a human's approval decision.
    """
    config = {"configurable": {"thread_id": thread_id}}

    state = graph.invoke(Command(resume=payload.approved), config=config)

    if "tool_result" not in state and payload.approved:
        raise HTTPException(status_code=500, detail="Approved but no tool result was produced.")

    return DecisionOut(thread_id=thread_id, status="completed", result=state.get("tool_result", {}))