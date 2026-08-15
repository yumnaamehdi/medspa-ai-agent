import os
import json
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    return OpenAI(api_key=api_key)

BASE_DIR = Path(__file__).resolve().parent.parent
EMBEDDINGS_FILE = BASE_DIR / "rag" / "embeddings.json"


def load_documents():
    with open(EMBEDDINGS_FILE, "r") as file:
        return json.load(file)


def create_embedding(text):
    client = get_openai_client()

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding

def cosine_similarity(vector_a, vector_b):
    a = np.array(vector_a)
    b = np.array(vector_b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def retrieve(query, top_k=3, min_score=0.50):
    documents = load_documents()

    query_embedding = create_embedding(query)

    results = []

    for document in documents:
        score = cosine_similarity(
            query_embedding,
            document["embedding"]
        )

        if score >= min_score:
            results.append({
                "title": document["title"],
                "type": document["type"],
                "text": document["text"],
                "score": float(score)
            })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]