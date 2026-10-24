# Testing Strategy — Research X

## 1. Purpose

This document defines how Research X will be tested to ensure that its search results, paper metadata, citation graph, AI-generated answers, workspace features, security controls, and user interface behave correctly.

Testing must verify not only that features work, but also that research information is accurate, traceable, and presented honestly.

## 2. Testing Principles

- Test observable behavior, not implementation details alone.
- Test important success paths, failure paths, and edge cases.
- Never treat plausible-looking output as proof of correctness.
- Verify paper identifiers, authors, publication details, references, and evidence provenance.
- Ensure that AI answers are supported by retrieved evidence or explicitly report insufficient evidence.
- Keep tests deterministic wherever possible.
- Mock external research providers and AI services in unit tests.
- Never require real API keys or paid services for the standard local test suite.
- Avoid tests that depend on live external data or unstable network conditions.
- Add regression tests for bugs that have been fixed.
- Do not weaken a meaningful test simply to make the suite pass.

## 3. Testing Levels

### 3.1 Unit Tests

Test individual functions and modules in isolation.

Examples:

- Paper metadata normalization.
- External identifier validation.
- Paper deduplication.
- Citation direction and graph construction.
- Search parameter validation.
- Evidence selection and source attribution.
- AI response validation.
- Workspace ownership checks.
- API error formatting.

Unit tests should be fast, independent, and deterministic.

### 3.2 Integration Tests

Test interactions between components.

Examples:

- FastAPI endpoints interacting with repositories and services.
- SQLAlchemy models and database constraints.
- Database migrations creating the expected schema.
- Research provider adapters converting external responses into internal schemas.
- Citation and reference records being stored and retrieved correctly.
- AI answer generation using mocked retrieval and model responses.
- Workspace operations enforcing ownership and access rules.

Use an isolated test database. Prefer PostgreSQL for tests involving PostgreSQL-specific behavior or constraints. The current model and migration tests use isolated SQLite databases with foreign-key enforcement, and the migration is separately rendered using PostgreSQL SQL. They require no PostgreSQL server or production credentials. Add an isolated PostgreSQL test job before relying on PostgreSQL-only behavior. Never run integration tests against production data.

### 3.3 API Tests

Verify HTTP behavior, schemas, validation, and error handling.

Check:

- Correct status codes.
- Request parameter validation.
- Response schema consistency.
- Pagination and result limits.
- Missing or malformed identifiers.
- Provider timeouts and failures.
- Database failures.
- Authentication and authorization where implemented.
- Consistent error response structure.
- Absence of internal secrets and stack traces in client-facing errors.

### 3.4 Frontend Tests

Test important user-facing behavior.

Examples:

- Search forms and result lists.
- Loading, empty, error, and retry states.
- Paper detail views.
- Citation graph interactions.
- Reader evidence links.
- Workspace creation and paper saving.
- Notes and collections.
- Paper comparison.
- Keyboard navigation and accessible labels.

Tests should focus on user-visible behavior rather than fragile implementation details.

### 3.5 End-to-End Tests

Test critical workflows across the frontend and backend.

Initial end-to-end workflows:

1. Open Research X and load the application.
2. Search for a research topic.
3. Open a paper's detail page.
4. Navigate from a paper to its references and citing papers.
5. Open a citation graph and inspect a connected paper.
6. Ask a question about a supported paper and inspect its evidence.
7. Create or open a workspace and save a paper.
8. Add a note to a saved paper.
9. Compare two papers.

Use controlled fixtures or mocked external services where appropriate. End-to-end tests must not depend on a particular live provider response remaining unchanged.

## 4. Research Data Correctness

Research X must test the integrity of academic metadata and relationships.

### Paper Metadata

Verify that:

- Titles and author lists are normalized correctly.
- Publication dates are not fabricated when unavailable.
- Missing values remain explicitly missing rather than being invented.
- DOI and other external identifiers are validated and normalized.
- Duplicate provider records can be reconciled without silently merging distinct papers.
- Conflicting metadata can retain source provenance.
- Provider-specific fields are mapped consistently to internal schemas.

### Citation and Reference Relationships

Verify that:

- A citation edge has the correct direction.
- If paper A cites paper B, the stored relationship represents A → B.
- References and citing papers are not accidentally reversed.
- Duplicate edges are handled according to the data model.
- Missing references are not interpreted as proof that no references exist.
- Semantic similarity is not presented as a verified citation.
- AI-inferred relationships are clearly distinguished from verified relationships.

### Search

Verify that:

- Empty queries and invalid parameters are handled correctly.
- Result limits and pagination work as specified.
- Sorting is deterministic when the same input and dataset are used.
- Provider errors do not produce fabricated search results.
- Empty results are distinct from provider failures.
- Search results preserve the provenance needed for later inspection.

## 5. AI and Evidence Tests

AI features require additional safeguards because fluent answers can still be incorrect.

Test the following:

- Answers are grounded in the retrieved passages provided to the model.
- Evidence references resolve to the correct paper and passage.
- A claim is not attributed to a passage that does not support it.
- The system reports insufficient evidence when retrieval is inadequate.
- Missing full text is not represented as successfully analyzed full text.
- Summaries preserve important qualifications and limitations.
- Paper comparisons distinguish what each paper actually reports.
- Research-gap suggestions are labeled as hypotheses requiring verification.
- Model output that violates the expected schema is rejected or safely handled.
- Prompt injection contained in paper text is treated as untrusted content.
- Model failures and timeouts produce safe, understandable errors.
- Sensitive user information is not unintentionally included in prompts or logs.

