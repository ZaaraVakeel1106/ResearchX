# Development Workflow — Research X

## 1. Purpose

This document defines how Research X is developed, reviewed, tested, and maintained using Git, GitHub, VS Code, and AI coding assistants such as Codex.

The goal is to make development predictable, maintainable, and safe while allowing features to be built incrementally.

## 2. Core Rules

- Read `AGENTS.md` and relevant documentation before implementing a feature.
- Follow `PRODUCT_SPEC.md`, `ARCHITECTURE.md`, `DATA_MODEL.md`, `GRAPH_MODEL.md`, `API_SPEC.md`, `AI_AND_EVIDENCE.md`, and `SECURITY_AND_PRIVACY.md` as applicable.
- Work on one clearly defined task at a time.
- Keep changes focused and avoid unrelated refactoring.
- Inspect existing code before creating or modifying files.
- Preserve user changes and never overwrite work without understanding its purpose.
- Do not fabricate test results, research metadata, citations, or implementation status.
- Run appropriate tests and report their actual outcomes.
- Update documentation when implementation decisions or public interfaces change.
- Never commit or push changes without explicit authorization from the user.

## 3. Repository and Branch Strategy

The default branch is `main`.

Use feature branches for meaningful implementation tasks.

Recommended branch naming:

- `feat/paper-search`
- `feat/citation-graph`
- `feat/evidence-reader`
- `feat/workspaces`
- `fix/metadata-deduplication`
- `test/graph-edge-cases`
- `docs/api-clarifications`

Keep branch names short and descriptive.

### Branch rules

1. Start new work from an up-to-date `main` unless a task explicitly depends on another branch.
2. Confirm the current branch and working-tree status before switching branches or pulling changes.
3. Never discard uncommitted work merely to change branches.
4. Avoid implementing multiple unrelated features in one branch.
5. Merge changes through the repository's agreed review process.
6. Do not force-push or rewrite shared history without explicit authorization.

The exact merge and branch-protection settings will be configured after the initial repository setup.

## 4. Standard Task Lifecycle

Every implementation task follows this sequence.

### Step 1: Understand

- Read the relevant acceptance criteria in `FEATURE_PLAN.md`.
- Inspect the related architecture, API, data model, graph model, and security requirements.
- Identify dependencies and existing implementations.
- List assumptions and unresolved questions.

### Step 2: Plan

Before editing, identify:

- Files likely to change.
- Expected behavior.
- API or database implications.
- Security and privacy implications.
- Tests required.
- Documentation requiring updates.
- Risks and dependencies.

For larger tasks, present the plan for review before implementing.

### Step 3: Implement

- Make the smallest coherent change that meets the requirements.
- Reuse existing abstractions where appropriate.
- Avoid unnecessary dependencies.
- Keep business logic separate from route handlers and presentation components.
- Validate external data at integration boundaries.
- Preserve provenance for research metadata and AI evidence.
- Do not introduce unrelated features.

### Step 4: Verify

- Run focused tests first.
- Run relevant broader tests.
- Run linting, formatting, type checks, and builds when configured.
- Inspect failures rather than assuming they are unrelated.
- Check the Git diff for accidental edits, secrets, debug code, and generated files.
- Confirm that documentation and tests match the implementation.

### Step 5: Report

The completion report should state:

- What changed.
- Which files changed.
- Which tests and checks were run.
- Which checks passed or failed.
- Any known limitations.
- Any database migration or configuration requirements.
- Whether the work remains uncommitted.

Never report an unrun test as passing.

### Step 6: Review and Integrate

Review the diff and verify acceptance criteria before merging.

Commit, push, open a pull request, or merge only when the user explicitly authorizes the relevant action.

## 5. Using Codex Safely

Codex should be treated as a coding assistant working within the repository's documented requirements, not as an unquestioned source of truth.

For every task, its instructions should specify:

1. The feature or defect being addressed.
2. Relevant documentation to read.
3. Expected behavior and acceptance criteria.
4. Files or modules likely to be affected.
5. Constraints and explicitly excluded work.
6. Required tests and documentation updates.
7. The expected completion report.

Codex should inspect the repository before proposing file changes. It must not assume the architecture described in documentation has already been implemented.

### Required behavior

- Follow repository instructions in `AGENTS.md`.
- Inspect existing code and tests before editing.
- Ask for clarification when a material ambiguity cannot be resolved safely.
- Avoid unrelated changes and speculative dependencies.
- Never expose secrets in source code, logs, examples, or test fixtures.
- Never change production data or external services during ordinary testing.
- Never bypass a failing test by deleting it or weakening its assertions without justification and approval.
- Never claim tests passed without executing them and inspecting the results.
- Summarize any deviation from the requested scope.

### Human review

Before accepting generated changes:

