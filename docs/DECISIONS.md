# Architecture Decision Records — Research X

## 1. Purpose

This document records important product, architecture, data, and engineering decisions for Research X.

Its purpose is to:

- Keep implementation consistent across features and contributors.
- Explain why important choices were made.
- Prevent repeated debates about settled decisions.
- Make assumptions and unresolved questions visible.
- Help AI coding assistants follow the intended architecture.

This document is a living record. Update it when a significant decision changes.

## 2. Decision Status

Use these statuses:

- **Proposed:** A candidate approach that still needs validation or approval.
- **Accepted:** The approach has been approved for implementation.
- **Implemented:** The accepted approach has been implemented and verified.
- **Superseded:** A newer decision replaces this one.
- **Rejected:** The approach was considered and deliberately not selected.

Do not mark a decision as implemented simply because it appears in this document.

## 3. Decision Record Format

For significant decisions, record:

- **ID:** A stable identifier, such as ADR-001.
- **Title:** A short description.
- **Status:** One of the statuses above.
- **Context:** The problem or constraint.
- **Decision:** The chosen approach.
- **Alternatives:** Important alternatives considered.
- **Consequences:** Benefits, trade-offs, and limitations.
- **Related documents:** Documents that must remain consistent with the decision.

## 4. Initial Decisions

The entries below capture the current proposed direction. They are not proof that the stack, providers, or hosting arrangements have already been finalized.

### ADR-001: Build a Research Exploration Platform

**Status:** Accepted

**Context**

A conventional search experience helps users locate papers, but research often requires understanding relationships, tracing references, comparing findings, and checking evidence.

**Decision**

Research X will combine paper discovery, citation navigation, source-grounded reading assistance, and persistent research organization in one workflow.

**Consequences**

- Features must support a connected research workflow rather than exist as unrelated tools.
- Source provenance and evidence traceability are core requirements.
- Differentiation must be validated through user research and product evaluation rather than assumed.

**Related documents:** `PRODUCT_SPEC.md`, `FEATURE_PLAN.md`

### ADR-002: Use a Modular Monolith for the Initial Backend

**Status:** Proposed

**Context**

The MVP needs a maintainable backend without the operational overhead of distributed services.

**Decision**

Start with one FastAPI backend organized into clear modules for API routes, schemas, services, repositories, integrations, and graph logic.

**Alternatives considered**

- Microservices from the beginning.
- A backend with little or no separation between business logic and route handlers.

**Consequences**

- Simpler local development and deployment.
- Clear internal boundaries without distributed-system complexity.
- Modules must remain appropriately separated as the application grows.


**Related documents:** `ARCHITECTURE.md`, `DEVELOPMENT_WORKFLOW.md`

### ADR-003: Use React, TypeScript, and Vite for the Frontend

**Status:** Proposed

**Context**

Research X needs an interactive interface for search, paper reading, graph exploration, and workspace management.

**Decision**

Use React, TypeScript, and Vite as the proposed frontend foundation.

**Alternatives considered**

Other frontend frameworks and application architectures.

**Consequences**

- Shared TypeScript types and explicit API contracts are important.
- Interactive graph and reader experiences need dedicated feature modules.
- The final dependency and tooling choices must be verified during repository setup.

**Related documents:** `ARCHITECTURE.md`, `API_SPEC.md`

### ADR-004: Use FastAPI, Pydantic, and SQLAlchemy

**Status:** Proposed

**Context**

The backend requires typed API contracts, validation, database access, and a clear integration layer.

**Decision**

Use Python with FastAPI, Pydantic, and SQLAlchemy, with Alembic for schema migrations.

**Consequences**

- Request and response schemas must remain consistent with the API specification.
- Database changes must be managed through migrations.
- Integration boundaries must validate external provider responses.

**Related documents:** `ARCHITECTURE.md`, `DATA_MODEL.md`, `API_SPEC.md`

### ADR-005: Use PostgreSQL as the Primary Database

**Status:** Proposed

**Context**

The platform needs persistent academic metadata, citation relationships, user workspaces, notes, and provenance records.

**Decision**

Use PostgreSQL as the proposed primary database.

**Consequences**

- Database constraints should enforce important integrity rules.
- Migrations must preserve existing data unless a destructive change is explicitly approved.
- Search and graph performance must be measured before introducing specialized infrastructure.
- The hosting provider remains undecided.

**Related documents:** `ARCHITECTURE.md`, `DATA_MODEL.md`, `DEPLOYMENT_AND_OPERATIONS.md`

### ADR-006: Introduce Research Providers Through Adapters

**Status:** Accepted

**Context**

Research data providers may differ in identifiers, metadata completeness, reference coverage, rate limits, licensing, and response formats.

