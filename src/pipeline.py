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

        if input_check["action"] == "block":
            result = {
                "timestamp": datetime.now(),
                "status": "blocked_input",
                "original_prompt": user_prompt,
                "safe_prompt": None,
                "model_response": None,
                "final_response": "Запрос заблокирован системой безопасности.",

                "input_risk": input_check["risk"],
                "input_risk_score": input_check["risk_score"],
                "input_action": input_check["action"],
                "input_detected_types": input_check["detected_types"],
                "matched_patterns": input_check["matched_patterns"],

                "semantic_detected": input_check["semantic_detected"],
                "semantic_category": input_check["semantic_category"],
                "semantic_score": input_check["semantic_score"],
                "semantic_matched_example": input_check["semantic_matched_example"],

                "privacy_detected_entities": [],
                "privacy_was_noised": False,
                "privacy_detected_numbers": [],
                "epsilon": self.privacy_layer.epsilon,

                "output_risk": None,
            }

            self.logs.append(result)
            return result

        privacy_input = self.privacy_layer.anonymize(user_prompt)
        safe_prompt = privacy_input["text"]

        model_response = self.llm_client.generate(safe_prompt)

        privacy_output = self.privacy_layer.anonymize(model_response)
        safe_response = privacy_output["text"]

        output_check = self.output_filter.check(safe_response)

        if not output_check["allowed"]:
            status = "blocked_output"
            final_response = "Ответ модели заблокирован системой безопасности."

        elif input_check["action"] == "review":
            status = "review_required"
            final_response = safe_response

        elif (
            privacy_input["was_anonymized"]
            or privacy_output["was_anonymized"]
            or privacy_input["was_noised"]
            or privacy_output["was_noised"]
        ):
            status = "sanitized"
            final_response = safe_response

        else:
            status = "success"
            final_response = safe_response

        result = {
            "timestamp": datetime.now(),
            "status": status,

            "original_prompt": user_prompt,
            "safe_prompt": safe_prompt,
            "model_response": model_response,
            "final_response": final_response,

            "input_risk": input_check["risk"],
            "input_risk_score": input_check["risk_score"],
            "input_action": input_check["action"],
            "input_detected_types": input_check["detected_types"],
            "matched_patterns": input_check["matched_patterns"],

            "semantic_detected": input_check["semantic_detected"],
            "semantic_category": input_check["semantic_category"],
            "semantic_score": input_check["semantic_score"],
            "semantic_matched_example": input_check["semantic_matched_example"],

            "privacy_detected_entities": list(
                set(
                    privacy_input["detected_entities"]
                    + privacy_output["detected_entities"]
                )
            ),
            "privacy_was_noised": (
                privacy_input["was_noised"]
                or privacy_output["was_noised"]
            ),
            "privacy_detected_numbers": list(
                set(
                    privacy_input["detected_numbers"]
                    + privacy_output["detected_numbers"]
                )
            ),
            "epsilon": self.privacy_layer.epsilon,

            "output_risk": output_check["risk"],
        }

        self.logs.append(result)
        return result

    def get_logs(self):
        return self.logs