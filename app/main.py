"""
Entry point for the Agentic Ops Orchestrator API.

This file creates the FastAPI app and defines the health check
endpoint, used to confirm the service is running (locally, in
Docker, and later on AWS).
"""

from fastapi import FastAPI

app = FastAPI(title="Agentic Ops Orchestrator")


@app.get("/health")
def health_check():
    """
    Simple endpoint to confirm the API is up and responding.

    Returns a small JSON payload rather than nothing, so tools
    like uptime monitors or CI/CD checks have something concrete
    to verify against.
    """
    return {"status": "ok", "service": "agentic-ops-orchestrator"}