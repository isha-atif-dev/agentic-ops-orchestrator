"""
Runs the classifier against every synthetic request and checks
whether it predicts the correct request type. This is the first
real accuracy check for Phase 2, before building anything else on
top of the classifier.
"""

from app.agents.classifier import classify_request
from tests.synthetic_requests import SYNTHETIC_REQUESTS

correct = 0
total = len(SYNTHETIC_REQUESTS)

for example in SYNTHETIC_REQUESTS:
    predicted = classify_request(example["text"])
    is_correct = predicted == example["expected_type"]
    correct += is_correct

    status = "PASS" if is_correct else "FAIL"
    print(f"[{status}] \"{example['text']}\"")
    print(f"    expected: {example['expected_type'].value}")
    print(f"    got:      {predicted.value}")

print(f"\nAccuracy: {correct}/{total} ({correct/total:.0%})")