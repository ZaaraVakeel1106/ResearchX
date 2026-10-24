# Research X — Feature and Development Plan

**Status:** Initial planning
**Version:** 0.1
**Source of truth:** `docs/PRODUCT_SPEC.md`

---

## 1. Purpose

This document defines the implementation order for Research X.

Development will proceed in small, testable stages. Each stage must have clear acceptance criteria and must respect the product requirements, architecture, security rules, and data-integrity requirements.

A feature is not complete merely because its interface exists. Its intended behavior must work, relevant failure cases must be handled, and applicable tests must pass.

## 2. Priority Definitions

- **P0 — Foundation:** Required before meaningful feature development.
- **P1 — Core MVP:** Essential capabilities required for the initial usable product.
- **P2 — Enhanced MVP:** Improves research workflows after the core experience works.
- **P3 — Future:** Advanced functionality that should wait until the fundamentals are reliable.

## 3. Development Phases

### Phase 0 — Repository and Project Foundation

**Priority:** P0

Tasks:

- [x] Create the GitHub repository.
- [x] Clone the repository locally.
- [x] Create the `docs/` directory.
- [x] Create `docs/PRODUCT_SPEC.md`.
- [x] Create root `AGENTS.md`.
- [ ] Create the complete documentation set.
- [ ] Finalize the initial technology stack and architecture.
- [x] Establish `.gitignore` and `.env.example`.
- [x] Establish frontend and backend package configuration.
- [ ] Add formatting, linting, and continuous integration.
- [x] Add focused backend automated tests.
- [ ] Add continuous integration.
- [ ] Verify the project can be set up from a clean checkout.

**Acceptance criteria**

- The repository has a documented and understandable structure.
- A new developer can follow the setup instructions.
- Secrets and generated files are excluded from version control.
- Automated checks run reproducibly.
- No product feature is marked complete without verification.

### Phase 1 — Application Skeleton

**Priority:** P0

Tasks:

- [x] Create the frontend application.
- [x] Create the backend application.
- [x] Establish the API versioning convention.
- [x] Add a health-check endpoint.
- [x] Add centralized environment configuration for local CORS origins.
- [ ] Add centralized error handling.
- [x] Add database connection configuration and initial migrations.
- [x] Establish typed health response and frontend service conventions.
- [x] Create the initial landing page and navigation shell.
- [ ] Add loading, empty, and error-state components.

**Acceptance criteria**

- Frontend and backend start using documented commands.
- The frontend can communicate with the backend.
- Health checks return the documented response.
- Configuration errors are actionable.
- Automated checks run without requiring paid external services.

### Phase 2 — Academic Paper Search

**Priority:** P1

Tasks:

- [ ] Select and document an academic metadata provider.
- [ ] Implement a backend integration adapter.
- [ ] Normalize provider responses into Research X schemas.
- [ ] Implement search and pagination.
- [ ] Add relevant filters where supported.
- [ ] Build the search-results interface.
- [ ] Implement paper identification and deduplication.
- [ ] Handle missing metadata, rate limits, and provider failures.

**Acceptance criteria**

- A real search returns traceable academic records.
- Each result displays available metadata correctly.
- Pagination does not silently duplicate results.
- Missing fields do not break the interface.
- Provider errors are communicated honestly.
- Automated tests cover successful responses and failures.

### Phase 3 — Paper Details

**Priority:** P1

Tasks:

- [ ] Implement paper-detail retrieval.
- [ ] Display available title, authors, abstract, publication information, and identifiers.
- [ ] Display original source links.
- [ ] Show reference and citation information when available.
- [ ] Indicate full-text availability where reliably known.
- [ ] Add navigation between search results and paper details.

**Acceptance criteria**

- Selecting a search result opens the correct paper.
- Stable identifiers are used where available.
- Incomplete metadata is handled gracefully.
- Source links are preserved.
- Unsupported or unavailable information is not invented.

### Phase 4 — Citation Graph

**Priority:** P1

Tasks:

- [ ] Document the graph data model and relationship provenance.
- [ ] Implement reference retrieval.
- [ ] Implement citing-paper retrieval.
- [ ] Build the interactive graph visualization.
- [ ] Support selecting and expanding nodes.
- [ ] Connect graph nodes to paper-detail pages.
- [ ] Add graph depth, node-count, and request limits.
- [ ] Distinguish citation links from similarity and inferred links.

**Acceptance criteria**

- Graph nodes correspond to identifiable publications.
- Verified citation edges come from traceable bibliographic relationships.
- Edge types are visually and semantically distinguishable.
- Expansion is bounded and handles failures.
- Selecting a node preserves the user's exploration context.
- Tests cover duplicate nodes, incomplete metadata, and unavailable relationships.

### Phase 5 — Evidence-Grounded AI Reader

**Priority:** P1

Tasks:

- [ ] Select and document the AI provider and model.
- [ ] Define permitted full-text acquisition methods.
- [ ] Implement accessible-document ingestion.
- [ ] Implement text extraction and chunking.
- [ ] Implement retrieval over processed source passages.
- [ ] Generate answers grounded in retrieved evidence.
- [ ] Return passage references and source locations when available.
- [ ] Implement insufficient-evidence behavior.
- [ ] Track provider errors, latency, and usage.
- [ ] Evaluate answer quality and citation correctness.

