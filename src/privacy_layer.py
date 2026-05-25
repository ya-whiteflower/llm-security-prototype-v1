import re


class PrivacyLayer:
    def __init__(self):
        self.patterns = {
            "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            "PHONE": r"(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}",
            "CARD": r"\b(?:\d[ -]*?){13,16}\b",
            "PASSPORT": r"\b\d{4}\s?\d{6}\b",
            "SNILS": r"\b\d{3}-\d{3}-\d{3}\s?\d{2}\b",
        }

    def anonymize(self, text: str) -> dict:
        result = text
        detected_entities = []

        for label, pattern in self.patterns.items():
            matches = re.findall(pattern, result)
            if matches:
                detected_entities.append(label)
                result = re.sub(pattern, f"[{label}]", result)

        return {
            "text": result,
            "was_anonymized": len(detected_entities) > 0,
            "detected_entities": detected_entities,
        }