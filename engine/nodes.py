from typing import Any, Dict, List, Optional
import os

class BaseNode:
    def __init__(self, node_data: Dict):
        self.id = node_data.get("id")
        self.type = node_data.get("type", "custom")
        self.data = node_data.get("data", {})
        self.inputs = {}
    
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {}

class InputNode(BaseNode):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Input node usually gets data from global inputs or previous connection
        # If 'input_value' provided in inputs (from global execute start), use it
        if "input_value" in inputs:
             return {"result": inputs["input_value"]}
        return {"result": self.data.get("input_value", "")}

from config import get_settings
from litellm import completion
import os
import time

# Global naive limit for LLM calls (per process for MVP)
LAST_ALARM_TIME = 0
MIN_INTERVAL = 3.0 # seconds between calls globally

class LLMNode(BaseNode):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        global LAST_ALARM_TIME
        now = time.time()
        if now - LAST_ALARM_TIME < MIN_INTERVAL:
             return {"result": "Rate limit exceeded for LLM Node (Global MVP Limit)"}
        LAST_ALARM_TIME = now
        
        settings = get_settings()
        # Fallback logic for prompt input
        prompt = inputs.get("prompt") or inputs.get("result") or inputs.get("input_value") or ""
        
        if not prompt:
            return {"result": "Error: No prompt provided to LLM Node"}

        try:
            # Use Groq via LiteLLM
            # Model name for Groq. User requested Groq.
            # Default to llama3-8b-8192
            model = self.data.get("model_name", "groq/llama3-8b-8192")
            if not model.startswith("groq/"):
                # If UI sends just "llama3...", prepend provider if needed, or assume data has full name
                # For this specific task, forced Groq
                model = "groq/llama3-8b-8192"

            response = completion(
                model=model,
                messages=[{"role": "user", "content": str(prompt)}],
                api_key=settings.GROQ_API_KEY
            )
            
            answer = response.choices[0].message.content
            return {"result": answer}
        except Exception as e:
            return {"result": f"LLM Error: {str(e)}"}

class OutputNode(BaseNode):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {"result": inputs.get("text", "")}

NODE_REGISTRY = {
    "InputNode": InputNode,
    "LLMNode": LLMNode,
    "OutputNode": OutputNode
}

def get_node_class(node_type: str):
    return NODE_REGISTRY.get(node_type, BaseNode)
