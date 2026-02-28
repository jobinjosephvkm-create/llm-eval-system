from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()


# ---------- Request Model ----------
class RunRequest(BaseModel):
    input: str
    system_prompt: str = "You are a precise and logical assistant."


def calculate_average_score(metrics):
    """Calculate weighted average score from metrics"""
    accuracy = metrics.get("accuracy", 5)
    clarity = metrics.get("clarity", 5)
    reasoning = metrics.get("reasoning_quality", 5)
    hallucination = metrics.get("hallucination_risk", 5)
    
    # Hallucination is negative → invert
    hallucination_score = 10 - hallucination
    return round(
        accuracy * 0.3 +
        clarity * 0.25 +
        reasoning * 0.3 +
        hallucination_score * 0.15,
        2
    )


@app.post("/run")
def run_pipeline(req: RunRequest):
    initial_prompt = req.system_prompt
    current_prompt = initial_prompt
    
    # Track best prompt and its score
    best_prompt = initial_prompt
    best_score = 0.0
    best_output = ""
    best_metrics = {}
    
    # Store initial iteration results
    initial_output = ""
    initial_metrics = {}
    initial_score = 0.0
    
    # Iterate 5 times
    for iteration in range(5):
        # 1️⃣ Call Agent with current prompt
        try:
            agent_resp = requests.post(
                "http://agent:8000/chat",
                json={
                    "input": req.input,
                    "system_prompt": current_prompt
                },
                timeout=60
            )
            agent_resp.raise_for_status()  # Raise exception for bad status codes
            if not agent_resp.text:
                raise ValueError("Agent returned empty response")
            agent_response = agent_resp.json()
        except Exception as e:
            print(f"[ORCHESTRATOR] ERROR calling agent: {e}")
            print(f"[ORCHESTRATOR] Response status: {agent_resp.status_code if 'agent_resp' in locals() else 'N/A'}")
            print(f"[ORCHESTRATOR] Response text: {agent_resp.text[:200] if 'agent_resp' in locals() and agent_resp.text else 'N/A'}")
            raise
        
        output = agent_response.get("output", "")
        
        # 2️⃣ Call Judge to evaluate output
        try:
            judge_resp = requests.post(
                "http://judge:8000/evaluate",
                json={
                    "question": req.input,
                    "answer": output
                },
                timeout=60
            )
            judge_resp.raise_for_status()  # Raise exception for bad status codes
            if not judge_resp.text:
                raise ValueError("Judge returned empty response")
            judge_response = judge_resp.json()
        except Exception as e:
            print(f"[ORCHESTRATOR] ERROR calling judge: {e}")
            print(f"[ORCHESTRATOR] Response status: {judge_resp.status_code if 'judge_resp' in locals() else 'N/A'}")
            print(f"[ORCHESTRATOR] Response text: {judge_resp.text[:200] if 'judge_resp' in locals() and judge_resp.text else 'N/A'}")
            raise
        
        # Calculate average score
        metrics = {
            "accuracy": judge_response.get("accuracy", 5),
            "clarity": judge_response.get("clarity", 5),
            "reasoning_quality": judge_response.get("reasoning_quality", 5),
            "hallucination_risk": judge_response.get("hallucination_risk", 5),
        }
        average_score = calculate_average_score(metrics)

        # ---- Log intermediate results to console for docker logs ----
        print("\n[ORCHESTRATOR] Iteration", iteration + 1, "of 5")
        print("[ORCHESTRATOR] Prompt:")
        print(current_prompt)
        print("[ORCHESTRATOR] Output (truncated to 400 chars):")
        print((output or "")[:400])
        print("[ORCHESTRATOR] Metrics:", metrics)
        print("[ORCHESTRATOR] Average score:", average_score)
        
        # Store initial iteration results
        if iteration == 0:
            initial_output = output
            initial_metrics = {**judge_response, "average_score": average_score}
            initial_score = average_score
        
        # Track best prompt (highest score)
        if average_score > best_score:
            best_score = average_score
            best_prompt = current_prompt
            best_output = output
            best_metrics = {**judge_response, "average_score": average_score}
        
        # 3️⃣ Call Optimiser to improve prompt (except on last iteration)
        if iteration < 4:
            try:
                optimiser_resp = requests.post(
                    "http://optimiser:8000/improve",
                    json={
                        "input": req.input,
                        "metrics": {
                            **metrics,
                            "average_score": average_score
                        },
                        "current_prompt": current_prompt
                    },
                    timeout=60
                )
                optimiser_resp.raise_for_status()  # Raise exception for bad status codes
                if not optimiser_resp.text:
                    raise ValueError("Optimiser returned empty response")
                optimiser_response = optimiser_resp.json()
            except Exception as e:
                print(f"[ORCHESTRATOR] ERROR calling optimiser: {e}")
                print(f"[ORCHESTRATOR] Response status: {optimiser_resp.status_code if 'optimiser_resp' in locals() else 'N/A'}")
                print(f"[ORCHESTRATOR] Response text: {optimiser_resp.text[:200] if 'optimiser_resp' in locals() and optimiser_resp.text else 'N/A'}")
                # Continue with current prompt if optimiser fails
                print("[ORCHESTRATOR] Continuing with current prompt due to optimiser error")
            else:
                current_prompt = optimiser_response.get("improved_prompt", current_prompt)
                print("[ORCHESTRATOR] Updated prompt from optimiser:")
                print(current_prompt)
    
    # ---------- Return initial and best prompts ----------
    return {
        "initial": {
            "prompt": initial_prompt,
            "output": initial_output,
            "metrics": initial_metrics,
            "average_score": initial_score
        },
        "best": {
            "prompt": best_prompt,
            "output": best_output,
            "metrics": best_metrics,
            "average_score": best_score,
            "iteration": "Found during 5 iterations"
        },
        "iterations": 5
    }