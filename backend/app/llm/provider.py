from typing import Protocol, runtime_checkable

import httpx


@runtime_checkable
class LLMProvider(Protocol):
    model_name: str

    def generate(self, prompt: str) -> str:
        ...


class LLMConfigurationError(Exception):
    pass


class LLMTimeoutError(Exception):
    pass


class LLMRateLimitError(Exception):
    pass


class LLMProviderError(Exception):
    pass


class LLMMalformedResponseError(Exception):
    pass


class OpenAICompatibleLLMProvider:
    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: float = 30.0,
        max_tokens: int = 800,
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_tokens = max_tokens

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise LLMConfigurationError("LLM provider API key is not configured")
        if not self.model_name:
            raise LLMConfigurationError("LLM model name is not configured")
        if self.timeout_seconds < 1:
            raise LLMConfigurationError("LLM timeout must be at least one second")

        if "SOURCE DATA" in prompt and "USER QUESTION" in prompt:
            system_prompt, remainder = prompt.split("SOURCE DATA", 1)
            source_prompt, question_prompt = remainder.split("USER QUESTION", 1)
            messages = [
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": "SOURCE DATA" + source_prompt.strip()},
                {"role": "user", "content": "USER QUESTION" + question_prompt.strip()},
            ]
        else:
            messages = [{"role": "user", "content": prompt}]

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": "Bearer " + self.api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "temperature": 0,
                        "max_tokens": self.max_tokens,
                        "response_format": {"type": "json_object"},
                    },
                )
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError("LLM provider request timed out") from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError("LLM provider request failed") from exc

        if response.status_code == 429:
            raise LLMRateLimitError("LLM provider rate limit exceeded")
        if response.status_code >= 400:
            raise LLMProviderError("LLM provider returned an error response")

        try:
            payload = response.json()
            content = payload["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise LLMMalformedResponseError("LLM provider returned a malformed response") from exc
        if not isinstance(content, str) or not content.strip():
            raise LLMMalformedResponseError("LLM provider returned an empty response")
        return content.strip()
