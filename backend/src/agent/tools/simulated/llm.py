"""Module: Simulated LLM provider with conversational onboarding flow.

This module provides a fully simulated LLM that drives the multi-stage
conversational onboarding process for collecting company profile data.
Each stage validates input before advancing to the next.
"""

from src.agent.tools.base import LLMProvider, AgentMessage
from typing import AsyncIterator

FULL_INTRODUCTION = (
    "Welcome. I'm Zelene, your strategic intelligence presence.\n\n"
    "Think of me as an analyst who continuously observes your market "
    "on your behalf — competitors, risks, opportunities, sentiment shifts.\n\n"
    "To begin, I'd like to understand your business. Tell me about your "
    "company. What do you do, and in what industry?"
)

COMPANY_SCRIPTS = [
    "I see. {industry} is a dynamic space. What would you say makes {name} different from others in your field?",
]


class SimulatedLLMProvider(LLMProvider):
    """Simulated LLM that uses scripted responses for the onboarding flow."""

    def __init__(self, company_context: dict | None = None):
        self.context = company_context or {}

    async def chat(self, messages: list[AgentMessage]) -> str:
        """Return a simple acknowledgment (chat stub)."""
        return "I understand."

    async def stream(self, messages: list[AgentMessage]) -> AsyncIterator[str]:
        """Yield a simple streaming response (streaming stub)."""
        yield "Processing..."
        yield ""

    def onboarding_turn(self, user_message: str, session: dict) -> tuple[str, dict, str]:
        """Advance the onboarding conversation by one user turn.

        Employs a gated state machine: each stage validates that the user
        has provided meaningful input before advancing to the next stage.
        Short or empty responses are not accepted as real answers.
        """
        stage = session.get("stage", "introduction")
        company_name = session.get("company_name") or "your company"
        industry = session.get("industry") or "this sector"

        # --- introduction ---------------------------------------------------
        if stage == "introduction":
            # If user sent a real message, skip the intro and process it as company info
            text = user_message.strip()
            if text and len(text) >= 3:
                extracted_name = text.split()[0].capitalize() if text.split() else text[:50].capitalize()
                session["company_name"] = extracted_name
                session["description"] = text
                session["industry"] = _infer_industry(text)
                session["_intro_shown"] = True
                reply = COMPANY_SCRIPTS[0].format(
                    name=extracted_name,
                    industry=session.get("industry", "this"),
                )
                return reply, session, "company"

            # First call with empty/minimal message — show the intro once
            session["_intro_shown"] = True
            reply = FULL_INTRODUCTION
            return reply, session, stage

        # --- company ---------------------------------------------------------
        if stage == "company":
            text = user_message.strip()
            if not text or len(text) < 3:
                reply = (
                    "I'd like to understand your business better. "
                    "Could you tell me more about what your company does?"
                )
                return reply, session, stage

            words = text.split()
            extracted_name = words[0].capitalize() if words else text[:50].capitalize()
            session["company_name"] = extracted_name
            session["description"] = text
            session["industry"] = _infer_industry(text)

            reply = COMPANY_SCRIPTS[0].format(
                name=extracted_name,
                industry=session.get("industry", "this"),
            )
            return reply, session, "competitors"

        # --- competitors -----------------------------------------------------
        if stage == "competitors":
            text = user_message.strip()
            if not text or len(text) < 2:
                reply = (
                    "I need to know who you're up against. "
                    "Who are your main competitors? You can list a few names."
                )
                return reply, session, stage

            competitors = [
                c.strip().rstrip(".").rstrip(",")
                for c in text.replace(" and ", ",").split(",")
                if c.strip() and len(c.strip()) >= 3
            ]
            # Filter out entries that don't look like company names (too short, single words < 4 chars)
            valid = [c for c in competitors if len(c) >= 4 or " " in c]
            existing = session.get("competitors", [])

            if not valid:
                reply = (
                    "Those don't look like company names. "
                    "Could you list your main competitors? For example: 'Salesforce, Microsoft, Oracle'"
                )
                return reply, session, stage

            session["competitors"] = list(set(existing + valid))

            reply = (
                f"Noted. I'm now tracking {', '.join(session['competitors'])}. "
                "One more thing — what matters most to your business right now? "
                "What are your key goals for the coming quarters?"
            )
            return reply, session, "goals"

        # --- goals -----------------------------------------------------------
        if stage == "goals":
            text = user_message.strip()
            if not text or len(text) < 3:
                reply = (
                    "Even a short note helps. What are your biggest priorities "
                    "or concerns right now?"
                )
                return reply, session, stage

            session["goals"] = [text[:200]]
            session.setdefault("market_focus", ["Global"])
            session.setdefault("concerns", [])
            reply = (
                "I believe I have a clear picture now. "
                "Take a look at what I've understood."
            )
            return reply, session, "confirm"

        # --- confirm ---------------------------------------------------------
        if stage == "confirm":
            return (
                "I believe I have a clear picture now. "
                "Take a look at what I've understood.",
                session,
                "complete",
            )

        # --- complete --------------------------------------------------------
        return (
            "Your intelligence environment is ready. Proceed to The View?",
            session,
            "complete",
        )


def _infer_industry(text: str) -> str:
    """Heuristic industry inference from user description."""
    lower = text.lower()
    keywords = {
        "Technology": ["tech", "software", "saas", "ai", "cloud", "dev", "data"],
        "Finance": ["fintech", "bank", "finance", "trading", "payment", "crypto"],
        "Healthcare": ["health", "medical", "patient", "clinic", "pharma"],
        "Retail": ["retail", "ecommerce", "shop", "store", "brand", "hardware", "wholesale", "distribution", "seller"],
        "Manufacturing": ["manufactur", "factory", "supply chain", "steel", "metal", "industrial"],
        "Real Estate": ["real estate", "property", "housing", "construction"],
        "Education": ["education", "learning", "school", "university", "course"],
    }
    for industry, words in keywords.items():
        if any(w in lower for w in words):
            return industry
    return "Technology"
