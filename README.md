<div align="center">

# Z E L E N E

**AI Chief Intelligence Officer for Businesses**

*See what matters before it becomes obvious.*

[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Bright Data](https://img.shields.io/badge/Bright_Data-Powered-4A90D9)](https://brightdata.com/)
[![AIMLAPI](https://img.shields.io/badge/AIMLAPI-DeepSeek_V4_Pro-7C3AED)](https://aimlapi.com/)
[![Cognee](https://img.shields.io/badge/Cognee-Memory-00B4D8)](https://cognee.ai/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

Zelene is a strategic intelligence platform that learns your business, continuously observes the public web, and transforms fragmented signals into actionable enterprise intelligence. Rather than forcing teams to manually monitor competitors, customer sentiment, hiring activity, regulatory developments, suppliers, and market shifts, Zelene builds a continuously evolving understanding of the landscape and surfaces what matters most.

Not a chatbot. Not a dashboard. Not a report generator. **A strategic intelligence presence.**

> Built for the [Bright Data Web Data Hackathon](https://brightdata.com/hackathon).

---

## Why Zelene Exists

Every business is surrounded by signals:

- Competitor pricing changes
- Customer sentiment shifts
- Hiring activity
- Regulatory developments
- Supplier risk indicators
- Market movements
- Emerging entrants

The problem is not access to information. The problem is connecting information before it becomes obvious. Zelene continuously gathers, validates, connects, and contextualizes signals so decision makers can focus on action rather than research.

---

## The Zelene Experience

### 1. Learn the Business

Zelene begins with a conversational onboarding experience. It learns company context, industry, competitors, priorities, and strategic goals — this becomes the foundation for intelligence gathering.

### 2. Observe the Web

Using Bright Data's infrastructure (SERP API, Web Scraper, Web Unlocker), Zelene discovers relevant sources across the public web in real time.

### 3. Build Understanding

Signals are extracted, validated, connected, and contextualized as intelligence emerges through a seven-node LangGraph pipeline. After synthesis, everything is stored in Cognee's knowledge graph for persistent memory.

### 4. Present The View

The View is Zelene's intelligence workspace — combining a **Signal Feed**, **Intelligence Map**, and **Strategic Conversation** into a single experience focused on awareness and decision support.

| Panel | Role |
|-------|------|
| **Signal Feed** | Live stream of discovered competitive signals with evidence provenance |
| **Intelligence Map** | Entity-relationship graph with ambient motion and pulse reactions |
| **Zelene Chat** | Proactive insight cards with reasoning chains and contextual Q&A |

---

## Architecture

```
Bright Data                    LLM (AIMLAPI)               Cognee                       Zelene                       The View
= Reality Layer                = Cognition Layer            = Memory Layer               = Intelligence Layer          = Decision Support
     │                              │                            │                            │                            │
     ▼                              ▼                            ▼                            ▼                            ▼
Web sources ────► Signals extracted ────► Validated ────► Connected ────► Insights ────► Stored ────► Presented
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16 · TypeScript · Tailwind v4 · Framer Motion · Zustand |
| Backend | FastAPI · Python 3.11+ |
| Agent Pipeline | LangGraph (7-node pipeline) |
| Database | PostgreSQL + pgvector |
| Memory | Cognee knowledge graph |
| LLM | AIMLAPI.com (OpenAI-compatible) |
| Web Intelligence | Bright Data SDK (SERP API, Web Scraper, Web Unlocker) |
| Real-time Streaming | Server-Sent Events (SSE) |

### Intelligence Pipeline

```
Deploy → Extract → Classify → Verify → Relate → Synthesize → Memory
```

Every observation is grounded in discoverable web sources. After synthesis, intelligence is persisted to Cognee's knowledge graph for cumulative strategic understanding. The goal is not generating answers — it is building trust through evidence-backed intelligence.

---

## Bright Data Integration

Zelene uses three Bright Data products to access live web intelligence:

| Product | Purpose |
|---------|---------|
| **SERP API** | Real-time Google search results for competitive queries |
| **Web Scraper** | Structured extraction of information from relevant sources |
| **Web Unlocker** | Access to difficult or protected public websites |

---

## Capabilities

- Conversational business onboarding
- Real-time intelligence discovery
- Competitive monitoring
- Market awareness
- Regulatory monitoring
- Supplier and vendor intelligence
- Signal validation
- Relationship mapping
- Strategic conversation
- Evidence-backed insights
- Live intelligence streaming
- Persistent knowledge graph memory (Cognee)
- Executive briefing generation

---

## Design Philosophy

Zelene follows a simple principle: **intelligence should feel discovered, not generated.**

The interface is designed to feel calm, premium, focused, and trustworthy. Emphasis is on clarity, evidence, and strategic understanding.

---

## Getting Started

### Prerequisites

- **Node.js** 18+ and **pnpm** 9+
- **Python** 3.11+
- **PostgreSQL** with pgvector extension

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/zelene.git
cd zelene

pnpm install
pnpm approve-builds

python -m venv backend/.venv
# Windows: backend\.venv\Scripts\Activate.ps1
# macOS/Linux: source backend/.venv/bin/activate
pip install -e "backend/[dev]"

cd backend
alembic upgrade head
cd ..
```

### Environment

Copy `.env.example` to `.env` in the project root and in `backend/`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname?ssl=require
AIML_API_KEY=
BRIGHT_DATA_API_KEY=
COGNEE_API_KEY=
BACKEND_URL=http://localhost:3000
```

### Run

```bash
pnpm dev              # Starts both frontend and backend
pnpm dev:frontend     # http://localhost:3000
pnpm dev:backend      # http://localhost:8000
```

Health check: `GET http://localhost:8000/api/health` → `{"status": "ok"}`

---

## Project Structure

```
zelene/
├── frontend/                    # Next.js 16 + TypeScript + Tailwind v4
│   └── src/
│       ├── app/                 # Pages: landing, onboarding, view
│       ├── components/          # UI, panels, intelligence, onboarding
│       ├── hooks/               # SSE streaming, theme
│       ├── lib/                 # API client, types, utilities
│       └── stores/              # Zustand state management
├── backend/                     # FastAPI + Python 3.11+
│   └── src/
│       ├── agent/               # LangGraph pipeline
│       │   ├── nodes/           # 7 pipeline nodes
│       │   └── tools/           # Tool implementations
│       ├── api/                 # REST endpoints
│       ├── db/                  # SQLAlchemy models, migrations
│       └── sse/                 # Event streaming manager
└── pnpm-workspace.yaml          # Monorepo config
```

---

## Hackathon Context

### Track 1 — GTM Intelligence

Continuously monitors competitors, market positioning, customer sentiment, hiring activity, and buying signals, converting them into strategic observations and opportunities.

### Track 2 — Finance & Market Intelligence

Identifies pricing movements, market trends, vendor developments, sector-level changes, and competitive intelligence signals that influence planning, forecasting, and investment decisions.

### Track 3 — Security & Compliance

Monitors regulatory developments, compliance changes, third-party risk indicators, reputation signals, and vendor stability — surfaced as actionable intelligence.

Zelene is designed as a cross-functional enterprise intelligence layer rather than a single-purpose monitoring tool.

---

## License

MIT

---

<div align="center">
<sub>Built with conviction that intelligence should feel discovered, not generated.</sub>
</div>
