import os
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = BASE_DIR / "rag" / "embeddings.json"


def load_json(filename):
    with open(DATA_DIR / filename, "r") as file:
        return json.load(file)


def load_text(filename):
    with open(DATA_DIR / filename, "r") as file:
        return file.read()


def build_documents():
    documents = []

    services = load_json("services.json")
    pricing = load_json("pricing.json")
    policies = load_json("policies.json")
    faq = load_text("faq.md")

    # -------------------------
    # SERVICES
    # -------------------------
    for service in services:
        documents.append({
            "type": "service",
            "title": service["name"],
            "text": (
                f"Service: {service['name']}. "
                f"Category: {service['category']}. "
                f"Description: {service['description']}"
            )
        })

    # -------------------------
    # PRICING
    # -------------------------
    for name, info in pricing.items():
        documents.append({
            "type": "pricing",
            "title": name,
            "text": (
                f"Pricing for {name}: "
                f"${info['price']} {info['unit']}."
            )
        })

    # -------------------------
    # POLICIES
    # Split each policy into its
    # own searchable document
    # -------------------------
    for policy_name, policy_info in policies.items():

        readable_title = policy_name.replace("_", " ").title()

        if isinstance(policy_info, dict):

            policy_parts = []

            for key, value in policy_info.items():
                readable_key = key.replace("_", " ").title()

                policy_parts.append(
                    f"{readable_key}: {value}"
                )

            policy_text = ". ".join(policy_parts)

        else:
            policy_text = str(policy_info)

        documents.append({
            "type": "policy",
            "title": readable_title,
            "text": (
                f"Clinic policy for {readable_title}. "
                f"{policy_text}"
            )
        })

    # -------------------------
    # FAQ
    # -------------------------
    documents.append({
        "type": "faq",
        "title": "Frequently Asked Questions",
        "text": faq
    })

    return documents


def create_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


def main():

    documents = build_documents()

    embedded_documents = []

    print(
        f"Creating embeddings for "
        f"{len(documents)} documents..."
    )

    for index, document in enumerate(
        documents,
        start=1
    ):

        print(
            f"Embedding {index}/"
            f"{len(documents)}: "
            f"{document['title']}"
        )

        embedding = create_embedding(
            document["text"]
        )

        embedded_documents.append({
            **document,
            "embedding": embedding
        })

    with open(OUTPUT_FILE, "w") as file:
        json.dump(
            embedded_documents,
            file,
            indent=2
        )

    print()
    print("Done.")
    print(
        f"Saved embeddings to "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()