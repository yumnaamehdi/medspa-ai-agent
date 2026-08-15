import json
import time
from pathlib import Path

from rag.retrieval import retrieve


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_FILE = BASE_DIR / "evals" / "dataset.json"


def load_dataset():
    with open(DATASET_FILE, "r") as file:
        return json.load(file)


def evaluate():
    dataset = load_dataset()

    correct = 0
    total = len(dataset)
    total_latency = 0

    print("\nRAG EVALUATION")
    print("=" * 60)

    for item in dataset:
        query = item["query"]
        expected_title = item["expected_title"]
        expected_type = item["expected_type"]

        start = time.time()

        results = retrieve(
        query,
        top_k=3,
        min_score=0.50
        )
        latency = time.time() - start
        total_latency += latency

        if expected_title is None:
            passed = len(results) == 0
        else:
            passed = any(
                result["title"] == expected_title
                and result["type"] == expected_type
                for result in results
            )

        if passed:
            correct += 1

        print(f"\nQuery: {query}")
        print(f"Expected: {expected_title} / {expected_type}")

        if results:
            print(
                "Retrieved:",
                [
                    (
                        result["title"],
                        result["type"],
                        round(result["score"], 3)
                    )
                    for result in results
                ]
            )
        else:
            print("Retrieved: []")

        print("PASS" if passed else "FAIL")
        print(f"Latency: {latency:.3f}s")

    accuracy = correct / total * 100
    average_latency = total_latency / total

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"Tests passed: {correct}/{total}")
    print(f"Retrieval accuracy: {accuracy:.1f}%")
    print(f"Average retrieval latency: {average_latency:.3f}s")


if __name__ == "__main__":
    evaluate()