**Acceptance criteria**

- Answers use only content actually available to the system.
- Supporting passages can be inspected by the user.
- Unsupported questions trigger an honest limitation response.
- Abstract-only access is clearly disclosed.
- Missing API credentials produce an actionable error.
- Tests use mocked AI responses.
- Evaluation includes unsupported questions and misleading-source cases.

### Phase 6 — Research Workspace

**Priority:** P1

Tasks:

- [ ] Define the workspace and saved-paper data model.
- [ ] Decide whether authentication is required for the initial release.
- [ ] Implement collections or research projects.
- [ ] Implement saving and removing papers.
- [ ] Implement notes and reading status.
- [ ] Associate saved papers with research questions.
- [ ] - [ ] Implement and test backend ownership and authorization checks for every private workspace, collection, saved-paper operation, and note operation.

**Acceptance criteria**

- Users can organize and revisit saved research.
- Saved papers resolve to the correct publications.
- Notes persist as expected.
- User-owned data cannot be accessed by unauthorized users.
- Deletion and error behavior are documented.

### Phase 7 — Paper Comparison

**Priority:** P2

Tasks:

- [ ] Allow users to select papers for comparison.
- [ ] Define a common comparison schema.
- [ ] Extract problem, method, dataset, findings, and limitations where available.
- [ ] Attach supporting evidence to factual comparison fields.
- [ ] Show unknown or unreported information explicitly.
- [ ] Build a comparison table or equivalent structured interface.

**Acceptance criteria**

- Multiple selected papers can be compared in a consistent format.
- Facts are distinguishable from interpretation.
- Unsupported fields remain unknown rather than guessed.
- Evidence can be traced back to its source.
- Partial or inaccessible papers are handled honestly.

### Phase 8 — Research Exploration Intelligence

**Priority:** P3

Tasks:

- [ ] Improve ranking and recommendation quality.
- [ ] Explore semantic similarity between papers.
- [ ] Support multi-hop citation exploration.
- [ ] Identify recurring methods, datasets, and concepts.
- [ ] Suggest follow-up reading.
- [ ] Generate candidate research questions.
- [ ] Evaluate potential research-gap suggestions.

**Acceptance criteria**

- Recommendations have an understandable basis.
- Similarity links are not confused with citations.
- Candidate gaps are labeled as hypotheses.
- Evaluation demonstrates usefulness beyond a simple baseline.
- No claim of research novelty is made without adequate evidence.

### Phase 9 — Release Readiness

**Priority:** P0 before public release

Tasks:

- [ ] Run unit and integration tests.
- [ ] Run frontend build and type checks.
- [ ] Add end-to-end tests for core journeys.
- [ ] Review authentication, authorization, input validation, and upload security.
- [ ] Check rate limits and cost controls.
- [ ] Verify error handling and observability.
- [ ] Review accessibility and responsive behavior.
- [ ] Document environment variables and deployment.
- [ ] Verify migrations and database recovery procedures.
- [ ] Publish known limitations and supported data sources.

**Acceptance criteria**

- Core user journeys pass their release tests.
- Critical security issues are resolved.
- Deployment is reproducible.
- External provider failures do not cause misleading results.
- Setup and troubleshooting documentation is complete.
- Known limitations are disclosed.

## 4. Dependency Order

The main dependency chain is:

1. Repository and documentation foundation.
2. Application skeleton and configuration.
3. Academic metadata integration.
4. Search and paper details.
5. Citation graph.
6. Evidence-grounded reader.
7. Research workspace.
8. Paper comparison.
9. Advanced research intelligence.
10. Release readiness.

Some work can proceed in parallel after interfaces and schemas are agreed upon. Parallel implementation should not create competing definitions of the same data model or API.

## 5. Feature Implementation Rules

For each feature:

1. Read the applicable specifications.
2. Inspect the current code and Git status.
3. Confirm requirements and acceptance criteria.
4. Identify API, schema, and database changes.
5. Implement the smallest complete vertical slice.
6. Add automated tests.
7. Run relevant checks.
8. Review the diff.
9. Update documentation and task status.
10. Report what was implemented, tested, and left unresolved.

Do not mark a feature complete solely because its code has been written.

## 6. Tracking Conventions

Use these statuses in future task tracking:

- `Not started`
- `In progress`
- `Blocked`
- `Implemented — tests pending`
- `Verified`
- `Deferred`

A task should be marked `Verified` only when its acceptance criteria have been checked.

## 7. Current Project Status

Completed:

- GitHub repository created.
- Repository cloned locally.
- Initial product specification created.
- Root agent instructions created.
- Feature plan created.
- FastAPI and React/Vite application foundations created.
- Versioned health endpoint and frontend health connection implemented.
- Focused backend health and configuration tests added.

Not yet verified:

- Architecture beyond the initial application skeleton.
- Technology choices beyond the React/Vite frontend and FastAPI backend foundation.
- External provider selection.
- PostgreSQL integration testing against an isolated live server.
- Continuous integration and broader automated checks.
- End-to-end feature behavior.

These remain planned work, not completed functionality.

---

**End of Feature and Development Plan**
