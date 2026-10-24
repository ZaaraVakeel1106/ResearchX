# Research X

**Discover research. Connect ideas. Trace evidence.**

Research X is a research-paper discovery and exploration platform designed to help students and researchers find academic literature, understand papers, navigate citation networks, compare findings, and organize their research.

Rather than stopping at a list of search results, Research X aims to connect the stages of research: discovery, reading, evidence verification, exploration, and organization.

> **Project status:** The FastAPI and React foundation and a stateless OpenAlex paper search experience are implemented. Provider selection and other product features remain under evaluation or planned.

## The Problem

Finding a relevant research paper is only the beginning of the research process.

Researchers often need to:

- Discover relevant papers across a research topic.
- Understand a paper's contributions, methods, findings, and limitations.
- Follow references to earlier work and discover papers that cite a selected paper.
- Explore connections between related studies.
- Verify AI-generated explanations against actual source material.
- Compare papers to understand similarities, differences, and open questions.
- Keep papers, notes, and research questions organized in one place.

Research X aims to bring these activities into a connected research workflow.

## Product Vision

Build a research workspace that helps users move from a question to a deeper understanding of the literature, with traceable sources and clear distinctions between verified facts and AI-generated suggestions.

### Capabilities

- **Paper discovery:** An initial OpenAlex search experience returns normalized provider metadata without saving results. Provider selection, filters, and persistent canonical paper records remain open or planned.
- **Paper exploration:** Inspect paper details, authors, publication information, references, and citing papers.
- **Citation graph:** Navigate bibliographic relationships visually.
- **Evidence-grounded reading:** Ask questions about supported paper content and inspect the evidence behind answers.
- **Research workspace:** Save papers, organize collections, and maintain notes.
- **Paper comparison:** Compare research questions, methods, findings, and limitations.
- **Research exploration assistance:** Generate research directions and possible gaps as hypotheses to investigate, not guaranteed discoveries.

The remaining capabilities are planned; paper detail, graph, reader, workspace, and comparison workflows are not implemented yet.

## What Makes Research X Different?

A search interface, an AI summary, or a citation graph alone is not enough to establish meaningful differentiation.

Research X will prioritize the connections between these capabilities:

1. **Traceable explanations:** Help users inspect the source passages supporting AI-generated answers.
2. **Relationship transparency:** Distinguish verified citations from semantic similarity and AI-inferred relationships.
3. **Connected exploration:** Move between papers, references, evidence, comparisons, and notes without losing research context.
4. **Honest uncertainty:** Make missing evidence and incomplete metadata visible rather than inventing information.
5. **Persistent research context:** Keep research questions, saved papers, collections, and notes together.

The product's differentiation must be validated through competitor research, user feedback, and measurable evaluation.

## Initial Audience

The initial target users are university students and early-stage researchers, with an initial focus on computer science, artificial intelligence, and machine learning literature.

The product architecture should support future expansion to other academic disciplines without compromising source quality or research integrity.

## Core Principles

- Evidence before confidence.
- Source provenance for research information.
- Verified citations kept distinct from similarity and inference.
- No fabricated paper metadata, references, or evidence.
- Privacy for user-created research content.
- Respect for copyright, provider terms, and usage restrictions.
- Accessible alternatives to visual-only interactions.
- Small, tested, maintainable implementation steps.

## Planned Technology Stack

The following is the proposed initial stack. Provider and hosting choices remain subject to validation.

| Area | Proposed technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Styling | Tailwind CSS and design tokens |
| Backend | Python, FastAPI, Pydantic |
| Database access | SQLAlchemy |
| Database migrations | Alembic |
| Primary database | PostgreSQL |
| Citation graph visualization | Cytoscape.js |
| Backend testing | Pytest |
| Research metadata | Provider adapter; candidate provider to be validated |
| AI integration | Backend adapter for a selected model provider |
| Version control | Git and GitHub |

See `docs/ARCHITECTURE.md` and `docs/DECISIONS.md` for details and unresolved decisions.

## Repository Structure

```text
ResearchX/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   ├── core/
│   │   └── schemas/
│   ├── tests/
│   └── requirements.txt
├── docs/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── AGENTS.md
└── README.md
```

The backend currently contains API routes, settings, response schemas, and focused tests. The frontend contains the Vite app, typed API client, and landing page. Feature modules will be added as those features are implemented.

## Documentation Guide

