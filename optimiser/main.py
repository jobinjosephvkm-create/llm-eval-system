from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.chat_models import ChatOllama
import json
import os

app = FastAPI()


class ImproveRequest(BaseModel):
    input: str
    metrics: dict
    current_prompt: str


class ImproveResponse(BaseModel):
    improved_prompt: str


# LLM client for optimiser – uses Ollama inside the Docker network
llm = ChatOllama(
    model=os.getenv("OPTIMISER_MODEL", "phi3"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
    temperature=0.3,
)


@app.post("/improve", response_model=ImproveResponse)
def improve(req: ImproveRequest):
    metrics = req.metrics
    score = metrics.get("average_score", 5)
    accuracy = metrics.get("accuracy", 5)
    clarity = metrics.get("clarity", 5)
    reasoning = metrics.get("reasoning_quality", 5)
    hallucination = metrics.get("hallucination_risk", 5)

    # Start from the current prompt
    improved_prompt = req.current_prompt

    # Fallback rule-based hints (used if LLM is unavailable)
    hints = []

    if clarity < 8:
        hints.append("Make your explanation simpler and easier to understand.")

    if reasoning < 8:
        hints.append("Explain the reasoning step by step with examples.")

    if hallucination > 5:
        hints.append("Be careful to provide accurate and factual information.")

    if score < 8.0:
        hints.append("Add an example to illustrate the concept clearly.")

    # Try to use the LLM to generate an improved prompt
    try:
        system_msg = (
            "You are a prompt engineering assistant. "
            "Given a user's question, evaluation metrics, and the current system prompt, "
            "rewrite the system prompt so that future answers are more accurate, clearer, "
            "better reasoned, and have lower hallucination risk. "
            "Return ONLY the improved system prompt text, with no explanations or markdown."
        )

        user_msg = (
            f"Question:\n{req.input}\n\n"
            f"Current system prompt:\n{req.current_prompt}\n\n"
            f"Evaluation metrics (JSON):\n{json.dumps(metrics, indent=2)}\n\n"
        )

        if hints:
            user_msg += "High-level improvement hints:\n- " + "\n- ".join(hints) + "\n\n"

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        response = llm.invoke(messages)
        candidate = (response.content or "").strip()

        if candidate:
            improved_prompt = candidate
    except Exception as e:
        # If LLM call fails (e.g., no Ollama running), fall back to simple hint-based prompt
        if hints:
            improved_prompt = req.current_prompt + " " + " ".join(hints)

    return {"improved_prompt": improved_prompt}