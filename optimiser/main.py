from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ImproveRequest(BaseModel):
    input: str
    metrics: dict
    current_prompt: str

class ImproveResponse(BaseModel):
    improved_prompt: str

@app.post("/improve", response_model=ImproveResponse)
def improve(req: ImproveRequest):
    metrics = req.metrics
    score = metrics.get("average_score", 5)
    accuracy = metrics.get("accuracy", 5)
    clarity = metrics.get("clarity", 5)
    reasoning = metrics.get("reasoning_quality", 5)
    hallucination = metrics.get("hallucination_risk", 5)

    improved_prompt = req.current_prompt

    hints = []

    # Low clarity → simplify
    if clarity < 8:
        hints.append("Make your explanation simpler and easier to understand.")

    # Low reasoning → step-by-step
    if reasoning < 8:
        hints.append("Explain the reasoning step by step with examples.")

    # High hallucination risk → accuracy caution
    if hallucination > 5:
        hints.append("Be careful to provide accurate and factual information.")

    # Low average score → overall improvement
    if score < 8.0:
        hints.append("Add an example to illustrate the concept clearly.")

    if hints:
        improved_prompt += " " + " ".join(hints)

    return {"improved_prompt": improved_prompt}