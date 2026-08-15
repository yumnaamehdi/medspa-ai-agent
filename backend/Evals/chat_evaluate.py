import json
import time
from pathlib import Path

from main import chat, ChatRequest


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_FILE = BASE_DIR / "evals" / "chat_dataset.json"


def load_dataset():
    with open(DATASET_FILE, "r") as file:
        return json.load(file)


def evaluate():
    dataset = load_dataset()

    correct = 0
    total = len(dataset)
    total_latency = 0

    print("\nEND-TO-END CHAT EVALUATION")
    print("=" * 60)

    for item in dataset:
        query = item["query"]
        expected_contains = item["expected_contains"]
        expected_empty_sources = item.get("expected_empty_sources", False)

        start = time.time()

        result = chat(
            ChatRequest(message=query)
        )

        latency = time.time() - start
        total_latency += latency

        response_text = result["response"].lower()
        sources = result.get("retrieved_sources", [])

        contains_expected = all(
            phrase.lower() in response_text
            for phrase in expected_contains
        )

        sources_match = True

        if expected_empty_sources:
            sources_match = len(sources) == 0

        passed = (
            contains_expected
            and sources_match
        )

        if passed:
            correct += 1

        print(f"\nQuery: {query}")
        print(f"Response: {result['response']}")
        print(f"Sources: {sources}")
        print("PASS" if passed else "FAIL")
        print(f"Latency: {latency:.3f}s")

    accuracy = correct / total * 100
    average_latency = total_latency / total

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"Tests passed: {correct}/{total}")
    print(f"End-to-end accuracy: {accuracy:.1f}%")
    print(f"Average latency: {average_latency:.3f}s")


if __name__ == "__main__":
    evaluate()