from src.agent.tools.base import LLMProvider, AgentMessage
from typing import AsyncIterator

STAGES = ["introduction", "company", "competitors", "goals", "confirm"]

ONBOARDING_SCRIPTS = {
    "introduction": [
        "Welcome. I'm Zelene, your strategic intelligence presence.",
        "Think of me as an analyst who continuously observes your market on your behalf — competitors, risks, opportunities, sentiment shifts.",
        "To begin, I'd like to understand your business. Tell me about your company. What do you do, and in what industry?",
    ],
    "company": [
        "I see. {industry} is a dynamic space.",
        "What would you say makes {name} different from others in your field?",
    ],
    "competitors": [
        "Understood. Now, who do you consider your main competitors?",
    ],
    "goals": [
        "Good. One more thing — what matters most to your business right now?",
    ],
    "confirm": [
        "I believe I have a clear picture now. Take a look at what I've understood.",
    ],
}

class SimulatedLLMProvider(LLMProvider):
    def __init__(self, company_context: dict | None = None):
        self.context = company_context or {}

    async def chat(self, messages: list[AgentMessage]) -> str:
        return "I understand."

    async def stream(self, messages: list[AgentMessage]) -> AsyncIterator[str]:
        yield "Processing..."
        yield ""

    def onboarding_turn(self, user_message: str, session: dict) -> tuple[str, dict, str]:
        stage = session.get("stage", "introduction")
        company_name = session.get("company_name")

        if stage == "introduction":
            session["description"] = user_message
            words = user_message.split()
            session["company_name"] = " ".join(words[:3]) if len(words) > 3 else (user_message[:255] if user_message else "Your Company")
            session["industry"] = "Technology"
            next_stage = "company"
        elif stage == "company":
            next_stage = "competitors"
        elif stage == "competitors":
            competitors = [c.strip() for c in user_message.replace(" and ", ",").split(",") if c.strip()]
            existing = session.get("competitors", [])
            session["competitors"] = list(set(existing + competitors))
            next_stage = "goals" if len(session["competitors"]) > 0 else "competitors"
        elif stage == "goals":
            session["goals"] = [user_message[:200]]
            session["market_focus"] = ["Global"]
            session["concerns"] = []
            next_stage = "confirm"
        elif stage == "confirm":
            next_stage = "complete"
        else:
            next_stage = "complete"

        msg_counts = session.setdefault("_msg_count", {})
        msg_counts[stage] = msg_counts.get(stage, 0) + 1
        idx = msg_counts[stage] - 1
        scripts = ONBOARDING_SCRIPTS.get(stage, ONBOARDING_SCRIPTS["introduction"])

        if stage == "introduction":
            reply = scripts[idx] if idx < len(scripts) else scripts[-1]
        elif stage == "confirm":
            reply = scripts[0]
        else:
            reply = scripts[0].format(name=company_name or "your company", industry=session.get("industry", "this"))

        return reply, session, next_stage
