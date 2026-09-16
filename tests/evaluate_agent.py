"""
Evaluates the full agent pipeline (classify -> approval gate ->
execute) against the synthetic request set. Unlike Phase 2's
classifier-only test, this checks three things per request:
classification correctness, correct approval gating behaviour, and
correct tool selection once approved.
"""

from langgraph.types import Command
from app.agents.graph import graph
from tests.synthetic_requests import SYNTHETIC_REQUESTS
from app.models.taxonomy import TAXONOMY

results = []

for i, example in enumerate(SYNTHETIC_REQUESTS):
    thread_id = f"eval-{i}"
    config = {"configurable": {"thread_id": thread_id}}

    expected_type = example["expected_type"]
    expected_tier = TAXONOMY[expected_type]["risk_tier"]
    expected_tools = set(TAXONOMY[expected_type]["tools"])

    state = graph.invoke(
        {"customer_id": "cust_001", "message": example["text"]},
        config=config,
    )

    classification_correct = state.get("request_type") == expected_type.value
    was_paused = "__interrupt__" in state
    should_have_paused = expected_tier.value != "auto"
    gating_correct = was_paused == should_have_paused

    # Auto-approve everything paused, so we can check tool selection too
    if was_paused:
        state = graph.invoke(Command(resume=True), config=config)

    actual_tools = set(state.get("tool_result", {}).keys())
    tools_correct = actual_tools == expected_tools

    all_correct = classification_correct and gating_correct and tools_correct

    results.append({
        "text": example["text"],
        "classification_correct": classification_correct,
        "gating_correct": gating_correct,
        "tools_correct": tools_correct,
        "all_correct": all_correct,
    })

    status = "PASS" if all_correct else "FAIL"
    print(f"[{status}] \"{example['text']}\"")
    if not all_correct:
        print(f"    classification_correct: {classification_correct}")
        print(f"    gating_correct: {gating_correct} (expected pause: {should_have_paused}, actual pause: {was_paused})")
        print(f"    tools_correct: {tools_correct} (expected: {expected_tools}, actual: {actual_tools})")

total = len(results)
fully_correct = sum(r["all_correct"] for r in results)
print(f"\nFull pipeline accuracy: {fully_correct}/{total} ({fully_correct/total:.0%})")
print(f"Classification accuracy: {sum(r['classification_correct'] for r in results)}/{total}")
print(f"Gating accuracy: {sum(r['gating_correct'] for r in results)}/{total}")
print(f"Tool selection accuracy: {sum(r['tools_correct'] for r in results)}/{total}")