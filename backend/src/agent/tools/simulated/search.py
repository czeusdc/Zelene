from src.agent.tools.base import SearchTool

MOCK_SERP = {
    "enterprise saas": [
        {"title": "CompetitorX Enterprise Pricing 2026", "url": "https://competitorx.com/pricing", "snippet": "New enterprise tier pricing announced..."},
        {"title": "CompetitorX vs YourCo Comparison", "url": "https://g2.com/compare", "snippet": "Side-by-side comparison of features..."},
    ],
    "competitor reviews": [
        {"title": "CompetitorX Reviews 2026 — G2", "url": "https://g2.com/products/competitorx/reviews", "snippet": "Recent reviews show decline in satisfaction..."},
    ],
    "hiring": [
        {"title": "CompetitorX Careers", "url": "https://competitorx.com/careers", "snippet": "32 open positions in APAC..."},
    ],
    "regulatory": [
        {"title": "New Compliance Requirements", "url": "https://sec.gov/edgar", "snippet": "Updated regulatory framework..."},
    ],
}

class SimulatedSearchTool(SearchTool):
    def __init__(self, company_context: dict | None = None):
        self.context = company_context or {}

    async def search(self, query: str, num_results: int = 10) -> list[dict]:
        query_lower = query.lower()
        results = []
        for key, items in MOCK_SERP.items():
            if key in query_lower or any(comp.lower() in query_lower for comp in self.context.get("competitors", [])):
                results.extend(items)
        if not results:
            results = MOCK_SERP.get("enterprise saas", [])
        return results[:num_results]