- Inspect the diff.
- Check correctness and maintainability.
- Verify error handling and input validation.
- Review database and API compatibility.
- Confirm research claims remain source-grounded.
- Run appropriate tests.
- Reject unnecessary complexity.

## 6. Git Safety

Before starting a task:

```powershell
git status --short --branch
git branch --show-current
```

Before reviewing a change:

```powershell
git diff --check
git diff --stat
git diff
```

Before staging:

```powershell
git status --short
```

Stage only intended files. Prefer explicit file paths over staging everything when unrelated or generated changes may exist.

After staging, review the staged changes:

```powershell
git diff --cached --check
git diff --cached --stat
git diff --cached
```

Do not commit `.env` files, API keys, private documents, local databases, virtual environments, build outputs, or unrelated user files.

These commands are reference examples. Verify the repository state and intended operation before running any command that changes Git state.

## 7. Database and Migration Safety

- Use Alembic for database schema migrations when the backend is implemented.
- Do not manually alter a shared or production database to bypass migrations.
- Review migration scripts before applying them.
- Preserve existing data unless a destructive change is explicitly approved.
- Test migrations against an isolated database.
- Document schema changes and compatibility considerations.
- Keep database credentials outside version control.

Database migrations must be coordinated with the affected models, schemas, repositories, services, and tests.

## 8. API and Frontend Coordination

When an API contract changes:

1. Update `API_SPEC.md`.
2. Update backend request and response schemas.
3. Update route handlers and service logic.
4. Add or update API tests.
5. Update frontend API clients and TypeScript types.
6. Update affected UI behavior and error states.
7. Verify that frontend and backend agree on field names, types, and status codes.

Avoid independently inventing frontend and backend contracts.

## 9. Research Data and AI Change Control

Changes affecting research information require additional review.

- Preserve the distinction between verified citation edges, semantic similarity, and AI-inferred relationships.
- Retain source identifiers and provenance when processing provider metadata.
- Do not fabricate missing paper details or publication dates.
- Keep evidence references attached to supported AI claims.
- Ensure insufficient evidence is handled honestly.
- Treat paper content and retrieved documents as untrusted input.
- Update AI evaluation tests when prompts, retrieval logic, evidence selection, or model behavior changes.
- Document changes that could affect reproducibility or the interpretation of research results.

## 10. Dependency Management

Before introducing a dependency:

- Confirm that existing dependencies do not already solve the problem.
- Check compatibility with the selected runtime and framework.
- Consider maintenance, licensing, security, size, and operational costs.
- Add it only where it provides a clear benefit.
- Update the correct dependency manifest and lockfile.
- Test installation from the recorded dependency definitions.

Do not silently upgrade unrelated dependencies during feature implementation.

## 11. Configuration and Secrets

- Store local secrets in ignored environment files.
- Maintain `.env.example` with placeholder values only.
- Validate required configuration at application startup where appropriate.
- Provide actionable errors when configuration is missing.
- Never paste credentials into prompts, source files, screenshots, commits, or public issues.
- Never log full authorization headers, API keys, or sensitive user content.

If a secret is accidentally committed, treat it as exposed and rotate it. Removing the text from a later commit does not make the secret safe.

## 12. Documentation Maintenance

Update documentation when a change affects:

- Product scope or acceptance criteria.
- Architecture or module boundaries.
- Data models or migrations.
- API contracts.
- Citation graph semantics.
- AI evidence behavior.
- Security or privacy requirements.
- Testing commands or CI checks.
- Deployment and configuration.
- Important implementation decisions.

Avoid documenting planned behavior as if it already exists. Clearly distinguish current implementation, planned work, and unresolved decisions.

## 13. Definition of Done

A task is complete only when:

- Its agreed acceptance criteria are met.
- The implementation follows documented architecture and security requirements.
- Relevant tests have been executed and their outcomes reported.
- Linting, type checks, and builds have been run where configured.
- API and data model changes are consistent.
- Required documentation is updated.
- The diff has been reviewed for unintended changes and secrets.
- Known limitations are documented.
- Git operations have stayed within the user's authorization.

A feature is not considered complete merely because its code has been generated.

## 14. Initial Development Constraints

During repository preparation:

- Finish and review the foundational documentation first.
- Do not prematurely implement every planned feature.
- Establish the application skeleton and development tooling before feature work.
- Verify provider availability, usage restrictions, and integration requirements before committing to an external service.
- Record significant architectural decisions.
- Implement incrementally, validating each stage before moving forward.

## 15. Decisions to Finalize

- Pull request and branch protection policy.
- Required code review and CI checks.
- Exact formatting, linting, and test commands.
- Codex task and review conventions.
- Release and versioning strategy.
- Database migration review procedure.

Record finalized decisions in `DECISIONS.md` and keep this workflow aligned with the actual repository configuration.