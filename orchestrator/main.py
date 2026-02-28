from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()


# ---------- Request Model ----------
class RunRequest(BaseModel):
    input: str
    system_prompt: str = "You are a precise and logical assistant."


@app.post("/run")
def run_pipeline(req: RunRequest):

    # 1️⃣ Call Agent (initial)
    agent_response = requests.post(
        "http://agent:8000/chat",
        json={
            "input": req.input,
            "system_prompt": req.system_prompt
        }
    ).json()

    initial_output = agent_response.get("output", "")

    # 2️⃣ Call Judge on initial output
    judge_response = requests.post(
        "http://judge:8000/evaluate",
        json={
            "question": req.input,
            "answer": initial_output
        }
    ).json()

    # Extract metrics
    accuracy = judge_response.get("accuracy", 5)
    clarity = judge_response.get("clarity", 5)
    reasoning = judge_response.get("reasoning_quality", 5)
    hallucination = judge_response.get("hallucination_risk", 5)

    # Hallucination is negative → invert
    hallucination_score = 10 - hallucination
    average_score = round(
        accuracy * 0.3 +
        clarity * 0.25 +
        reasoning * 0.3 +
        hallucination_score * 0.15,
        2
    )

    # 3️⃣ Call Optimiser
    optimiser_response = requests.post(
        "http://optimiser:8000/improve",
        json={
            "input": req.input,
            "metrics": {
                "accuracy": accuracy,
                "clarity": clarity,
                "reasoning_quality": reasoning,
                "hallucination_risk": hallucination,
                "average_score": average_score
            },
            "current_prompt": req.system_prompt
        }
    ).json()

    improved_prompt = optimiser_response.get("improved_prompt", req.system_prompt)

    # 4️⃣ Call Agent again with improved prompt
    improved_agent_response = requests.post(
        "http://agent:8000/chat",
        json={
            "input": req.input,
            "system_prompt": improved_prompt
        }
    ).json()

    improved_output = improved_agent_response.get("output", "")

    # 5️⃣ Call Judge on improved output
    improved_judge_response = requests.post(
        "http://judge:8000/evaluate",
        json={
            "question": req.input,
            "answer": improved_output
        }
    ).json()

    # Extract improved metrics
    improved_accuracy = improved_judge_response.get("accuracy", 5)
    improved_clarity = improved_judge_response.get("clarity", 5)
    improved_reasoning = improved_judge_response.get("reasoning_quality", 5)
    improved_hallucination = improved_judge_response.get("hallucination_risk", 5)

    improved_hallucination_score = 10 - improved_hallucination
    improved_average_score = round(
        improved_accuracy * 0.3 +
        improved_clarity * 0.25 +
        improved_reasoning * 0.3 +
        improved_hallucination_score * 0.15,
        2
    )

    # ---------- User-readable formatted output ----------
    return {
        "stages": {
            "initial": {
                "prompt": req.system_prompt,
                "output": initial_output,
                "metrics": {
                    **judge_response,
                    "average_score": average_score
                }
            },
            "optimisation": {
                "improved_prompt": improved_prompt,
                "improved_output": improved_output,
                "metrics_after_optimisation": {
                    **improved_judge_response,
                    "average_score": improved_average_score
                }
            }
        }
    }