**Decision**

Integrate providers behind backend adapters that normalize their responses into internal schemas.

OpenAlex is an initial candidate, not a permanently finalized dependency. Its capabilities, current terms, and suitability must be verified before implementation.

**Consequences**

- Provider-specific response formats must not leak throughout the application.
- Provenance should be retained.
- Provider failure must remain distinguishable from a valid empty result.
- The architecture should allow another provider to be added without rewriting unrelated product features.
- Evaluate providers using actual coverage of computer science and AI/ML papers, reference and citation availability, metadata quality, and identifier coverage.
- Verify current API documentation, usage limits, licensing terms, attribution requirements, and caching or retention restrictions before implementation.
- Keep provider-specific identifiers and provenance so records can be traced back to their sources.
- Treat provider selection as a measured engineering decision; do not assume that one provider offers complete coverage of all scholarly literature.

**Related documents:** `ARCHITECTURE.md`, `DATA_MODEL.md`, `API_SPEC.md`

### ADR-007: Distinguish Citation Edges from Similarity and Inference

**Status:** Accepted

**Context**

Researchers need to know whether a relationship is supported by a bibliographic citation, computed similarity, or an AI-generated hypothesis.

**Decision**

Represent and display these relationship types distinctly:

- **CITES:** A verified bibliographic citation relationship.
- **SIMILAR_TO:** A similarity relationship supported by a defined similarity method.
- **INFERRED_RELATED_TO:** A proposed relationship inferred by a model or algorithm.

Do not display similarity or inference as if it were a verified citation.

**Consequences**

- Every relationship type needs defined provenance and semantics.
- Graph queries and UI labels must preserve the distinction.
- Tests must verify direction, type, and evidence where applicable.
- Record the source and verification status of imported citation relationships wherever the available data supports it.
- Distinguish confirmed citation relationships from missing, unavailable, or incomplete reference data.
- Do not invent citation edges from title similarity, AI-generated suggestions, or incomplete metadata; represent such relationships using their appropriate non-citation types.

**Related documents:** `GRAPH_MODEL.md`, `DATA_MODEL.md`, `PRODUCT_SPEC.md`

### ADR-008: Ground AI Answers in Retrieved Evidence

**Status:** Accepted

**Context**

AI-generated research explanations can be misleading when they make unsupported claims or attach irrelevant citations.

**Decision**

Use a retrieval-grounded workflow in which answers are based on relevant source passages. Preserve links between answer claims, evidence passages, and source papers where the implementation supports claim-level attribution.

When evidence is inadequate, the system must communicate that limitation instead of inventing support.

**Consequences**

- Retrieval quality and answer quality must be evaluated separately.
- Evidence references must resolve to real stored or retrievable source material.
- Paper text must be treated as untrusted input.
- Research-gap suggestions must be presented as hypotheses requiring verification.
- AI output must not be treated as automatically correct.
- If only an abstract or partial text is available, the reader and AI must clearly disclose the limits of the available content.
- Store only source text that the platform is permitted to retain; otherwise, preserve permitted metadata, source links, and evidence locators where available.
- Every displayed evidence reference must identify the source and available location precisely enough for the user to verify it; do not fabricate page numbers, quotations, or source locations.

**Related documents:** `AI_AND_EVIDENCE.md`, `DATA_MODEL.md`, `TESTING.md`

### ADR-009: Preserve Research Metadata Provenance

**Status:** Accepted

**Context**

Different sources may report conflicting or incomplete paper metadata. Researchers need to understand where information came from.

**Decision**

Preserve source identifiers and relevant provenance for imported metadata. Avoid silently inventing missing fields or merging distinct papers.

The precise reconciliation and conflict-resolution algorithm remains to be defined.

**Consequences**

- Normalization and deduplication need explicit rules and tests.
- Important metadata conflicts should remain inspectable.
- External identifiers must be validated.
- Missing data must not be confused with confirmed absence.
- Maintain an internal canonical paper ID that is independent of any single external provider's identifier.
- Normalize and validate external identifiers such as DOIs before matching records.
- Do not merge records solely because their titles are similar; use corroborating metadata and a defined matching rule.
- When identity remains uncertain, preserve separate records and flag the potential duplicate for review rather than silently merging them.
- Record the source and retrieval time of imported metadata so its freshness can be assessed.
- Define explicit refresh and cache-expiration policies before implementing recurring metadata updates.
- When providers disagree, preserve enough source information to investigate the conflict instead of silently treating one value as universally correct.

**Related documents:** `DATA_MODEL.md`, `API_SPEC.md`, `TESTING.md`

### ADR-010: Use a Citation-First Graph Model

**Status:** Accepted

**Context**

