import os
from fastapi.middleware.cors import CORSMiddleware

import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

from rag.retrieval import retrieve


# Load environment variables
load_dotenv()
print("RENDER:", os.getenv("RENDER"))
print("OPENAI_API_KEY loaded:", bool(os.getenv("OPENAI_API_KEY")))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://medspa-ai-agent.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    return OpenAI(api_key=api_key)
# -------------------------
# LOAD KNOWN SERVICES
# -------------------------

BASE_DIR = Path(__file__).resolve().parent
SERVICES_FILE = BASE_DIR / "data" / "services.json"


def load_known_services():
    with open(SERVICES_FILE, "r") as file:
        services = json.load(file)

    return [
        service["name"].lower()
        for service in services
    ]


KNOWN_SERVICES = load_known_services()


# -------------------------
# REQUEST MODEL
# -------------------------

class ChatRequest(BaseModel):
    message: str


# -------------------------
# SYSTEM PROMPT
# -------------------------

SYSTEM_PROMPT = """
You are an AI customer assistant for a medical aesthetics clinic.

Rules:
- Answer using only the clinic information supplied in RETRIEVED CLINIC INFORMATION.
- Never invent prices, services, policies, or clinic-specific information.
- Never diagnose medical conditions.
- If the retrieved information does not contain the answer, say you do not have that information.
- Recommend speaking with a licensed medical provider when medical assessment is needed.
- Answer only what the customer asked.
- Do not add unrelated policies, prices, deposits, or consultation information.
- Be concise, friendly, and professional.
"""


# -------------------------
# HOME ENDPOINT
# -------------------------

@app.get("/")
def home():
    return {
        "message": "MedSpa AI Agent is running",
        "rag": True
    }


# -------------------------
# CHAT ENDPOINT
# -------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    # Convert user's message to lowercase
    message_lower = request.message.lower()

    # Words that suggest the user is asking
    # about an aesthetic treatment
    treatment_keywords = [
        "filler",
        "botox",
        "microneedling",
        "sculptra",
        "kybella",
        "prf",
        "prp",
        "laser",
        "ipl"
    ]

    # Does the question mention a treatment?
    mentions_treatment = any(
        keyword in message_lower
        for keyword in treatment_keywords
    )

    # Does the question mention one of OUR known services?
    mentions_known_service = any(
        service in message_lower
        for service in KNOWN_SERVICES
    )

    # If they ask about an unknown treatment,
    # do not let RAG guess
    if mentions_treatment and not mentions_known_service:
        return {
            "response": (
                "I don't have information about that treatment "
                "in the clinic knowledge base."
            ),
            "retrieved_sources": []
        }

    # -------------------------
    # RAG RETRIEVAL
    # -------------------------

    results = retrieve(
        request.message,
        top_k=3,
        min_score=0.50
    )

    # Nothing relevant was found
    if not results:
        return {
            "response": (
                "I don't have that information in the clinic knowledge base. "
                "Please contact the clinic for more information."
            ),
            "retrieved_sources": []
        }

    # Combine retrieved documents
    context = "\n\n".join(
        result["text"]
        for result in results
    )

    # Give retrieved context + question to GPT
    user_input = f"""
RETRIEVED CLINIC INFORMATION:

{context}

CUSTOMER QUESTION:

{request.message}
"""

    # -------------------------
    # GENERATE AI RESPONSE
    # -------------------------
    client = get_openai_client()
    response = client.responses.create(
        model="gpt-5-mini",
        instructions=SYSTEM_PROMPT,
        input=user_input
    )

    # -------------------------
    # RETURN RESULT
    # -------------------------

    return {
        "response": response.output_text,
        "retrieved_sources": [
            {
                "title": result["title"],
                "type": result["type"],
                "score": round(result["score"], 3)
            }
            for result in results
        ]
    }
@app.get("/health")
def health():
    return {
        "status": "ok",
        "render": os.getenv("RENDER") == "true",
        "openai_key_configured": bool(os.getenv("OPENAI_API_KEY"))
    }
