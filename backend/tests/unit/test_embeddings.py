import numpy as np
import os
import pytest

from app.embeddings.sentence_transformer_provider import SentenceTransformerEmbeddingProvider


class FakeModel:
    def __init__(self, output=None):
        self.output = output

    def encode(self, texts, **kwargs):
        if self.output is None:
            return np.array([[1.0] * 384 for _ in texts])
        return np.asarray(self.output)


def test_embedding_provider_returns_normalized_384_vectors():
    provider = SentenceTransformerEmbeddingProvider(model_factory=lambda *args, **kwargs: FakeModel())
    vectors = provider.generate(["def hello(): pass"])
    assert len(vectors) == 1
    assert len(vectors[0]) == 384
    assert abs(sum(value * value for value in vectors[0]) - 1.0) < 1e-5


def test_embedding_provider_generates_batches():
    provider = SentenceTransformerEmbeddingProvider(model_factory=lambda *args, **kwargs: FakeModel())
    vectors = provider.generate(["one", "two"])
    assert len(vectors) == 2


def test_embedding_provider_empty_input_does_not_load_model():
    called = False
    def factory(*args, **kwargs):
        nonlocal called
        called = True
        return FakeModel()
    provider = SentenceTransformerEmbeddingProvider(model_factory=factory)
    assert provider.generate([]) == []
    assert called is False


@pytest.mark.parametrize("text", ["", "   ", None])
def test_embedding_provider_rejects_invalid_input(text):
    provider = SentenceTransformerEmbeddingProvider(model_factory=lambda *args, **kwargs: FakeModel())
    with pytest.raises(ValueError, match="non-empty"):
        provider.generate([text])


def test_embedding_provider_rejects_nonfinite_output():
    provider = SentenceTransformerEmbeddingProvider(
        model_factory=lambda *args, **kwargs: FakeModel([[float("nan")] * 384])
    )
    with pytest.raises(ValueError, match="NaN|infinite"):
        provider.generate(["bad"])


def test_embedding_provider_loading_failure_is_reported():
    def factory(*args, **kwargs):
        raise RuntimeError("model unavailable")
    provider = SentenceTransformerEmbeddingProvider(model_factory=factory)
    with pytest.raises(RuntimeError, match="Failed to load embedding model.*model unavailable"):
        provider.generate(["test"])


def test_embedding_provider_rejects_zero_vector():
    provider = SentenceTransformerEmbeddingProvider(
        model_factory=lambda *args, **kwargs: FakeModel([[0.0] * 384])
    )
    with pytest.raises(ValueError, match="zero"):
        provider.generate(["zero"])


@pytest.mark.skipif(
    os.getenv("RUN_REAL_EMBEDDING_SMOKE") != "1",
    reason="Set RUN_REAL_EMBEDDING_SMOKE=1 to download/load the real model",
)
def test_real_sentence_transformer_smoke():
    provider = SentenceTransformerEmbeddingProvider(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        dimension=384,
        device="cpu",
    )
    text_chunks = [
        "def add(left: int, right: int) -> int:\n    return left + right",
        "export function add(left: number, right: number): number { return left + right; }",
    ]
    vectors = provider.generate(text_chunks)
    assert len(vectors) == 2
    for vector in vectors:
        assert len(vector) == 384
        assert np.all(np.isfinite(vector))
        assert np.any(np.asarray(vector) != 0.0)
