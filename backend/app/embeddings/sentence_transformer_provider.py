import threading
import math
from typing import Sequence


class SentenceTransformerEmbeddingProvider:
    _models = {}
    _lock = threading.Lock()

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 dimension: int = 384, device: str = "cpu", model_factory=None):
        self.model_name = model_name
        self.dimension = dimension
        self.device = device
        self._model_factory = model_factory
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return self._model
        if self._model_factory is not None:
            try:
                self._model = self._model_factory(self.model_name, device=self.device)
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to load embedding model {self.model_name}: {exc}"
                ) from exc
            return self._model
        key = (self.model_name, self.device)
        with self._lock:
            if key not in self._models:
                try:
                    if self._model_factory is None:
                        from sentence_transformers import SentenceTransformer
                        factory = SentenceTransformer
                    else:
                        factory = self._model_factory
                    model = factory(self.model_name, device=self.device)
                except Exception as exc:
                    raise RuntimeError(
                        f"Failed to load embedding model {self.model_name}: {exc}"
                    ) from exc
                self._models[key] = model
            self._model = self._models[key]
        return self._model

    def generate(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ValueError("Embedding inputs must be non-empty strings")

        model = self._load_model()
        try:
            encoded = model.encode(
                list(texts),
                batch_size=len(texts),
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        except Exception as exc:
            raise RuntimeError(f"Embedding inference failed: {exc}") from exc

        try:
            import numpy as np
            rows = np.asarray(encoded, dtype=float)
            if rows.ndim != 2 or rows.shape != (len(texts), self.dimension):
                raise ValueError(
                    f"Expected {len(texts)}x{self.dimension} embeddings, got {rows.shape}"
                )
            if not np.all(np.isfinite(rows)):
                raise ValueError("Embedding output contains NaN or infinite values")
        except ImportError as exc:
            raise RuntimeError("NumPy is required for embedding validation") from exc

        vectors = []
        for row in rows:
            norm = math.sqrt(sum(float(value) * float(value) for value in row))
            if norm == 0 or not math.isfinite(norm):
                raise ValueError("Embedding output contains a zero or invalid vector")
            vectors.append([float(value / norm) for value in row])
        return vectors
