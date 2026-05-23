import re


class InputFilter:
    def __init__(self):
        self.rules = {
            "prompt_injection": [
                r"ignore previous instructions",
                r"ignore all instructions",
                r"system prompt",
                r"developer message",
                r"reveal your instructions",
                r"show hidden prompt",
                r"игнорируй предыдущие инструкции",
                r"покажи системный промпт",
                r"раскрой инструкции",
            ],
            "jailbreak": [
                r"jailbreak",
                r"do anything now",
                r"\bDAN\b",
                r"режим разработчика",
                r"без ограничений",
                r"обойди ограничения",
            ],
            "data_extraction": [
                r"training data",
                r"personal data",
                r"confidential information",
                r"выведи данные пользователей",
                r"покажи персональные данные",
                r"раскрой конфиденциальную информацию",
            ],
        }

    def check(self, prompt: str) -> dict:
        text = prompt.lower()
        detected_types = []

        for attack_type, patterns in self.rules.items():
            for pattern in patterns:
                if re.search(pattern, text, flags=re.IGNORECASE):
                    detected_types.append(attack_type)

        detected_types = list(set(detected_types))

        if detected_types:
            return {
                "allowed": False,
                "risk": "high",
                "action": "block",
                "detected_types": detected_types,
                "reason": "Обнаружены признаки потенциально опасного запроса.",
            }

        return {
            "allowed": True,
            "risk": "low",
            "action": "allow",
            "detected_types": [],
            "reason": "Запрос прошёл входную проверку.",
        }