"""Module: Real Gemini LLM provider using the Google GenAI SDK.

This module implements the LLMProvider interface against Google's Gemini API,
providing chat, structured-output, and streaming capabilities. Falls back to
the simulated provider when the API is unavailable or returns errors.
"""

import json
import logging
import re
from typing import AsyncIterator

from google import genai
from google.genai import types

from src.agent.tools.base import LLMProvider, AgentMessage
from src.agent.tools.real.prompts import ZELENE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Real LLM provider powered by Google Gemini via the GenAI SDK.

    Wraps a genai.Client instance configured with Zelene's system prompt.
    Supports standard chat, JSON-structured output, and token streaming.
    Automatically falls back to the simulated provider on unrecoverable errors
    when simulation_fallback is enabled.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        """Initialise the Gemini provider and configure the SDK client.

        Args:
            api_key: Google AI API key for authentication.
            model: Gemini model identifier to use.
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model
        self.simulation_fallback = True
        self._config = types.GenerateContentConfig(
            system_instruction=ZELENE_SYSTEM_PROMPT,
            temperature=0.4,
            top_p=0.95,
            max_output_tokens=4096,
        )

    async def chat(self, messages: list[AgentMessage]) -> str:
        """Send a conversation to Gemini and return the full text response.

        Args:
            messages: Ordered list of agent messages forming the conversation.

        Returns:
            The model's text reply, or a simulated fallback response.
        """
        contents = self._to_contents(messages)
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=self._config,
            )
            return response.text
        except Exception as exc:
            logger.error("Gemini chat request failed: %s", exc)
            if self.simulation_fallback:
                return await self._fallback_chat(messages)
            raise

    async def chat_structured(
        self, messages: list[AgentMessage], schema_description: str
    ) -> list[dict] | dict:
        """Send a conversation and parse the response as JSON.

        Appends an instruction message requesting JSON output matching the
        provided schema, then strips markdown fences before parsing.

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
            content=f"Respond ONLY with valid JSON. Schema: {schema_description}",
        )
        extended = list(messages) + [instruction]
        try:
            text = await self.chat(extended)
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
            text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.error("Gemini structured response JSON parse failed: %s", exc)
            if self.simulation_fallback:
                return await self._fallback_chat_structured(messages, schema_description)
            return []
        except Exception as exc:
            logger.error("Gemini structured request failed: %s", exc)
            if self.simulation_fallback:
                return await self._fallback_chat_structured(messages, schema_description)
            return []

    async def stream(self, messages: list[AgentMessage]) -> AsyncIterator[str]:
        """Stream Gemini's response token-by-token.

        Args:
            messages: Ordered list of agent messages forming the conversation.

        Yields:
            Individual text chunks from the model's streamed response.
        """
        contents = self._to_contents(messages)
        try:
            async for chunk in await self.client.aio.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=self._config,
            ):
                if chunk.text is not None:
                    yield chunk.text
        except Exception as exc:
            logger.error("Gemini stream failed: %s", exc)
            yield "I'm having trouble processing that right now."

    @staticmethod
    def _to_contents(messages: list[AgentMessage]) -> list[types.Content]:
        """Convert AgentMessage objects to google.genai Content objects.

        Args:
            messages: List of agent messages to convert.

        Returns:
            List of Content objects suitable for the GenAI SDK.
        """
        role_map = {"user": "user", "assistant": "model"}
        return [
            types.Content(
                role=role_map.get(m.role, "user"),
                parts=[types.Part.from_text(text=m.content)],
            )
            for m in messages
        ]

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
