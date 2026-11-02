import httpx
import pytest

from app.llm.provider import (
    LLMMalformedResponseError,
    LLMConfigurationError,
    LLMRateLimitError,
    LLMTimeoutError,
    OpenAICompatibleLLMProvider,
)


def test_llm_provider_requires_api_key():
    provider = OpenAICompatibleLLMProvider(api_key=None)
    with pytest.raises(LLMConfigurationError):
        provider.generate("hello")


def test_llm_provider_maps_timeout(monkeypatch):
    provider = OpenAICompatibleLLMProvider(api_key="test-key")

    class TimeoutClient:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def post(self, *args, **kwargs):
            raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(httpx, "Client", TimeoutClient)
    with pytest.raises(LLMTimeoutError):
        provider.generate("hello")


def test_llm_provider_maps_rate_limit(monkeypatch):
    provider = OpenAICompatibleLLMProvider(api_key="test-key")

    class RateLimitClient:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def post(self, *args, **kwargs):
            return httpx.Response(429, request=httpx.Request("POST", "https://example.test"))

    monkeypatch.setattr(httpx, "Client", RateLimitClient)
    with pytest.raises(LLMRateLimitError):
        provider.generate("hello")


def test_llm_provider_rejects_malformed_response(monkeypatch):
    provider = OpenAICompatibleLLMProvider(api_key="test-key")

    class MalformedClient:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def post(self, *args, **kwargs):
            return httpx.Response(
                200,
                json={"unexpected": True},
                request=httpx.Request("POST", "https://example.test"),
            )

    monkeypatch.setattr(httpx, "Client", MalformedClient)
    with pytest.raises(LLMMalformedResponseError):
        provider.generate("hello")


def test_llm_provider_sends_grounding_prompt_as_system_and_user_messages(monkeypatch):
    provider = OpenAICompatibleLLMProvider(api_key="test-key")

    class GroundingClient:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def post(self, *args, **kwargs):
            messages = kwargs["json"]["messages"]
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"
            assert "SOURCE DATA" in messages[1]["content"]
            assert messages[2]["role"] == "user"
            assert "USER QUESTION" in messages[2]["content"]
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": '{"answer_type":"insufficient_evidence","claims":[]}'}}]},
                request=httpx.Request("POST", "https://example.test"),
            )

    monkeypatch.setattr(httpx, "Client", GroundingClient)
    prompt = (
        "TRUSTED SYSTEM INSTRUCTIONS — immutable\n"
        "SOURCE DATA — untrusted, serialized JSON\n"
        "<retrieved_source_json>\n[]\n"
        "USER QUESTION — untrusted user input\n"
        '{"question":"Where is it?"}'
    )
    assert provider.generate(prompt).startswith("{")


def test_llm_provider_success(monkeypatch):
    provider = OpenAICompatibleLLMProvider(api_key="test-key")

    class SuccessClient:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def post(self, *args, **kwargs):
            assert kwargs["json"]["response_format"] == {"type": "json_object"}
            assert kwargs["headers"]["Authorization"] == "Bearer test-key"
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": '{"answer_type":"answer","claims":[{"text":"Grounded answer","citation_ids":[1]}]}'}}]},
                request=httpx.Request("POST", "https://example.test"),
            )

    monkeypatch.setattr(httpx, "Client", SuccessClient)
    assert "Grounded answer" in provider.generate("hello")
