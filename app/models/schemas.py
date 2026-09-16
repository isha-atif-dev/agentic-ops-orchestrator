"""
Pydantic schemas for the API's request and response bodies.

Keeping these separate from the internal AgentState (in
app/agents/state.py) is deliberate, the API's shape is a public
contract, the internal graph state is free to change without
breaking anyone calling the API.
"""

from pydantic import BaseModel
from typing import Optional


class SubmitRequestIn(BaseModel):
    customer_id: str
    message: str


class SubmitRequestOut(BaseModel):
    thread_id: str
    status: str  # "completed" or "pending_approval"
    result: Optional[dict] = None
    pending_review: Optional[dict] = None


class DecisionIn(BaseModel):
    approved: bool


class DecisionOut(BaseModel):
    thread_id: str
    status: str  # "completed"
    result: dict