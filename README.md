# Agentic Ops Orchestrator

An agentic system for Meridian Financial Services Ltd (a fictional bank) that reads real customer operations requests, written in plain English, and decides what action to take, executing low-risk actions automatically and pausing high-risk ones for human approval.

This is the second project in a two-part AI Engineer portfolio. [Project 1, RAG Compliance Assistant](https://github.com/isha-atif-dev/rag-compliance-assistant), is a "knows things" system, it answers questions from documents. This project is the "does things" counterpart, it takes action based on a request, not just retrieves information.

## The problem it solves

Meridian's customers send in requests like:

- "My account was flagged for KYC review, can you check the status?"
- "Someone's used my card without my permission."
- "I want to cancel my subscription."
- "I think someone opened an account in my name."

A human normally has to read each one, work out what it actually is, decide what to do, and act, or escalate. This system automates that decision-making, while keeping a human in the loop for anything consequential.

## How it works

```mermaid
flowchart TD
    A[Customer message] --> B[Classify intent<br/>Claude, structured output]
    B --> C{Risk tier<br/>from taxonomy}
    C -->|auto| D[Agent loop runs immediately]
    C -->|needs_approval / urgent_approval| E[Pauses for human review]
    E -->|approved| D
    E -->|rejected| F[No action taken]
    D --> G[Claude decides which tool(s)<br/>to call, executes them,<br/>decides when it's done]
    G --> H[Action taken + logged]
```

1. A request comes in through the API (or the customer-facing web page).
2. **Classification**: Claude reads the message and classifies it into one of 8 request types, using structured JSON output so the result is always a valid, predictable category, not free text.
3. **Risk gating**: a hand-written taxonomy maps each request type to a risk tier (`auto`, `needs_approval`, `urgent_approval`). This part is deliberately deterministic, not AI-decided, a bank should not let an LLM decide on its own whether something needs human sign-off.
4. **Human approval**: for anything above `auto`, the graph pauses (via LangGraph's `interrupt()`) and the request appears on the internal ops dashboard for a reviewer to approve or reject. Nothing executes until a human acts.
5. **Agentic execution**: once approved (or immediately, for low-risk requests), Claude is handed the full set of available tools and decides for itself which one(s) to call, in what order, based on the actual request, not a fixed lookup. It can call more than one tool, and it decides when it's done.
6. Every action is logged (`action_log` table) for auditability.

## Two frontends, two different users

Unlike a typical chatbot demo, this system has two separate interfaces, because it has two separate kinds of user:

- **`frontend/customer.html`**, a simple "How can we help?" page a customer writes their request into.
- **`frontend/dashboard.html`**, Meridian's internal ops dashboard, where a reviewer sees pending requests (with an AI-generated recommendation), and approves or rejects them.

Both are plain HTML/CSS/JavaScript calling the FastAPI backend directly, no build step, no framework, opened straight in a browser.

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| API | FastAPI | Same as Project 1, consistent, async-friendly, auto-generates interactive docs |
| Orchestration | LangGraph | Branching, stateful workflow with a pause/resume mechanism, not a straight pipeline |
| LLM | Claude API (Haiku model) | Classification and agentic tool-use loop; a small, fast model is enough since the task is narrow, not general reasoning |
| Database | SQLite | A deliberate change from Project 1's Postgres, this project doesn't need a full database server, a file-based database is the right-sized tool for a small amount of mocked backend data |
| Deployment | Docker + AWS EC2 | Shared free-tier EC2 instance with Project 1, different port (8001), since the AWS account is limited to one instance |

## The agentic loop, in detail

Early on, this project used a fixed lookup table: classify the request, then run whatever tools the taxonomy said were mapped to that type. That's a **workflow**, not an **agent**, the model never actually decided anything about which actions to take, it just filled in a category, and code did the rest.

That was rebuilt to a real agentic tool-use loop:

- Claude is given all 8 tools (with schemas) and the customer's message.
- It decides which tool(s) to call, and with what arguments, itself.
- Each tool's result is fed back to it, and it decides whether another tool call is needed, or whether it's done (`stop_reason == "end_turn"`).
- A safety cap (`MAX_ITERATIONS = 5`) exists purely to prevent runaway loops, not as a normal stopping point.

This means the same message can genuinely result in different, still-reasonable actions on different runs, e.g. a stolen card report might just escalate to the fraud team, or escalate **and** freeze the account, depending on the model's read of the situation. That's expected agentic behaviour, not a bug, and it's exactly why the human approval gate matters even more with a real agent than with a fixed pipeline.

## Evaluation

Classifying "did the agent do the right thing" needed a different approach than Project 1's Recall@5. Three things are checked per request:

1. **Classification correctness**, did it identify the right request type?
2. **Gating correctness**, did it correctly pause (or not pause) for approval?
3. **Essential tool coverage**, did it call at least the necessary tool(s)? (Checked as a subset, not exact match, since an agent taking a reasonable extra precaution is a feature, not a failure.)

**Result: 100% across 3 consecutive evaluation runs**, after fixing three real, reproducible issues (below).

## Real engineering problems hit and fixed

These are worth knowing in detail, they're better interview material than a clean build with no bumps:

- **The Anthropic API had changed since training data**: `temperature` no longer exists as a parameter, structured output now goes through a nested `output_config.format` object requiring `additionalProperties: false`. Rather than guess, the actual installed SDK was introspected directly to confirm the real parameter shapes before writing code.
- **A duplicate `FastAPI()` instantiation silently broke every route** except the auto-generated `/docs` page, a second `app = FastAPI(...)` call later in the file quietly replaced the first, and every `@app.get`/`@app.post` route was attached to the one that got discarded.
- **The SQLite database file was accidentally committed to Git.** `.gitignore` excluded Django's default `db.sqlite3` but not this project's actual filename, so every `git push`/`git pull` was overwriting real server data with local dev data (and vice versa). Fixed by removing it from tracking and adding `*.db` to `.gitignore`.
- **The agent sometimes took no action at all**, given free choice, the model would occasionally just respond with clarifying questions instead of acting, appropriate for a chatbot, wrong for a backend system with no way to ask a follow-up. Fixed by forcing a tool call on the first turn (`tool_choice: "any"`), then leaving it free to decide when it's actually done.
- **The agent sometimes called the same tool twice in one run**, e.g. escalating a fraud case twice, which would create duplicate cases in a human investigator's queue. Prompting alone didn't reliably prevent this; fixed with a code-level idempotency guard that intercepts a repeated tool call before the real action runs again.
- **A reproducible reasoning gap for identity theft cases**: the agent would escalate to the fraud team but not freeze the account, reasoning that the fraudulent account was separate from the existing one. This was a genuine, repeatable logic gap, not random variance, confirmed across multiple runs, and fixed by making the underlying reasoning ("your identity being compromised puts your existing account at risk too") explicit in the system prompt.

## Known limitations

Being upfront about these rather than hiding them:

- The approval checkpointer (`MemorySaver`) is in-memory only. If the server restarts, any request still waiting for approval is lost. Fine for a portfolio demo, not production-ready.
- CORS is fully open (`allow_origins=["*"]`), correct for a public demo, not something to do with real customer data.
- There's no login system, the customer-facing page uses a single hardcoded demo customer ID, rather than real authentication.
- The two frontend pages are local HTML files calling the live API, not themselves hosted at a public URL.
- Some run-to-run variability in exactly which tool(s) the agent chooses is expected and by design, a trade-off of using a real agent instead of fixed routing.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/requests` | Submit a new customer request |
| POST | `/requests/{thread_id}/decision` | Approve or reject a paused request |
| GET | `/requests/pending` | List requests awaiting review (dashboard queue) |
| GET | `/requests/stats` | Today's approved/rejected/pending/total counts (dashboard stat cards) |

## Project structure

```
agentic-ops-orchestrator/
  app/
    agents/               classifier, agent loop, tool specs, graph, nodes, state
    models/               request taxonomy, risk tiers, Pydantic schemas
    tools/                SQLite db, the 8 mocked backend tools, request logging
    main.py               FastAPI entry point, routes, CORS, DB init on startup
    config.py             loads settings/secrets from environment
  frontend/
    customer.html         customer-facing request page
    dashboard.html         internal ops approval dashboard
  tests/
    synthetic_requests.py  evaluation question set
    test_classifier.py
    evaluate_agent.py      full pipeline evaluation
  Dockerfile
  docker-compose.yml
  requirements.txt
```

## Running locally

```bash
git clone https://github.com/isha-atif-dev/agentic-ops-orchestrator.git
cd agentic-ops-orchestrator
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file:

```
ANTHROPIC_API_KEY=your-key-here
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Then open `frontend/customer.html` and `frontend/dashboard.html` directly in a browser (update the `API_BASE` constant in each if not running locally).

## Deployment

Deployed on the same AWS EC2 instance as Project 1 (a free-tier constraint, one instance only), on a different port (8001 vs 8000). Unlike Project 1, this project needed no CPU-only PyTorch workaround, it has no local embedding or ML model dependency, only lightweight API calls, so the Docker image is small and the build is fast.

```bash
docker compose up --build -d
```

## Author

Isha Atif, built as part of a two-project AI Engineer portfolio alongside [RAG Compliance Assistant](https://github.com/isha-atif-dev/rag-compliance-assistant).