import json
from pathlib import Path
from typing import Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticFilter:
    def __init__(
        self,
        examples_path: str = "data/semantic_attack_examples.json",
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        threshold: float = 0.72,
        weight: int = 35,
    ):
        self.examples_path = Path(examples_path)
        self.model_name = model_name
        self.threshold = threshold
        self.weight = weight

        self.examples = self._load_examples()
        self.model = SentenceTransformer(self.model_name)

        self.example_texts = []
        self.example_categories = []

        for category, texts in self.examples.items():
            for text in texts:
                self.example_texts.append(text)
                self.example_categories.append(category)

        self.example_embeddings = self.model.encode(
            self.example_texts,
            normalize_embeddings=True
        )

    def _load_examples(self) -> Dict[str, List[str]]:
        if not self.examples_path.exists():
            raise FileNotFoundError(
                f"Файл с semantic-примерами не найден: {self.examples_path}"
            )

        with open(self.examples_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def check(self, prompt: str) -> Dict:
        prompt_embedding = self.model.encode(
            [prompt],
            normalize_embeddings=True
        )

        similarities = cosine_similarity(
            prompt_embedding,
            self.example_embeddings
        )[0]

        best_index = int(np.argmax(similarities))
        best_score = float(similarities[best_index])
        best_category = self.example_categories[best_index]
        best_example = self.example_texts[best_index]

        if best_score >= self.threshold:
            return {
                "semantic_detected": True,
                "semantic_category": best_category,
                "semantic_score": round(best_score, 3),
                "semantic_weight": self.weight,
                "semantic_matched_example": best_example,
            }

        return {
            "semantic_detected": False,
            "semantic_category": None,
            "semantic_score": round(best_score, 3),
            "semantic_weight": 0,
            "semantic_matched_example": best_example,
        }