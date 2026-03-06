
import os
from typing import List, Dict, Any, Optional

# Try to import langchain_ollama, fallback to httpx if needed
try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    import httpx


class OllamaAPI:
    """
    Free local Ollama API for AI inference.
    No API keys required - runs locally using Ollama.
    
    Setup:
    1. Install Ollama: https://ollama.ai
    2. Run: ollama pull llama3.1
    3. Run: ollama serve
    """
    
    def __init__(self, model: str = None, host: str = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1")
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        if OLLAMA_AVAILABLE:
            self.llm = ChatOllama(
                model=self.model,
                base_url=self.host,
                temperature=0.7,
                num_ctx=4096,
            )
        else:
            self.llm = None
    
    def get_model(self) -> str:
        return self.model
    
    def get_completions(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        if OLLAMA_AVAILABLE and self.llm:
            try:
                from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
                
                lc_messages = []
                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        lc_messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        lc_messages.append(AIMessage(content=content))
                    elif role == "system":
                        lc_messages.append(SystemMessage(content=content))
                
                response = self.llm.invoke(lc_messages)
                
                return {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": response.content
                        }
                    }]
                }
            except Exception as e:
                return {"choices": [{"message": {"role": "assistant", "content": f"Error: {str(e)}"}}]}
        else:
            return self._get_completions_http(messages)
    
    def _get_completions_http(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{self.host}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "choices": [{
                        "message": {
                            "role": data.get("message", {}).get("role", "assistant"),
                            "content": data.get("message", {}).get("content", "")
                        }
                    }]
                }
        except Exception as e:
            return {"choices": [{"message": {"role": "assistant", "content": f"Error: {str(e)}"}}]}
    
    def generate(self, prompt: str, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = self.get_completions(messages)
        
        if response.get("choices"):
            return response["choices"][0]["message"]["content"]
        return ""


def get_ollama(model: str = None) -> OllamaAPI:
    return OllamaAPI(model=model)


class LLAMAGATEAPI(OllamaAPI):
    pass

