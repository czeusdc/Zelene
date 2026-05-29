"""Module: Real LLM provider using the AIMLAPI.com OpenAI-compatible API.

This module implements the LLMProvider interface against the AIMLAPI.com
chat completions endpoint, providing chat, structured-output, and streaming
capabilities via httpx. Falls back to the simulated provider on errors.
"""

import json
import logging
import re
from typing import AsyncIterator

import httpx

from src.agent.tools.base import LLMProvider, AgentMessage
from src.agent.tools.real.prompts import ZELENE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

AIMLAPI_BASE_URL = "https://api.aimlapi.com/v1/chat/completions"
DEFAULT_MODEL = "deepseek/deepseek-v4-pro"


class AIMLAPIProvider(LLMProvider):
    """Real LLM provider powered by AIMLAPI.com's OpenAI-compatible API.

    Uses a persistent httpx.AsyncClient for connection reuse. Supports
    standard chat, JSON-structured output (via response_format), and
    token streaming. Automatically falls back to the simulated provider
    on unrecoverable errors.
    """

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        reasoning_effort: str = "medium",
    ):
        """Initialise the AIMLAPI provider with authentication and model.

        Args:
            api_key: AIMLAPI API key for Bearer authentication.
            model: Model identifier (e.g. deepseek/deepseek-v4-pro).
            reasoning_effort: Reasoning depth — "low", "medium", or "high".
                Lower = faster/cheaper, higher = deeper analysis.
        """
        self.api_key = api_key
        self.model_name = model
        self.simulation_fallback = True
        self.temperature = 0.4
        self.max_tokens = 4096
        self.reasoning_effort = reasoning_effort
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5),
        )

    async def aclose(self):
        """Release the underlying HTTP client connections."""
        await self._client.aclose()

    def _build_payload(
        self,
        messages: list[AgentMessage],
        *,
        json_mode: bool = False,
    ) -> dict:
        """Convert agent messages to OpenAI-compatible JSON payload.

        Prepends the Zelene system prompt as the first message.

        Args:
            messages: Ordered list of agent messages forming the conversation.
            json_mode: If True, request structured JSON output via
                response_format. The prompt must still instruct the model
                to output JSON for this to take effect.

        Returns:
            JSON-serializable dict ready for the API.
        """
        api_messages = [
            {"role": "system", "content": ZELENE_SYSTEM_PROMPT}
        ]
        for m in messages:
            role = "assistant" if m.role == "assistant" else "user"
            api_messages.append({"role": role, "content": m.content})

        payload: dict = {
            "model": self.model_name,
            "messages": api_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "reasoning_effort": self.reasoning_effort,
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        return payload

    async def _post(self, payload: dict) -> dict:
        """Execute a POST request to the AIMLAPI endpoint.

        Uses the persistent AsyncClient for connection reuse.

        Args:
            payload: Full JSON request body.

        Returns:
            Parsed JSON response dict.

        Raises:
            httpx.HTTPError: On HTTP or network failures.
        """
        response = await self._client.post(
            AIMLAPI_BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _extract_text(data: dict) -> str:
        """Extract the model's text response from the API response.

        Args:
            data: Parsed JSON response from AIMLAPI.

        Returns:
            The text content of the first choice's message.
        """
        return data["choices"][0]["message"]["content"]

    async def chat(self, messages: list[AgentMessage]) -> str:
        """Send a conversation to the model and return the full text response.

        Args:
            messages: Ordered list of agent messages forming the conversation.

        Returns:
            The model's text reply, or a simulated fallback response.
        """
        payload = self._build_payload(messages)
        try:
            data = await self._post(payload)
            return self._extract_text(data)
        except Exception as exc:
            logger.error("AIMLAPI chat request failed: %s", exc)
            if self.simulation_fallback:
                return await self._fallback_chat(messages)
            raise

    async def chat_structured(
        self, messages: list[AgentMessage], schema_description: str
    ) -> list[dict] | dict:
        """Send a conversation and parse the response as JSON.

        Uses the API's response_format:json_object for guaranteed valid
        JSON output instead of relying on prompt-based coercion. Strips
        markdown fences as a fallback for providers that still wrap JSON.

        Args:
            messages: Ordered list of agent messages forming the conversation.
            schema_description: Human-readable JSON schema description to
                include in the prompt.

        Returns:
            Parsed JSON as a dict or list of dicts. Returns an empty list on
            parse failure when no fallback is available.
        """
        instruction = AgentMessage(
            role="user",
            content=(
                f"Respond ONLY with valid JSON. Do not wrap in markdown fences. "
                f"Schema: {schema_description}"
            ),
        )
        extended = list(messages) + [instruction]
        payload = self._build_payload(extended, json_mode=True)
        try:
            data = await self._post(payload)
            text = self._extract_text(data)
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
            text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.error("AIMLAPI structured response JSON parse failed: %s", exc)
            if self.simulation_fallback:
                return await self._fallback_chat_structured(messages, schema_description)
            return []
        except Exception as exc:
            logger.error("AIMLAPI structured request failed: %s", exc)
            if self.simulation_fallback:
                return await self._fallback_chat_structured(messages, schema_description)
            return []

    async def stream(self, messages: list[AgentMessage]) -> AsyncIterator[str]:
        """Stream the model's response token-by-token via SSE.

        Uses a separate httpx client with extended timeout for streaming.

        Args:
            messages: Ordered list of agent messages forming the conversation.

        Yields:
            Individual text chunks from the streamed response.
        """
        payload = self._build_payload(messages)
        payload["stream"] = True
        stream_client = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0))
        try:
            async with stream_client.stream(
                "POST",
                AIMLAPI_BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except Exception as exc:
            logger.error("AIMLAPI stream failed: %s", exc)
            yield "I'm having trouble processing that right now."
        finally:
            await stream_client.aclose()

    @staticmethod
    async def _fallback_chat(messages: list[AgentMessage]) -> str:
        """Delegate to the simulated provider as a last resort.

        Args:
            messages: Messages to forward to the simulated provider.

        Returns:
            The simulated provider's response text.
        """
        from src.agent.tools.simulated.llm import SimulatedLLMProvider

        return await SimulatedLLMProvider().chat(messages)

    @staticmethod
    async def _fallback_chat_structured(
        messages: list[AgentMessage], schema_description: str
    ) -> list[dict] | dict:
        """Delegate structured output to the simulated provider.

        Args:
            messages: Messages to forward to the simulated provider.
            schema_description: Schema description (unused by simulated provider).

        Returns:
            An empty list as the simulated fallback for structured output.
        """
        from src.agent.tools.simulated.llm import SimulatedLLMProvider

        await SimulatedLLMProvider().chat(messages)
        return []
