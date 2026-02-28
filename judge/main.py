from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.llms import Ollama
import json
import re

app = FastAPI()

# Connect to Ollama inside Docker network
llm = Ollama(
    model="phi3",
    base_url="http://ollama:11434",
    format="json"
)


# ---------- Request Model ----------

class EvalRequest(BaseModel):
    question: str
    answer: str


# ---------- Response Model ----------

class EvalResponse(BaseModel):
    accuracy: int
    clarity: int
    reasoning_quality: int
    hallucination_risk: int
    explanation: str
    average_score: float


# ---------- LLM as Judge ----------

@app.post("/evaluate", response_model=EvalResponse)
def evaluate(request: EvalRequest):

    judge_prompt = f"""
You are a strict LLM evaluator.

Evaluate the following answer to the question.

Question:
{request.question}

Answer:
{request.answer}

Return ONLY valid JSON in this exact format:

{{
  "accuracy": 0-10,
  "clarity": 0-10,
  "reasoning_quality": 0-10,
  "hallucination_risk": 0-10,
  "explanation": "short explanation"
}}

STRICT RULES:
- Return ONLY JSON
- No markdown
- No extra text
- No explanation outside JSON
- If you fail, the system will crash
"""

    # Invoke LLM
    response = llm.invoke(judge_prompt)
    print("\nRAW LLM RESPONSE:\n", response)

    try:
        # Extract JSON block even if model adds text
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if not match:
            raise ValueError("No JSON found")

        json_text = match.group()
        parsed = json.loads(json_text)

    except Exception as e:
        print("PARSE ERROR:", e)
        parsed = {
            "accuracy": 5,
            "clarity": 5,
            "reasoning_quality": 5,
            "hallucination_risk": 5,
            "explanation": "Failed to parse evaluation"
        }

    # ---------- Weighted Scoring ----------

    accuracy = parsed.get("accuracy", 5)
    clarity = parsed.get("clarity", 5)
    reasoning = parsed.get("reasoning_quality", 5)
    hallucination = parsed.get("hallucination_risk", 5)

    # Hallucination is negative → invert
    hallucination_score = 10 - hallucination

    average_score = (
        accuracy * 0.3 +
        clarity * 0.25 +
        reasoning * 0.3 +
        hallucination_score * 0.15
    )

    # Attach score
    parsed["average_score"] = round(average_score, 2)

    return parsed