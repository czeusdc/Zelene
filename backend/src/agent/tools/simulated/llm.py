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
    "on your behalf. Competitors, risks, opportunities, sentiment shifts.\n\n"
    "To begin, I'd like to understand your business. Tell me about your "
    "company. What do you do, and in what industry?"
)


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
        """
        stage = session.get("stage", "introduction")

        # --- introduction ---------------------------------------------------
        if stage == "introduction":
            text = user_message.strip()
            if text and len(text) >= 3:
                extracted_name = _extract_company_name(text)
                session["company_name"] = extracted_name
                session["description"] = text
                session["industry"] = _infer_industry(text)
                session["_intro_shown"] = True
                reply = (
                    f"I see. {session.get('industry', 'This')} is a dynamic space. "
                    f"What would you say makes {extracted_name} different "
                    f"from others in your field?"
                )
                return reply, session, "company"

            session["_intro_shown"] = True
            reply = FULL_INTRODUCTION
            return reply, session, stage

        # --- company ---------------------------------------------------------
        if stage == "company":
            text = user_message.strip()
            if not text or len(text) < 3:
                reply = (
                    "I'd like to understand what sets you apart. "
                    "Could you tell me more about what makes you different?"
                )
                return reply, session, stage

            session["differentiation"] = text
            reply = "Understood. Now, who do you consider your main competitors?"
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
            valid = [c for c in competitors if len(c) >= 4 or " " in c]

            if not valid:
                reply = (
                    "Those don't look like company names. "
                    "Could you list your main competitors? "
                    "For example: 'Salesforce, Microsoft, Oracle'"
                )
                return reply, session, stage

            existing = session.get("competitors", [])
            session["competitors"] = list(set(existing + valid))

            reply = (
                f"Noted. I'm now tracking {', '.join(session['competitors'])}. "
                "One more thing. What matters most to your business right now? "
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
        "Technology": ["tech", "software", "saas", "ai", "cloud", "dev", "data", "platform", "digital",
                       "app", "startup", "automation", "blockchain", "api", "analytics"],
        "Finance": ["fintech", "bank", "finance", "trading", "payment", "crypto", "invest", "lend",
                    "credit", "wealth", "asset", "portfolio", "mortgage", "exchange"],
        "Healthcare": ["health", "medical", "patient", "clinic", "pharma", "biotech", "hospital",
                       "wellness", "diagnostic", "therapeutic", "genomics", "telehealth"],
        "Retail": ["retail", "ecommerce", "shop", "store", "brand", "hardware", "wholesale",
                   "distribution", "seller", "merchant", "marketplace", "d2c"],
        "Manufacturing": ["manufactur", "factory", "supply chain", "steel", "metal", "industrial",
                          "assembly", "production", "warehouse", "machinery", "automotive"],
        "Real Estate": ["real estate", "property", "housing", "construction", "mortgage", "tenant",
                        "landlord", "commercial real estate", "brokerage"],
        "Education": ["education", "learning", "school", "university", "course", "edtech", "training",
                      "academy", "curriculum", "certification", "e-learning", "campus"],
        "Hospitality & Food Service": ["restaurant", "hospitality", "hotel", "catering", "food service",
                                       "bar", "brewery", "lodging", "travel", "tourism", "resort",
                                       "cafe", "meal", "kitchen", "dining", "culinary"],
        "Media & Entertainment": ["media", "entertainment", "streaming", "gaming", "content",
                                  "publish", "broadcast", "video", "music", "podcast", "creator",
                                  "studio", "animation", "gaming", "esports"],
        "Energy": ["energy", "renewable", "solar", "wind", "oil", "gas", "utility", "power",
                   "electric", "grid", "battery", "clean energy", "sustainable", "nuclear"],
        "Insurance": ["insurance", "underwriting", "claims", "actuarial", "insure", "risk",
                      "coverage", "annuity", "reinsurance"],
        "Agriculture": ["agriculture", "farming", "crop", "agri", "forestry", "farm", "organic",
                        "food production", "harvest", "sustainable agriculture"],
        "Telecommunications": ["telecom", "mobile", "network", "broadband", "isp", "wireless",
                               "connectivity", "fiber", "infrastructure", "carrier", "5g"],
        "Legal": ["legal", "law firm", "attorney", "litigation", "compliance", "regulatory",
                  "intellectual property", "corporate law", "paralegal"],
        "Consulting": ["consult", "advisory", "management consulting", "strategy", "consultancy",
                       "professional services", "boutique firm", "analyst"],
        "Cybersecurity": ["cybersecurity", "infosec", "security", "threat", "vulnerability",
                          "endpoint", "zero trust", "encryption", "penetration", "firewall"],
        "Transportation & Logistics": ["logistics", "transport", "shipping", "delivery", "fleet",
                                       "warehouse", "supply chain", "freight", "courier", "mobility"],
    }
    for industry, words in keywords.items():
        if any(w in lower for w in words):
            return industry
    return "Technology"


def _extract_company_name(text: str) -> str:
    """Extract the most likely company name from a user description.

    Skips common first-person pronouns, articles, and filler words to find
    the first meaningful proper noun or capitalized word.
    """
    skip = {
        "we", "our", "my", "i'm", "im", "i", "the", "a", "an", "its", "it",
        "this", "that", "these", "those", "your", "their", "his", "her",
        "we're", "were", "are", "is", "am", "was", "have", "had", "been", "be",
        "and", "or", "but", "if", "then", "also", "just", "so", "not", "no",
        "you", "they", "he", "she", "us", "them", "me",
    }
    words = text.split()
    for w in words:
        clean = w.strip(".,!?'\"").capitalize()
        if clean.lower() not in skip and len(clean) >= 2:
            return clean
    # Fallback: first non-trivial word
    for w in words:
        if len(w) >= 3:
            return w.strip(".,!?'\"").capitalize()
    return text[:50].capitalize()