Use a small, version-controlled evaluation dataset with known source passages, expected evidence references, and representative questions.

Evaluate answer correctness, evidence support, citation accuracy, appropriate uncertainty, and failure handling separately. A fluent answer alone must never count as a successful test.

## 6. Security and Privacy Tests

Verify that:

- A user cannot access another user's private workspace, notes, or collections.
- Missing or invalid credentials are rejected when authentication is required.
- Input validation rejects malformed or excessively large requests.
- Secrets do not appear in API responses or application logs.
- Database queries enforce appropriate ownership boundaries.
- File processing, if introduced, rejects unsupported or unsafe uploads.
- External provider errors do not expose internal implementation details.
- Rate limits and resource limits work where implemented.
- Deletion and retention behavior matches the documented policy.

Security tests must use isolated test accounts and data.

## 7. Accessibility and Usability Checks

For major screens, verify:

- Keyboard navigation works.
- Interactive controls have accessible names.
- Focus states are visible.
- Text and controls have adequate contrast.
- Loading and error states are understandable.
- Graph information has a non-visual alternative, such as an accessible list of connected papers.
- Important actions do not depend exclusively on color or hover.
- Layouts remain usable on supported screen sizes.

Automated accessibility checks should be supplemented with manual review.

## 8. Test Data and Fixtures

Create reusable fixtures for:

- Papers with complete metadata.
- Papers with missing metadata.
- Duplicate records from different providers.
- Papers with references and citing relationships.
- Disconnected citation graphs.
- Conflicting metadata snapshots.
- Evidence passages with source locations.
- AI answers with valid and invalid evidence references.
- Workspaces belonging to different users.
- Provider timeouts, rate limits, and malformed responses.

Use synthetic or appropriately licensed data in tests. Do not commit private user information, real credentials, or restricted full-text documents.

Fixtures should be small, understandable, and stable.

## 9. External Service Testing

External research providers and AI services must be accessed through adapters.

Tests should mock adapter responses to cover:

- Successful responses.
- Empty results.
- Malformed data.
- Rate limiting.
- Authentication failures.
- Network timeouts.
- Temporary service outages.
- Unexpected response formats.

A separate optional smoke test may contact a real provider when explicitly configured. It must not be required for normal development or continuous integration.

## 10. Running Tests

The commands below reflect the current backend and frontend configuration. Frontend and end-to-end test tooling remains open in `DECISIONS.md`.

### Backend

From the repository root, after the backend environment and dependencies are configured:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest backend/tests -v
```

Run a specific test file:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_health.py -v
```

### Frontend

From the frontend directory, check TypeScript and create a production build:

```powershell
npm run build
```

This is a build check, not a frontend test suite. Select a frontend test runner before adding behavior that requires component-level automated tests.

### End-to-End

Run the configured end-to-end test command after the application and test environment are available. The exact command will be documented once the tool and configuration are selected.

Do not assume a command works merely because it is listed here. Verify it against the actual project configuration.

## 11. Continuous Integration

The continuous integration workflow should progressively include:

1. Backend formatting and linting.
2. Backend unit tests.
3. Backend integration tests using an isolated database service.
4. Frontend linting and type checking.
5. Frontend unit and component tests.
6. Build verification.
7. Selected end-to-end tests.
8. Dependency and security checks where practical.

Pull requests should pass required checks before merging. External API keys must not be required for the standard workflow.

Keep CI failures actionable and avoid unnecessary duplication between local and CI commands.

## 12. Regression Testing

When fixing a defect:

1. Reproduce the defect where practical.
2. Add a test that demonstrates the incorrect behavior.
3. Implement the fix.
4. Run the focused test.
5. Run the relevant broader test suite.
6. Record any remaining limitations.

A regression test should fail for the original bug and pass after the fix.

## 13. MVP Quality Gates

Before a feature is considered complete:

- Its acceptance criteria in `FEATURE_PLAN.md` are met.
- Relevant unit and integration tests pass.
- Request and response schemas match `API_SPEC.md`.
- Data handling matches `DATA_MODEL.md`.
- Security and privacy requirements are respected.
- Loading, empty, and failure states are handled.
- User-facing research claims remain traceable to sources.
- Documentation is updated when behavior or interfaces change.
- No known critical defect is hidden or ignored.

Before an MVP release, additionally verify the primary end-to-end workflows, production build, migration process, deployment configuration, and essential monitoring.

## 14. Known Limitations

Testing cannot guarantee that every research claim is correct or that every provider record is complete.

Automated AI evaluation is an approximation and must be combined with careful evaluation of representative examples. Citation correctness, source fidelity, and uncertainty handling deserve special attention.

Live research databases change over time. Tests should validate the correctness of our processing and contracts rather than assume a provider's entire dataset is static.

## 15. Decisions to Finalize During Implementation

- The exact frontend test runner.
- The end-to-end testing framework.
- The CI provider and required checks.
- The supported PostgreSQL test setup.
- The initial AI evaluation dataset and acceptance thresholds.
- The extent of automated accessibility testing.
- The optional live-provider smoke-test procedure.

The supported PostgreSQL integration-test setup remains open. Current SQLite tests cover portable constraints, while PostgreSQL-only behavior still needs validation against an isolated PostgreSQL server.
