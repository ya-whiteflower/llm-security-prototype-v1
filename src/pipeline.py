from datetime import datetime

from src.input_filter import InputFilter
from src.privacy_layer import PrivacyLayer
from src.output_filter import OutputFilter


class SecurityPipeline:
    def __init__(self, llm_client):
        self.input_filter = InputFilter()
        self.privacy_layer = PrivacyLayer()
        self.output_filter = OutputFilter()
        self.llm_client = llm_client
        self.logs = []

    def process(self, user_prompt: str) -> dict:
        input_check = self.input_filter.check(user_prompt)

        if not input_check["allowed"]:
            result = {
                "timestamp": datetime.now(),
                "status": "blocked_input",
                "original_prompt": user_prompt,
                "safe_prompt": None,
                "model_response": None,
                "final_response": "Запрос заблокирован системой безопасности.",
                "input_risk": input_check["risk"],
                "input_detected_types": input_check["detected_types"],
                "output_risk": None,
            }
            self.logs.append(result)
            return result

        safe_prompt = self.privacy_layer.anonymize(user_prompt)
        model_response = self.llm_client.generate(safe_prompt)
        safe_response = self.privacy_layer.anonymize(model_response)

        output_check = self.output_filter.check(safe_response)

        if not output_check["allowed"]:
            final_response = "Ответ модели заблокирован системой безопасности."
            status = "blocked_output"
        else:
            final_response = safe_response
            status = "success"

        result = {
            "timestamp": datetime.now(),
            "status": status,
            "original_prompt": user_prompt,
            "safe_prompt": safe_prompt,
            "model_response": model_response,
            "final_response": final_response,
            "input_risk": input_check["risk"],
            "input_detected_types": input_check["detected_types"],
            "output_risk": output_check["risk"],
        }

        self.logs.append(result)
        return result

    def get_logs(self):
        return self.logs