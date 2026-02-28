from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph, END
from typing import TypedDict

app = FastAPI()

# Connect to Ollama container (use service name inside Docker network)
llm = ChatOllama(
    model="phi3",
    base_url="http://ollama:11434",
    temperature=0.3  # Add some randomness to allow different outputs with same prompt
)

# -----------------------------
# Define Agent State
# -----------------------------
class AgentState(TypedDict):
    input: str
    system_prompt: str
    output: str

P0 = "You are a precise and logical assistant."

# -----------------------------
# Agent Node
# -----------------------------
def agent_node(state: AgentState):
    messages = [
        {"role": "system", "content": state["system_prompt"]},
        {"role": "user", "content": state["input"]}
    ]
    response = llm.invoke(messages)
    return {"output": response.content}

# -----------------------------
# Build Graph
# -----------------------------
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.set_entry_point("agent")
graph.add_edge("agent", END)

app_graph = graph.compile()

# -----------------------------
# API Schema
# -----------------------------
class Query(BaseModel):
    input: str
    system_prompt: str = P0  # Default to P0 if not provided

@app.post("/chat")
def chat(query: Query):
    result = app_graph.invoke({
        "input": query.input,
        "system_prompt": query.system_prompt  # Use the provided system_prompt
    })
    return result