The graph is intended to help researchers navigate the scholarly record and discover related work.

**Decision**

Build the graph around verifiable citation and reference relationships first. Add similarity and inferred relationships as explicitly labeled extensions.

Bound graph queries to avoid unmanageable response sizes and provide alternative list-based navigation.

**Consequences**

- Citation direction must be consistent throughout the system.
- Missing reference data must not be interpreted as proof of no relationship.
- Graph exploration requires pagination, depth limits, or equivalent bounds.
- Accessibility must not depend exclusively on the visual graph.

**Related documents:** `GRAPH_MODEL.md`, `ARCHITECTURE.md`, `TESTING.md`

### ADR-011: Treat User Research Data as Private by Default

**Status:** Accepted

**Context**

Workspaces may contain notes, saved papers, research questions, and personal interpretations.

**Decision**

Treat user-created workspace content as private by default. Enforce ownership and authorization in the backend, not solely in the frontend.

Define retention and deletion behavior before collecting substantial personal data.

**Consequences**

- Workspace access requires explicit authorization checks.
- Tests must cover cross-user access attempts.
- Logs and external AI requests must not expose private information unnecessarily.
- Authentication details and hosting-specific session design remain to be finalized.
- Every private workspace, saved paper collection, and note must be associated with an authenticated owner.
- The backend must verify ownership or explicit authorization on every operation that accesses or modifies private resources.
- API responses must not expose another user's private data, even when resource identifiers are guessed or obtained elsewhere.
- Authentication, session management, account recovery, and account deletion must be designed before private user data is exposed in a deployed application.

**Related documents:** `SECURITY_AND_PRIVACY.md`, `DATA_MODEL.md`, `API_SPEC.md`

### ADR-012: Test External Integrations Independently

**Status:** Accepted

**Context**

Research providers and AI services can be slow, rate-limited, unavailable, or inconsistent.

**Decision**

Use mocked provider and model responses for ordinary automated tests. Keep optional live smoke tests separate.

**Consequences**

- Standard tests should not require paid API calls or personal credentials.
- Provider failure cases must be covered.
- Live integration behavior still requires occasional verification against current provider contracts and terms.

**Related documents:** `TESTING.md`, `ARCHITECTURE.md`, `DEVELOPMENT_WORKFLOW.md`

### ADR-013: Start with a Simple Deployment Architecture

**Status:** Proposed

**Context**

The MVP needs to be deployable and affordable without unnecessary infrastructure.

**Decision**

Prefer a static frontend, one backend application, and PostgreSQL. Select hosting and operational services after validating costs, requirements, and deployment compatibility.

**Consequences**

- Avoid introducing microservices or specialized graph infrastructure without evidence of need.
- Document environment variables, migrations, backups, and recovery.
- Production deployment and operational policies must be finalized before launch.

**Related documents:** `ARCHITECTURE.md`, `DEPLOYMENT_AND_OPERATIONS.md`

## 5. Open Decisions Register

The following questions require further research or explicit decisions.

| ID | Decision needed | Why it matters | Status |
|---|---|---|---|
| OPEN-001 | Confirm research metadata provider | Determines coverage, identifiers, terms, and limits | Open |
| OPEN-002 | Determine full-text access strategy | Affects copyright, evidence retrieval, and user experience | Open |
| OPEN-003 | Select AI model provider | Affects quality, cost, latency, and privacy | Open |
| OPEN-004 | Define authentication approach | Required for private workspaces and notes | Open |
| OPEN-005 | Finalize paper identity and deduplication rules | Prevents incorrect merges and duplicate records | Open |
| OPEN-006 | Define evidence passage storage and retention | Affects provenance, privacy, and storage requirements | Open |
| OPEN-007 | Select hosting and managed PostgreSQL providers | Determines deployment and operating costs | Open |
| OPEN-008 | Finalize frontend and end-to-end test tooling | Determines repeatable quality checks | Open |
| OPEN-009 | Define metadata refresh and cache policies | Affects freshness, provider load, and licensing compliance | Open |
| OPEN-010 | Define AI evaluation criteria and acceptance thresholds | Required to measure evidence-grounded answer quality | Open |
| OPEN-011 | Define account deletion and workspace retention behavior | Required for privacy and data lifecycle management | Open |
| OPEN-012 | Validate product differentiation with target users | Determines which features deserve priority | Open |

### Recommended Direction: Full-Text Access

**Status:** Proposed — requires validation before implementation.

Research X should support different levels of paper access:

