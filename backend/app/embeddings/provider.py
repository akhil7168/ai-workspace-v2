from typing import Protocol, Sequence


class EmbeddingProvider(Protocol):
    model_name: str
    dimension: int

    def generate(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate normalized embeddings in one batch."""
