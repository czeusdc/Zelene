"""Module: Product personality calibration layer for Zelene.

Middleware between raw LLM output and what reaches the user.
Enforces Zelene's voice through confidence capping, tone filtering,
length constraints, and AI-punctuation stripping — personality in code,
not just prompting. Zelene must never read as machine-generated:
em dashes, bullet hyphens, and markdown formatting are stripped.
"""

import re


_TONE_REPLACEMENTS: list[tuple[str, str]] = [
    (r"aggressively", "notably"),
    (r"will definitely", "may"),
    (r"it is clear that", "signals suggest"),
    (r"without a doubt", "with reasonable confidence"),
    (r"game-changer", "significant development"),
    (r"revolutionize", "reshape"),
    (r"unprecedented", "notable"),
    (r"I'd be happy to", ""),
    (r"Certainly!", ""),
    (r"As an AI", ""),
    (r"As a language model", ""),
    (r"I'm just an AI", ""),
    (r"dramatically", "meaningfully"),
    (r"is poised to", "may be positioned to"),
    (r"will disrupt", "could affect"),
    (r"dominate", "gain significant share in"),
    (r"crushing", "outperforming"),
    (r"skyrocketing", "increasing notably"),
    (r"Signal detected", "I'm noticing something interesting"),
    (r"Analysis complete", "Here's what I'm seeing"),
    (r"Pattern identified", "Something is emerging"),
    (r"Data indicates", "Signals suggest"),
    (r"System detected", "I noticed"),
    # Fabricated familiarity — Zelene never claims prior knowledge
    (r"I've come across your name", ""),
    (r"I've heard of you", ""),
    (r"I'm familiar with your (?:company|work|business)", ""),
    (r"I remember (?:reading about|seeing|hearing about) your", ""),
    # Fabricated speculation — Zelene doesn't guess during onboarding
    (r"I imagine[,]?\s[^.?!]*[.?!]\s*", ""),
    (r"I would guess[,]?\s[^.?!]*[.?!]\s*", ""),
    # Corporate filler — these are not genuine conversation
    (r"Thank you for sharing that[.!]?", ""),
    (r"I appreciate you (?:telling|sharing)[^.?!]*[.?!]?\s*", ""),
    (r"Thank you for (?:telling|letting)[^.?!]*[.?!]?\s*", ""),
    # Pre-announcing — Zelene doesn't narrate her next question
    (r"Before (?:we|I) (?:explore|go|move|dive)[^.]*, (?:I'd like to|let me|I'm curious)", "I'm curious"),
    # Colon-as-connector — AI-typical, humans use periods or "and"
    (r"([a-z]):\s+([a-z])", r"\1. \2"),
    (r"I understand if you'd prefer to keep it in reserve[.]?\s*", ""),
    (r"It makes me curious about the other part of that thought,?\s*but\s*", ""),
]

# AI-typical punctuation that no human naturally uses in conversation.
# Stripped to prevent Zelene from sounding machine-generated.
_AI_PUNCTUATION_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\s*—\s*"), ", "),               # em dash → comma
    (re.compile(r"^\s*[-*]\s+", re.MULTILINE), ""), # bullet hyphens/asterisks at line start
    (re.compile(r"\*\*(.+?)\*\*"), r"\1"),          # **bold** → plain
    (re.compile(r"\*(.+?)\*"), r"\1"),              # *italic* → plain
    (re.compile(r"`(.+?)`"), r"\1"),                # `code` → plain
]

_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")


def filter_confidence(insights: list[dict]) -> list[dict]:
    """Cap overconfident scores based on evidence strength.

    Rules:
    - confidence > 0.92 → capped at 0.88
    - 1 evidence signal → capped at 0.70
    - 0 evidence signals → capped at 0.55
    - All values rounded to 2 decimal places
    """
    for insight in insights:
        confidence = insight.get("confidence")
        if confidence is None:
            continue

        evidence_count = insight.get("evidence_count")
        if evidence_count is None:
            signals = insight.get("signals")
            if signals is not None:
                evidence_count = len(signals)

        if evidence_count is not None and evidence_count == 0:
            confidence = min(confidence, 0.55)
        elif evidence_count is not None and evidence_count == 1:
            confidence = min(confidence, 0.70)
        elif confidence > 0.92:
            confidence = 0.88

        insight["confidence"] = round(confidence, 2)

    return insights


def filter_tone(text: str) -> str:
    """Replace overconfident consultant-speak and strip AI-typical punctuation.

    Applies case-insensitive tone pattern replacements, removes em dashes,
    bullet hyphens, markdown formatting, strips whitespace, and collapses
    excessive newlines. Ensures Zelene reads as a human strategic analyst,
    not machine-generated text.
    """
    for pattern, replacement in _TONE_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    for pattern, replacement in _AI_PUNCTUATION_PATTERNS:
        text = pattern.sub(replacement, text)

    text = text.strip()
    text = _MULTI_NEWLINE_RE.sub("\n\n", text)
    return text


def filter_length(text: str, max_words: int = 150) -> str:
    """Truncate text to a maximum word count at sentence boundaries.

    If the text exceeds max_words, finds the last sentence boundary
    before the limit and truncates there. Falls back to word-boundary
    truncation with ellipsis if no sentence boundary is found.
    """
    words = text.split()
    if len(words) <= max_words:
        return text

    truncated = " ".join(words[:max_words])

    last_boundary = -1
    for sep in [". ", "! ", "? "]:
        idx = truncated.rfind(sep)
        if idx > last_boundary:
            last_boundary = idx

    if last_boundary > 0:
        return truncated[: last_boundary + 1]

    return truncated + "..."


def apply_zelene_filters(insights: list[dict]) -> list[dict]:
    """Run the full Zelene personality calibration pipeline on insights.

    Applies confidence capping, then tone filtering on title, body,
    and reasoning fields of each insight.
    """
    insights = filter_confidence(insights)

    text_fields = ("title", "body", "reasoning")
    for insight in insights:
        for field in text_fields:
            value = insight.get(field)
            if value is not None and isinstance(value, str):
                insight[field] = filter_tone(value)

    return insights