| Document | Purpose |
|---|---|
| `AGENTS.md` | Instructions and guardrails for AI coding assistants |
| `docs/PRODUCT_SPEC.md` | Product vision, requirements, and acceptance criteria |
| `docs/FEATURE_PLAN.md` | Phases, dependencies, and feature delivery plan |
| `docs/ARCHITECTURE.md` | System design, modules, and proposed API structure |
| `docs/DATA_MODEL.md` | Core entities, relationships, constraints, and provenance |
| `docs/GRAPH_MODEL.md` | Citation semantics, graph structure, and exploration |
| `docs/API_SPEC.md` | Planned endpoints, schemas, validation, and errors |
| `docs/AI_AND_EVIDENCE.md` | Evidence-grounded AI behavior and evaluation |
| `docs/SECURITY_AND_PRIVACY.md` | Security controls and user-data protection |
| `docs/TESTING.md` | Testing strategy and quality gates |
| `docs/DEVELOPMENT_WORKFLOW.md` | Git, Codex, implementation, and review workflow |
| `docs/DEPLOYMENT_AND_OPERATIONS.md` | Deployment, configuration, monitoring, and recovery |
| `docs/DECISIONS.md` | Accepted and proposed decisions and open questions |

## Development Status

The project has an initial application foundation; product features are still in the planning and implementation queue.

- [x] Define the product scope and principles.
- [x] Establish a phased feature plan.
- [x] Document the proposed architecture and data model.
- [x] Define citation graph semantics.
- [x] Specify the planned API.
- [x] Document AI evidence requirements.
- [x] Define security, privacy, and testing principles.
- [x] Establish development and deployment workflows.
- [x] Record initial architecture decisions and unresolved questions.
- [ ] Review documentation for consistency.
- [ ] Validate external providers and important technical choices.
- [x] Establish local frontend and backend setup instructions.
- [x] Implement the initial application skeleton and health endpoint.
- [x] Implement stateless OpenAlex paper search and discovery UI.
- [ ] Build and test the MVP incrementally.

Checklist items describe planning progress and must be updated when implementation work is actually completed.

## Getting Started

### Backend

In PowerShell, from the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Set RESEARCH_X_DATABASE_URL for local PostgreSQL; optionally set RESEARCH_X_OPENALEX_API_KEY.
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Run a local PostgreSQL server separately before applying migrations. The example connection string contains a placeholder password; replace it only in the ignored `.env` file. The API is available at `http://localhost:8000`; its health endpoint is `http://localhost:8000/api/v1/health`.

### Frontend

In a separate terminal, from the repository root:

```powershell
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite (normally `http://localhost:5173`). The landing page checks backend health and includes paper search through Vite's development proxy.

### Configuration

The backend reads `RESEARCH_X_CORS_ALLOWED_ORIGINS`, `RESEARCH_X_DATABASE_URL`, `RESEARCH_X_OPENALEX_BASE_URL`, and the optional secret `RESEARCH_X_OPENALEX_API_KEY`; database access and migrations require a PostgreSQL URL, while low-volume OpenAlex search can run without a key. Vite reads `VITE_API_PROXY_TARGET` and `VITE_API_BASE_URL`. Example environment files contain placeholders only; keep real `.env` files out of Git. Review [OpenAlex authentication and rate limits](https://help.openalex.org/api/authentication/) and [search pricing](https://help.openalex.org/api/searching/) before operating at higher volume.

### Tests

From the repository root, after installing the backend dependencies:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest backend/tests -v
```

Database tests use isolated SQLite databases and do not read `.env` or require PostgreSQL credentials. The migration is also rendered using the PostgreSQL dialect in the test suite.

## Development Approach

Research X will be built incrementally. The current foundation includes a versioned FastAPI health endpoint, a React + TypeScript + Vite landing page, and a stateless OpenAlex paper search experience. Search results are not persisted; provider selection remains subject to evaluation.

Each feature should have clear acceptance criteria, focused implementation changes, appropriate automated tests, and updated documentation. Generated code must be reviewed rather than accepted solely because it compiles.

See `docs/DEVELOPMENT_WORKFLOW.md` for the detailed development process.

## Important Constraints

- Do not invent academic metadata or citation relationships.
- Do not represent AI-inferred connections as verified citations.
- Do not make AI claims without appropriate supporting evidence.
- Do not assume public availability means unrestricted reuse.
- Do not commit credentials or private user information.
- Do not describe planned features as implemented.

## Long-Term Goal

Help researchers spend less time struggling with disconnected research tools and more time understanding the literature, tracing evidence, connecting ideas, and developing informed research questions.
