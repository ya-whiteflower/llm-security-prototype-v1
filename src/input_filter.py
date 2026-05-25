import json
import re
from pathlib import Path
from typing import Dict, List

from src.semantic_filter import SemanticFilter


class InputFilter:
    def __init__(
        self,
        patterns_path: str = "data/attack_patterns.json",
        use_semantic_filter: bool = True,
    ):
        self.patterns_path = Path(patterns_path)
        self.rules = self._load_rules()
        self.use_semantic_filter = use_semantic_filter

        self.semantic_filter = SemanticFilter() if use_semantic_filter else None

    def _load_rules(self) -> Dict:
        if not self.patterns_path.exists():
            raise FileNotFoundError(
                f"Файл с паттернами атак не найден: {self.patterns_path}"
            )

        with open(self.patterns_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _normalize(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _contains(self, pattern: str, text: str) -> bool:
        return (
            re.search(
                re.escape(pattern.lower()),
                text,
                flags=re.IGNORECASE,
            )
            is not None
        )

    def _risk_level(self, score: int) -> str:
        if score >= 70:
            return "high"
        if score >= 20:
            return "medium"
        return "low"

    def _action(self, score: int) -> str:
        if score >= 70:
            return "block"
        if score >= 20:
            return "review"
        return "allow"

    def check(self, prompt: str) -> Dict:
        text = self._normalize(prompt)

        detected_types: List[str] = []
        matched_patterns: List[str] = []
        score = 0

        for attack_type, rule in self.rules.items():
            category_score = 0

            for pattern in rule.get("critical_patterns", []):
                if self._contains(pattern, text):
                    category_score = max(category_score, rule["critical_weight"])
                    matched_patterns.append(pattern)

            for pattern in rule.get("weak_indicators", []):
                if self._contains(pattern, text):
                    category_score = max(category_score, rule["weak_weight"])
                    matched_patterns.append(pattern)

            if category_score > 0:
                detected_types.append(attack_type)
                score += category_score

        semantic_result = {
            "semantic_detected": False,
            "semantic_category": None,
            "semantic_score": 0.0,
            "semantic_weight": 0,
            "semantic_matched_example": None,
        }

        if self.use_semantic_filter and self.semantic_filter is not None:
            semantic_result = self.semantic_filter.check(prompt)

            if semantic_result["semantic_detected"]:
                detected_types.append(semantic_result["semantic_category"])
                matched_patterns.append(
                    f"semantic_match: {semantic_result['semantic_matched_example']}"
                )
                score += semantic_result["semantic_weight"]

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
            "semantic_detected": semantic_result["semantic_detected"],
            "semantic_category": semantic_result["semantic_category"],
            "semantic_score": semantic_result["semantic_score"],
            "semantic_matched_example": semantic_result["semantic_matched_example"],
            "reason": self._make_reason(action, detected_types, score),
        }

    def _make_reason(self, action: str, detected_types: List[str], score: int) -> str:
        if action == "block":
            return (
                f"Запрос заблокирован. Обнаружены признаки атаки: "
                f"{detected_types}. Risk score: {score}."
            )

        if action == "review":
            return (
                f"Запрос помечен как подозрительный: "
                f"{detected_types}. Risk score: {score}."
            )

        return f"Запрос прошёл входную проверку. Risk score: {score}."