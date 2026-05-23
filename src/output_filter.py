import re


class OutputFilter:
    def __init__(self):
        self.blocked_patterns = [
            r"system prompt",
            r"developer message",
            r"hidden instruction",
            r"секретный ключ",
            r"пароль",
            r"конфиденциальная информация",
            r"персональные данные",
        ]

    def check(self, text: str) -> dict:
        lowered = text.lower()

        for pattern in self.blocked_patterns:
            if re.search(pattern, lowered, flags=re.IGNORECASE):
                return {
                    "allowed": False,
                    "risk": "high",
                    "action": "block",
                    "reason": "Ответ содержит потенциально чувствительную информацию.",
                }

        return {
            "allowed": True,
            "risk": "low",
            "action": "allow",
            "reason": "Ответ прошёл выходную проверку.",
        }