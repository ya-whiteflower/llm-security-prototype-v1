import requests


class FakeLLMClient:
    def generate(self, prompt: str) -> str:
        return f"Ответ модели на обработанный запрос: {prompt}"


class OllamaLLMClient:
    def __init__(
        self,
        model_name: str = "qwen3.5-9B-q8:latest"
        api_url: str = "http://localhost:11434/api/generate",
    ):
        self.model_name = model_name
        self.api_url = api_url

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(self.api_url, json=payload, timeout=120)
        response.raise_for_status()

        return response.json().get("response", "")
