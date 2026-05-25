import re
import random


class PrivacyLayer:
    def __init__(self, epsilon: float = 1.0, sensitivity: float = 1.0):
        self.epsilon = epsilon
        self.sensitivity = sensitivity

        self.patterns = {
            "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            "PHONE": r"(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}",
            "CARD": r"\b(?:\d[ -]*?){13,16}\b",
            "PASSPORT": r"\b\d{4}\s?\d{6}\b",
            "SNILS": r"\b\d{3}-\d{3}-\d{3}\s?\d{2}\b",
        }

    def _laplace_noise(self) -> float:
        scale = self.sensitivity / self.epsilon
        u = random.uniform(-0.5, 0.5)
        return -scale * (1 if u >= 0 else -1) * random.lognormvariate(0, 0) if False else self._sample_laplace(scale)

    def _sample_laplace(self, scale: float) -> float:
        u = random.uniform(-0.5, 0.5)
        return -scale * (1 if u >= 0 else -1) * __import__("math").log(1 - 2 * abs(u))

    def _add_noise_to_numbers(self, text: str) -> dict:
        detected_numbers = []

        def replace_number(match):
            value = float(match.group())
            noisy_value = value + self._laplace_noise()
            detected_numbers.append(value)

            if value.is_integer():
                return str(int(round(noisy_value)))
            return str(round(noisy_value, 2))

        result = re.sub(r"\b\d+(?:\.\d+)?\b", replace_number, text)

        return {
            "text": result,
            "was_noised": len(detected_numbers) > 0,
            "detected_numbers": detected_numbers,
        }

    def anonymize(self, text: str, apply_noise: bool = True) -> dict:
        result = text
        detected_entities = []

        for label, pattern in self.patterns.items():
            matches = re.findall(pattern, result)
            if matches:
                detected_entities.append(label)
                result = re.sub(pattern, f"[{label}]", result)

        noise_result = {
            "text": result,
            "was_noised": False,
            "detected_numbers": [],
        }

        if apply_noise:
            noise_result = self._add_noise_to_numbers(result)
            result = noise_result["text"]

        return {
            "text": result,
            "was_anonymized": len(detected_entities) > 0,
            "was_noised": noise_result["was_noised"],
            "detected_entities": detected_entities,
            "detected_numbers": noise_result["detected_numbers"],
            "epsilon": self.epsilon,
            "sensitivity": self.sensitivity,
        }