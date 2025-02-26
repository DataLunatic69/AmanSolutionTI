import time
import re
import yaml
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq

# Load provider config
with open("providers.yaml", "r") as f:
    providers = yaml.safe_load(f)

# Sort providers by cost per 100 tokens (cheapest first)
providers = sorted(providers["providers"], key=lambda x: x["cost_per_100_tokens"])


class AgentState(TypedDict):
    question: str
    answer: str
    model_used: str
    cost: float
    tokens_used: int

def call_model(state: AgentState, config: dict) -> AgentState:
    """Calls the selected LLM model."""
    model_info = config["configurable"]["model"]
    
    llm = ChatGroq(groq_api_key=model_info["api_key"], model_name=model_info["name"])
    
    print(f"Using model: {model_info['name']}")
    
    messages = [{"role": "user", "content": state["question"]}]
    response = llm.invoke(messages)
    
    state["answer"] = response.content
    state["model_used"] = model_info["name"]
    
    # Approximate token usage (assuming 1 token = 4 characters)
    token_count = len(state["answer"]) / 4
    state["tokens_used"] = int(token_count)
    state["cost"] = (token_count / 100) * model_info["cost_per_100_tokens"]
    
    return state

# LangGraph workflow
workflow = StateGraph(AgentState)

for i, provider in enumerate(providers):
    workflow.add_node(f"model_{i}", call_model)
    workflow.add_edge(f"model_{i}", END)
    
    if i > 0:
        workflow.add_edge(f"model_{i-1}", f"model_{i}")

workflow.add_edge(START, "model_0")
graph = workflow.compile()

class ModelSwitcher:
    """Manages LLM invocation and fallback logic."""
    
    def __init__(self):
        self.graph = graph
        self.last_fail_time = None

    def invoke(self, question: str, remove_think: bool = True) -> dict:
        """Attempts to generate a response using failover handling."""
        state = {"question": question, "answer": "", "model_used": "", "cost": 0, "tokens_used": 0}
        
        try:
            result = self.graph.invoke(state)
            return self._format_response(result, remove_think)
        except Exception as e:
            print("All models failed. Error:", e)
            return {"error": "All models failed."}

    def _format_response(self, state: dict, remove_think: bool) -> dict:
        """Formats response for API output."""
        response = {
            "modelUsed": state["model_used"],
            "cost": state["cost"],
            "tokens": state["tokens_used"],
            "response": state["answer"]
        }

        if remove_think:
            response["response"] = re.sub(r"<think>.*?</think>", "", response["response"], flags=re.DOTALL).strip()

        return response
