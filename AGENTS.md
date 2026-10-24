# Research X — Agent Instructions

## 1. Project Overview

Research X is an AI-powered research discovery and exploration platform.

Its purpose is to help users:

- Discover academic papers.
- Understand papers and their evidence.
- Explore citation networks and related research.
- Compare research methods, findings, and limitations.
- Organize papers, notes, and research questions.
- Identify potential research directions without making unsupported novelty claims.

The product requirements and boundaries are defined in `docs/PRODUCT_SPEC.md`.

## 2. Mandatory Reading Before Changes

Before implementing a feature or making architectural changes:

1. Read this file.
2. Read `docs/PRODUCT_SPEC.md`.
3. Read the relevant technical documentation in `docs/`.
4. Inspect the existing implementation, tests, and configuration.
5. Check the current Git branch and working-tree status.

If a required document does not exist yet, do not invent its contents or claim that it has been reviewed.

When requirements conflict, identify the conflict and ask for clarification if it materially affects correctness, security, or architecture.

## 3. Protect Existing Work

- Never overwrite, discard, or revert user changes without explicit permission.
- Inspect `git status` before making changes.
- Do not use destructive Git commands such as `git reset --hard`, `git clean -fd`, or forced pushes unless explicitly authorized for the specific operation.
- Do not modify unrelated files to make a task appear complete.
- Do not commit or push changes unless explicitly instructed.
- Do not switch branches or merge branches without an explicit request.
- Never commit `.env` files, API keys, access tokens, passwords, private credentials, or other secrets.
- Preserve the existing Git history.

## 4. Scope and Implementation

- Implement only the requested feature and its necessary dependencies.
- Prefer small, understandable, maintainable changes.
- Follow the existing architecture and conventions.
- Avoid unnecessary abstractions, duplicated logic, and premature optimization.
- Do not introduce microservices or additional infrastructure without a documented reason.
- Do not replace working implementations simply because another approach is preferred.
- Keep frontend, backend, database access, external integrations, and AI processing separated according to the documented architecture.
- Do not silently change API contracts, database schemas, environment variables, or public interfaces.
- Update relevant documentation whenever implementation changes affect documented behavior.

## 5. Research Data Integrity

- Never fabricate papers, authors, titles, DOIs, publication dates, references, quotations, evidence passages, or research results.
- Use real academic metadata from approved sources in application workflows.
- Clearly distinguish live data from fixtures, test data, and illustrative examples.
- Preserve source identifiers and provenance wherever practical.
- Deduplicate papers using stable identifiers when available.
- Handle missing, conflicting, and incomplete metadata explicitly.
- Do not treat a missing record as proof that something does not exist.
- Do not claim comprehensive coverage of academic literature without evidence.

## 6. Citation Graph Rules

Every relationship displayed in the research graph must have an identifiable relationship type.

At minimum, distinguish:

- Bibliographic citation relationships.
- Content-based semantic similarity.
- AI-inferred or otherwise unverified relationships.

Never present semantic similarity or an AI-generated suggestion as a verified citation.

Where available, preserve the source and relevant metadata for each relationship.

Graph traversal must have reasonable depth, node, and request limits.

## 7. AI and Evidence Rules

- Ground paper-specific factual answers in content actually retrieved and processed.
- Provide source links or passage references for supported claims whenever available.
- Never invent quotations, page numbers, citations, experimental results, or paper contents.
- Distinguish source statements from model interpretation.
- State clearly when evidence is missing, incomplete, contradictory, or insufficient.
- Never imply that a full paper was analyzed when only its abstract or a partial text was available.
- Treat research-gap suggestions as hypotheses requiring further verification.
- Keep AI provider credentials on the backend.
- Do not send private user data to external providers unnecessarily.
- Keep model and provider integration behind documented backend interfaces where appropriate.
- Use mocked AI responses in ordinary automated tests.

## 8. Security and Privacy

- Validate and constrain all untrusted inputs.
- Enforce authentication and resource-ownership checks wherever applicable.
- Keep secrets in environment variables or approved secret-management systems.
- Maintain a safe `.env.example` containing placeholders only.
- Restrict cross-origin requests to approved origins.
- Apply sensible request, upload, graph-expansion, and AI usage limits.
- Validate uploaded file types and sizes.
- Defend document retrieval against server-side request forgery and unsafe URL access.
- Avoid logging credentials, sensitive document content, or unnecessary personal data.
- Respect academic provider terms, copyright, licenses, and access restrictions.
- Do not bypass paywalls or access controls.

## 9. Testing and Quality

- Add or update tests for behavior changed by the task.
- Use unit tests for isolated logic and integration tests for component boundaries.
- Mock external APIs and AI providers in routine automated tests.
- Include failure cases, invalid inputs, and missing-data scenarios.
- Never weaken or delete a test solely to make the test suite pass.
- Do not claim tests passed unless they were actually run and their results inspected.
- Report existing failures separately from regressions introduced by the change.
- Run the narrowest relevant test suite first, then broader checks when practical.
- Check formatting, linting, types, and build results according to the project's configured tools.

## 10. Database and API Changes

- Follow the documented data model and API specification.
- Use versioned database migrations for schema changes.
- Do not rely on destructive automatic schema synchronization.
- Validate request and response schemas.
- Return consistent, documented error responses.
- Use pagination and limits for potentially large result sets.
- Preserve compatibility unless a breaking change is explicitly approved.
- Never assume external API fields are always present or correctly formatted.

## 11. Dependencies and Configuration

- Prefer existing dependencies when they adequately solve the problem.
- Add a new dependency only when its value justifies its maintenance and security cost.
- Pin or constrain dependencies consistently with the chosen package-management approach.
- Document newly required environment variables.
- Update dependency files, setup instructions, and tests when necessary.
- Do not invent API keys or claim external services are configured when they are not.

## 12. Documentation

- Keep documentation consistent with the actual implementation.
- Mark unresolved decisions explicitly instead of silently assuming answers.
- Record important architectural decisions and their rationale.
- Update the feature plan and relevant specifications as features progress.
- Keep setup instructions reproducible for a new developer.
- Do not describe planned features as implemented features.

## 13. Working Procedure

For each task:

1. Restate the intended scope briefly.
2. Inspect relevant files and existing changes.
3. Identify dependencies and applicable requirements.
4. Implement the smallest complete solution.
5. Add or update tests.
6. Run relevant checks.
7. Review the final diff for unrelated changes, secrets, and inconsistencies.
8. Update relevant documentation.
9. Report what changed, files affected, tests run, test outcomes, and remaining limitations.

If blocked by missing requirements, credentials, unavailable services, or contradictory specifications, explain the blocker instead of fabricating a solution.

## 14. Completion Criteria

A task is complete only when:

- Its requested behavior is implemented.
- Relevant tests and checks have been run where feasible.
- The changes are limited to the intended scope.
- Documentation reflects the resulting behavior.
- No secrets or unrelated user changes are included.
- Remaining limitations and unverified assumptions are reported honestly.

**Core rule:** Correctness, evidence integrity, security, and maintainability take priority over speed or apparent completeness.