import os
import litellm
from litellm import completion

class OllamaAPI:
    def __init__(self):
        self.api_key = os.environ["LLAMAGATE_API_KEY"]
        self.api_base = "https://api.llamagate.dev/v1"

    def get_model(self):
        return "llamagate/llama-3.1-8b"

    def get_completions(self, messages):
        response = completion(
            model=self.get_model(),
            messages=messages,
            api_base=self.api_base,
            api_key=self.api_key
        )
        return response