- **Full text available:** Enable reading and evidence-grounded question answering only when the content can lawfully be accessed and processed.
- **Abstract only:** Allow discovery, metadata exploration, and abstract-based explanations. Clearly disclose that the full paper was not available.
- **Restricted or unavailable:** Provide available metadata and a link to the publisher or authorized source. Do not imply that Research X has inspected the full paper.
- **User-provided documents:** Support document-based reading only after defining file validation, privacy, retention, and copyright requirements.

The platform must distinguish content availability from permission to retrieve, process, or retain that content. Provider capabilities, licensing terms, and retention rules must be verified before implementation.

**Related documents:** `PRODUCT_SPEC.md`, `AI_AND_EVIDENCE.md`, `SECURITY_AND_PRIVACY.md`, `DEPLOYMENT_AND_OPERATIONS.md`.

### Recommended Direction: Evidence Storage and Retention

**Status:** Proposed — requires validation before implementation.

Research X should preserve enough information to make AI-generated explanations verifiable without assuming that all source text can be stored indefinitely.

- **Source identity:** Record the source paper's canonical ID and relevant external identifiers.
- **Evidence location:** Store a source locator, such as a page number, section, paragraph, or provider-specific location, when available.
- **Passage storage:** Store extracted text only when the applicable access rights and provider terms permit it.
- **Evidence provenance:** Record where the passage originated and the retrieval or extraction method used to obtain it.
- **Retention:** Define retention, deletion, and cache-expiration rules before storing substantial source text or private user documents.
- **Unavailable evidence:** If a passage cannot be retrieved or verified, disclose that limitation rather than fabricating a quotation or source location.

Evidence records must remain distinguishable from AI-generated summaries, interpretations, and hypotheses.

**Related documents:** `AI_AND_EVIDENCE.md`, `DATA_MODEL.md`, `SECURITY_AND_PRIVACY.md`, `DEPLOYMENT_AND_OPERATIONS.md`.

### Recommended Direction: AI Provider Integration

**Status:** Proposed — provider selection requires evaluation.

Research X should integrate AI models through a backend provider adapter rather than coupling core product logic to a single model vendor.

The initial implementation should:

- Use a configurable model provider so the implementation can change without rewriting the reader, evidence retrieval, or workspace modules.
- Send only the source content and user information necessary for the requested task.
- Require evidence-grounded answers when answering questions about research papers.
- Preserve source references and evidence locators independently of the model's generated response.
- Handle provider timeouts, rate limits, unavailable services, and malformed responses gracefully.
- Evaluate answer quality, evidence attribution, latency, and cost before choosing the production model.

**Provider selection criteria:** Evidence-grounding reliability, context capacity, cost, latency, data-handling terms, availability, and ease of integration.

**Related documents:** `ARCHITECTURE.md`, `AI_AND_EVIDENCE.md`, `SECURITY_AND_PRIVACY.md`, `TESTING.md`.

### Recommended Direction: AI Evaluation

**Status:** Proposed — metrics and acceptance thresholds require validation.

Research X should evaluate AI-powered research features against a documented test set containing representative papers, questions, retrieved evidence, and expected answer characteristics.

Evaluation should cover:

- **Evidence support:** Whether factual claims are supported by the retrieved source material.
- **Citation accuracy:** Whether cited sources and evidence locations actually support the associated claims.
- **Retrieval quality:** Whether the system retrieves relevant passages when suitable evidence is available.
- **Uncertainty handling:** Whether the system acknowledges missing, conflicting, or insufficient evidence.
- **Faithfulness:** Whether summaries and explanations preserve the source's meaning without introducing unsupported conclusions.
- **Robustness:** Whether the system handles unavailable full text, malformed provider responses, and adversarial instructions embedded in documents.
- **Operational performance:** Response latency, provider failures, and estimated cost per task.

Define measurable acceptance thresholds before treating an AI feature as production-ready. Do not claim that an AI answer is reliable solely because it is fluent or passes a small number of demonstrations.

**Related documents:** `AI_AND_EVIDENCE.md`, `TESTING.md`, `PRODUCT_SPEC.md`.

## 6. How to Add or Change a Decision

When a significant choice arises:

1. Identify the problem and constraints.
2. Inspect existing decisions and relevant documentation.
3. Compare reasonable alternatives.
4. Record the chosen approach and its trade-offs.
5. Update related documents.
6. Obtain approval when the choice affects product scope, security, data integrity, cost, or external commitments.
7. Mark replaced decisions as superseded rather than silently deleting their history.

Minor implementation details do not need separate decision records unless they create meaningful long-term consequences.

## 7. Consistency Rule

If an implementation task conflicts with an accepted decision, stop and resolve the conflict before proceeding.

A decision may be changed when new evidence justifies doing so, but related architecture, data model, API, security, and testing documentation must be updated together.

Documentation describes intended behavior; actual implementation and test results must be inspected before claiming a decision has been implemented.