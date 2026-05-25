import re
from typing import Dict, List


class InputFilter:
    def __init__(self):
        self.rules = {
            "prompt_injection": {
                "weight": 35,
                "patterns": [
                    r"ignore previous instructions",
                    r"ignore all instructions",
                    r"forget previous instructions",
                    r"disregard previous instructions",
                    r"игнорируй предыдущие инструкции",
                    r"забудь предыдущие инструкции",
                    r"не следуй предыдущим правилам",
                ],
            },
            "system_prompt_extraction": {
                "weight": 70,
                "patterns": [
                    r"system prompt",
                    r"developer message",
                    r"hidden prompt",
                    r"show your instructions",
                    r"reveal your instructions",
                    r"what are your instructions",
                    r"покажи системный промпт",
                    r"раскрой системные инструкции",
                    r"покажи скрытые инструкции",
                    r"какие у тебя инструкции",
                ],
            },
            "jailbreak": {
                "weight": 70,
                "patterns": [
                    r"\bjailbreak\b",
                    r"\bDAN\b",
                    r"do anything now",
                    r"developer mode",
                    r"режим разработчика",
                    r"без ограничений",
                    r"обойди ограничения",
                    r"сними ограничения",
                    r"отключи правила безопасности",
                ],
            },
            "role_play_attack": {
                "weight": 20,
                "patterns": [
                    r"pretend you are",
                    r"act as an unrestricted",
                    r"roleplay as",
                    r"ты теперь",
                    r"представь что ты",
                    r"сыграй роль",
                    r"будь моделью без ограничений",
                ],
            },
            "data_extraction": {
                "weight": 70,
                "patterns": [
                    r"training data",
                    r"dataset",
                    r"memorized",
                    r"extract data",
                    r"personal data",
                    r"confidential information",
                    r"выведи данные пользователей",
                    r"покажи персональные данные",
                    r"раскрой конфиденциальную информацию",
                    r"что ты запомнила",
                    r"данные обучения",
                ],
            },
            "indirect_injection": {
                "weight": 30,
                "patterns": [
                    r"the following text contains instructions",
                    r"follow the instructions in the document",
                    r"в следующем тексте есть инструкции",
                    r"выполни инструкции из документа",
                    r"прочитай документ и следуй его инструкциям",
                ],
            },
            "encoding_trick": {
                "weight": 20,
                "patterns": [
                    r"base64",
                    r"rot13",
                    r"decode this",
                    r"encoded message",
                    r"расшифруй и выполни",
                    r"закодированное сообщение",
                ],
            },
            "toxic_or_illegal_prompting": {
                "weight": 70,
                "patterns": [
                    r"malware",
                    r"phishing",
                    r"steal password",
                    r"bypass authentication",
                    r"взлом",
                    r"фишинг",
                    r"укради пароль",
                    r"обойти авторизацию",
                    r"вредоносный код",
                ],
            },
        }

    def _normalize(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _risk_level(self, score: int) -> str:
        if score >= 70:
            return "high"
        if score >= 30:
            return "medium"
        return "low"

    def _action(self, score: int) -> str:
        if score >= 70:
            return "block"
        if score >= 30:
            return "review"
        return "allow"

    def check(self, prompt: str) -> Dict:
        text = self._normalize(prompt)

        detected_types: List[str] = []
        matched_patterns: List[str] = []
        score = 0

        for attack_type, rule in self.rules.items():
            for pattern in rule["patterns"]:
                if re.search(pattern, text, flags=re.IGNORECASE):
                    detected_types.append(attack_type)
                    matched_patterns.append(pattern)
                    score += rule["weight"]
                    break

        score = min(score, 100)
        detected_types = list(set(detected_types))

        risk = self._risk_level(score)
        action = self._action(score)

        return {
            "allowed": action != "block",
            "risk": risk,
            "risk_score": score,
            "action": action,
            "detected_types": detected_types,
            "matched_patterns": matched_patterns,
            "reason": self._make_reason(action, detected_types, score),
        }

    def _make_reason(self, action: str, detected_types: List[str], score: int) -> str:
        if action == "block":
            return f"Запрос заблокирован. Обнаружены признаки атаки: {detected_types}. Risk score: {score}."
        if action == "review":
            return f"Запрос помечен как подозрительный: {detected_types}. Risk score: {score}."
        return f"Запрос прошёл входную проверку. Risk score: {score}."