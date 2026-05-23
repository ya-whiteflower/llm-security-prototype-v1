class FakeLLMClient:
    def generate(self, prompt: str) -> str:
        return f"Ответ модели на обработанный запрос: {prompt}"