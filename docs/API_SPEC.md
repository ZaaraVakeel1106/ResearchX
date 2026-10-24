# Research X — API Specification

**Status:** Proposed contract
**Product:** Research X
**API prefix:** `/api/v1`
**Purpose:** Define consistent frontend/backend communication before implementation.

## 1. API Principles

The Research X API must:

- Use predictable REST-style routes.
- Return JSON for successful API responses and structured errors.
- Validate request parameters and request bodies.
- Use stable internal IDs for application records.
- Avoid exposing database models directly as API contracts.
- Distinguish missing data from failed requests.
- Preserve bibliographic provenance and relationship types.
- Enforce authorization on the backend for private user data.
- Document pagination, limits, and filtering.
- Never fabricate metadata, citations, or evidence.

The API contract is authoritative for frontend/backend integration. If implementation requires a material change, update this document and relevant tests.

## 2. Base URL and Versioning

All application API routes use the `/api/v1` prefix.

For local development, the frontend and backend may run on separate ports. Configure the frontend's API base URL through an environment variable rather than hardcoding deployment-specific addresses throughout the application.

The exact production domain is a deployment decision and is not specified here.

## 3. Request and Response Conventions

### 3.1 JSON

Use `application/json` for JSON request bodies and responses.

Requests without a body should not require an artificial empty JSON object.

### 3.2 IDs

Use stable internal identifiers in application routes. External identifiers such as DOIs and provider-specific IDs must be validated and resolved through documented lookup behavior.

### 3.3 Dates and Timestamps

- Dates use `YYYY-MM-DD`.
- Timestamps use ISO 8601 with an explicit timezone, normally UTC.
- Publication dates may be incomplete in the source data.
- Do not invent missing dates.

### 3.4 Pagination

Large result sets must be bounded.

Use a consistent pagination scheme. The initial implementation may use offset-based pagination for straightforward search results and cursor-based pagination where stable traversal or large result sets justify it.

Every paginated response must document its pagination fields. Do not silently truncate results without indicating that more data may exist.

### 3.5 Sorting

Every supported sort option must be explicitly documented. Apply a deterministic secondary sort when necessary to avoid unstable ordering between requests.

### 3.6 Null and Missing Values

Use `null` for known fields whose value is unavailable when the schema permits it. Omit fields only when the contract explicitly defines them as optional.

Do not replace unknown metadata with invented defaults.

## 4. Standard Error Format

Errors should follow a consistent structure.

Example:

```json id="err-rx-01"
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid parameters.",
    "details": [
      {
        "field": "year_from",
        "message": "Must be a valid year."
      }
    ],
    "request_id": "request-id"
  }
}
```

The example is illustrative. The request ID may be omitted only where it is genuinely unavailable.

### 4.1 Error Codes

Initial error codes:

- `VALIDATION_ERROR`: invalid parameters or request body.
- `NOT_FOUND`: requested application resource does not exist or is not accessible under the documented policy.
- `UNAUTHORIZED`: authentication is missing or invalid.
- `FORBIDDEN`: the authenticated user lacks permission.
- `RATE_LIMITED`: request limit exceeded.
- `PROVIDER_UNAVAILABLE`: an external metadata provider cannot currently be used.
- `AI_UNAVAILABLE`: the configured AI service is unavailable.
- `INTERNAL_ERROR`: unexpected server error.

Use appropriate HTTP status codes:

| Status | Meaning |
|---|---|
| `200` | Successful read or operation returning a representation |
| `201` | Resource created |
| `204` | Successful operation with no response body |
| `400` | Malformed request where appropriate |
| `401` | Authentication required or invalid |
| `403` | Authenticated caller lacks permission |
| `404` | Resource not found or deliberately concealed |
| `409` | Conflict with current resource state |
| `422` | Syntactically valid request with invalid field values |
| `429` | Rate limit exceeded |
| `502` | Upstream provider failure |
| `503` | Required service temporarily unavailable |
| `500` | Unexpected internal failure |

Never return stack traces, secrets, internal filesystem paths, or raw provider credentials to clients.

### Workspace, Notes, and Collections API Rules

**Authorization**
- Every endpoint that reads or modifies a private workspace, note, saved paper, or collection must enforce backend ownership or explicit authorization.
- Return a consistent error response when a resource is missing or the caller is not authorized to access it. Do not expose private resource contents in error messages.

**Notes**
- Creating or updating a note must validate its required fields and reject malformed input.
- Updating a note must not silently overwrite unrelated fields.
- Deleting a note must follow the documented deletion policy and must not delete its parent workspace.

**Saved Papers**
- A workspace must not contain duplicate entries for the same canonical paper ID.
- Reading status must use a documented, controlled set of values.
- Removing a paper from a workspace must not delete the canonical paper record or its bibliographic relationships.

**Collections**
- A collection belongs to a workspace and must not be accessible through another workspace without authorization.
- Collection membership must reference existing canonical paper records.
- Deleting a collection must not delete its papers or the parent workspace.

**Pagination and Ordering**
- List endpoints must define bounded pagination and deterministic ordering before implementation.
- API responses must use consistent pagination and error conventions across workspace resources.

**Status:** Proposed — request and response schemas, reading-status values, pagination parameters, and exact error codes must be finalized before implementation.

## 5. Endpoint Inventory

The following endpoints are proposed for the initial product. Implement only when the corresponding feature is scheduled in `docs/FEATURE_PLAN.md`.

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/v1/health` | Application health |
| `GET` | `/api/v1/papers/search` | Search papers |
| `GET` | `/api/v1/papers/{paper_id}` | Retrieve paper details |
| `GET` | `/api/v1/papers/{paper_id}/references` | Retrieve references |
| `GET` | `/api/v1/papers/{paper_id}/citations` | Retrieve citing papers |
| `GET` | `/api/v1/graph/{paper_id}` | Retrieve a bounded graph neighborhood |
| `POST` | `/api/v1/reader/{paper_id}/questions` | Ask an evidence-grounded question |
| `POST` | `/api/v1/workspaces` | Create a workspace |
| `GET` | `/api/v1/workspaces` | List the current user's workspaces |
| `GET` | `/api/v1/workspaces/{workspace_id}` | Retrieve a workspace |
| `POST` | `/api/v1/workspaces/{workspace_id}/papers` | Save a paper |
| `DELETE` | `/api/v1/workspaces/{workspace_id}/papers/{paper_id}` | Remove a saved paper |
| `POST` | `/api/v1/workspaces/{workspace_id}/notes` | Create a note |
| `GET` | `/api/v1/workspaces/{workspace_id}/notes` | List notes in a workspace |
| `GET` | `/api/v1/workspaces/{workspace_id}/notes/{note_id}` | Retrieve a note |
| `PATCH` | `/api/v1/workspaces/{workspace_id}/notes/{note_id}` | Update a note |
| `DELETE` | `/api/v1/workspaces/{workspace_id}/notes/{note_id}` | Delete a note |
| `GET` | `/api/v1/workspaces/{workspace_id}/papers` | List saved papers and reading statuses |
| `POST` | `/api/v1/workspaces/{workspace_id}/collections` | Create a collection |
| `GET` | `/api/v1/workspaces/{workspace_id}/collections` | List collections |
| `GET` | `/api/v1/workspaces/{workspace_id}/collections/{collection_id}` | Retrieve a collection |
| `PATCH` | `/api/v1/workspaces/{workspace_id}/collections/{collection_id}` | Update a collection |
| `DELETE` | `/api/v1/workspaces/{workspace_id}/collections/{collection_id}` | Delete a collection |
| `POST` | `/api/v1/compare` | Compare selected papers |

Authentication, health checks, and optional feature routes must be finalized before their implementation. This inventory does not imply that every endpoint is part of the first coding milestone.

## 6. Health Check

### `GET /api/v1/health`

Purpose: confirm that the API process is responding.

Successful response: `200 OK`.

```json id="rx-health"
{
  "status": "ok"
}
```

This endpoint should not expose secrets, environment variables, database connection strings, or sensitive infrastructure details.

If a separate readiness check is required to verify database or provider connectivity, define it explicitly rather than making a simple liveness endpoint perform expensive external calls.

## 7. Paper Search

### `GET /api/v1/papers/search`

Purpose: search for academic papers using a configured metadata provider.

Proposed query parameters:

| Parameter | Type | Meaning |
|---|---|---|
| `q` | string | Search query |
| `year_from` | integer | Earliest publication year |
| `year_to` | integer | Latest publication year |
| `author` | string | Author-name filter where supported |
| `open_access` | boolean | Filter to records with reliably established open-access status, where supported |
| `sort` | string | Supported sort option |
| `page` | integer | Page number for offset-based pagination |
| `page_size` | integer | Number of results requested, subject to a server-side maximum |

At least a non-empty query or another explicitly supported discovery criterion must be provided. Exact validation rules must be finalized during implementation.

Successful response: `200 OK`.

```json id="rx-search"
{
  "items": [
    {
      "id": "internal-paper-id",
      "title": "Example Research Paper",
      "authors": [
        {
          "id": "internal-author-id",
          "display_name": "Example Author"
        }
      ],
      "publication_year": 2025,
      "venue": null,
      "doi": null,
      "abstract": null,
      "landing_page_url": null,
      "open_access_status": null,
      "metadata_provenance": {
        "provider": "configured-provider",
        "retrieved_at": "2026-01-01T00:00:00Z"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": null,
    "has_more": false
  }
}
```

All sample values are illustrative. Actual responses must use real retrieved metadata. The provider name and retrieval timestamp must not be fabricated.

Requirements:

- Return normalized application records.
- Preserve provider provenance.
- Validate filters and page sizes.
- Enforce a documented maximum page size.
- Handle provider failures with a structured error.
- Do not treat an unavailable provider as a successful empty search.
- Distinguish a genuinely empty result set from an upstream failure.
- Avoid returning duplicate records where canonical identity can be established safely.

## 8. Paper Details

### `GET /api/v1/papers/{paper_id}`

Purpose: retrieve one canonical paper record.

Successful response: `200 OK`.

The response should include available bibliographic metadata, authors in source order, external identifiers, provenance, and links to available application features.

Requirements:

- Return `404` for an unknown or deliberately inaccessible resource.
- Represent unavailable metadata as `null` where allowed.
- Do not assume a full-text document is available.
- Do not imply that a landing-page URL is a direct PDF URL.
- Do not return unrestricted raw provider payloads by default.

## 9. References and Citing Papers

### `GET /api/v1/papers/{paper_id}/references`

Returns papers referenced by the requested paper.

### `GET /api/v1/papers/{paper_id}/citations`

Returns papers that cite the requested paper.

Both endpoints should support bounded pagination and return relationship provenance.

A response should distinguish:

- Resolved references.
- Unresolved references, if included by the selected response mode.
- Provider-backed citation records.
- Any known coverage limitations.

Citation direction must remain consistent with `docs/GRAPH_MODEL.md`.

If the provider does not support a requested relationship or lacks sufficient coverage, report the limitation accurately.

## 10. Graph Neighborhood

### `GET /api/v1/graph/{paper_id}`

Purpose: return a bounded graph centered on a selected paper.

Proposed query parameters:

| Parameter | Type | Meaning |
|---|---|---|
| `depth` | integer | Traversal depth within a documented range |
| `limit` | integer | Maximum number of nodes |
| `relationships` | repeated or delimited values | Relationship types to include |
| `year_from` | integer | Optional lower publication-year bound |
| `year_to` | integer | Optional upper publication-year bound |

The final query encoding must be selected consistently during implementation.

Response structure:

- `root_paper_id`
- `nodes`
- `edges`
- `truncated`
- `next_cursor`, when pagination is used

Each edge must have a documented type, direction, and origin. Similarity and AI-inferred relationships must not be returned as citations.

The endpoint must:

- Validate depth and limits.
- Prevent unbounded traversal.
- Avoid duplicate nodes and edges.
- Handle cycles safely.
- Indicate truncation.
- Apply authorization to private workspace information.
- Return useful results when some paper metadata is missing.

## 11. Evidence-Grounded Reader

### `POST /api/v1/reader/{paper_id}/questions`

Purpose: answer a question using retrieved evidence associated with a paper and any explicitly permitted supporting sources.

Proposed request:

```json id="rx-question"
{
  "question": "What limitations do the authors discuss?",
  "workspace_id": null
}
```

`workspace_id` is optional and must be authorized if supplied.

Proposed successful response:

```json id="rx-answer"
{
  "answer": "The available evidence indicates ...",
  "evidence": [
    {
      "paper_id": "internal-paper-id",
      "passage_id": "evidence-passage-id",
      "quote": "A short supporting passage, when retention and display are permitted.",
      "locator": {
        "page": null,
        "section": "Limitations"
      },
      "relationship_to_claim": "supports"
    }
  ],
  "limitations": [
    "The available text may not contain the complete paper."
  ],
  "answer_status": "answered"
}
```

The example is illustrative, not a guarantee that all fields are always available.

Requirements:

- Validate question length and request size.
- Retrieve evidence before generating the answer.
- Ground factual claims in retrieved source material.
- Keep evidence references linked to the correct source.
- Never fabricate quotations, page numbers, sections, or citations.
- Clearly state when evidence is insufficient.
- Distinguish a paper's own claims from external interpretations.
- Respect copyright, provider terms, and user-document permissions.
- Do not imply that the AI answer replaces reading the source.
- Do not expose internal prompts, API keys, or hidden provider configuration.

If reliable evidence cannot be retrieved, return a safe insufficient-evidence response or a documented service error, depending on the failure.

## 12. Workspaces

### `POST /api/v1/workspaces`

Creates a workspace for the authenticated user.

Proposed request:

```json id="rx-workspace-create"
{
  "name": "My Research",
  "description": "Research on a selected topic."
}
```

Successful response: `201 Created`.

### `GET /api/v1/workspaces`

Returns only workspaces the authenticated user is authorized to access.

### `GET /api/v1/workspaces/{workspace_id}`

Returns workspace details and documented membership information.

### `POST /api/v1/workspaces/{workspace_id}/papers`

Saves an existing canonical paper to the workspace.

Proposed request:

```json id="rx-workspace-paper"
{
  "paper_id": "internal-paper-id",
  "reading_status": "to_read"
}
```

The API must validate the reading status and handle duplicate membership according to a documented policy, such as an idempotent response or `409 Conflict`.

### `DELETE /api/v1/workspaces/{workspace_id}/papers/{paper_id}`

Removes the paper's workspace membership. It must not delete the shared bibliographic paper record.

### `POST /api/v1/workspaces/{workspace_id}/notes`

Creates a user-authored note.

Proposed request:

```json id="rx-note"
{
  "title": "Key observations",
  "body": "My notes from reading this paper.",
  "paper_id": "internal-paper-id"
}
```

`title` and `paper_id` may be nullable according to the finalized schema.

Requirements:

- Authenticate the caller.
- Verify workspace ownership or authorized membership.
- Validate referenced papers and workspace rules.
- Preserve user-authored content separately from generated content.
- Apply documented deletion and retention behavior.

## 13. Paper Comparison

### `POST /api/v1/compare`

Purpose: compare a bounded set of papers.

Proposed request:

```json id="rx-compare-request"
{
  "paper_ids": [
    "paper-id-one",
    "paper-id-two"
  ],
  "comparison_question": "Compare the methods and limitations."
}
```

The exact minimum and maximum number of papers must be defined before implementation.

The response should provide a structured comparison, including relevant evidence references where AI-generated analysis is used.

Requirements:

- Validate all paper IDs.
- Avoid silently omitting requested papers.
- Identify unavailable abstracts or full text.
- Distinguish source-supported differences from generated interpretation.
- Cite the evidence supporting substantive claims.
- State when there is insufficient evidence for a comparison.

## 14. Authentication and Authorization

Authentication must be selected before private workspace endpoints are implemented.

Once authentication is enabled:

- Require valid authentication for private workspace operations.
- Derive the current user identity from verified authentication context.
- Never authorize access solely on a client-supplied user ID.
- Check resource ownership or explicit membership on every private resource request.
- Return consistent unauthorized or forbidden errors.
- Avoid leaking whether private resources exist when the security policy requires concealment.
- Keep secrets in server-side environment configuration or an appropriate secret manager.

Public paper search and public bibliographic endpoints may remain unauthenticated if rate limiting, provider terms, and deployment requirements permit.

## 15. External Provider Failures

The metadata provider and AI service are external dependencies.

The API must:

- Apply timeouts.
- Handle rate limits.
- Avoid uncontrolled retry loops.
- Return documented errors when a required dependency fails.
- Log diagnostic context without leaking sensitive information.
- Avoid presenting stale cached data as freshly retrieved data.
- Identify cached or previously retrieved data where freshness matters.

Fallback behavior must be defined per endpoint. A provider outage must not silently become a misleading empty result set.

## 16. Rate Limiting and Resource Limits

Set configurable limits for:

- Search page size.
- Query length.
- Graph depth and node count.
- Reader question length.
- Comparison request size.
- Request frequency for expensive AI and provider-backed endpoints.

Limits must be enforced on the backend. The API should return `429` when a documented rate limit is exceeded.

Exact production values should be chosen after initial testing and deployment constraints are understood.

## 17. Logging and Observability

Record enough information to diagnose API failures, including:

- Request ID.
- Route and HTTP status.
- Request duration.
- Provider failure category.
- Relevant error code.

Do not log API keys, authentication tokens, full private documents, or sensitive user content by default.

Logs should help diagnose failures without becoming an unnecessary repository of research questions or private notes.

## 18. API Testing Requirements

Tests must cover:

- Successful requests and response schemas.
- Missing and invalid query parameters.
- Invalid request bodies.
- Not-found behavior.
- Pagination boundaries.
- Provider timeouts and errors.
- Empty search results.
- Missing paper metadata.
- Citation direction and unresolved references.
- Graph truncation and depth limits.
- Insufficient-evidence responses.
- Authentication and workspace authorization.
- Duplicate workspace-paper operations.
- AI and provider rate limits where implemented.
- Prevention of sensitive information in error responses.

Use mocked external services for deterministic unit tests. Add controlled integration tests for actual database and provider adapters where appropriate.

## 19. API Documentation and Change Management

- Implement the API using FastAPI request and response schemas.
- Keep OpenAPI output aligned with this contract.
- Validate response schemas in automated tests.
- Update this document whenever endpoint behavior changes materially.
- Keep API changes compatible where practical.
- Record breaking changes and design decisions in `docs/DECISIONS.md`.
- Do not implement every listed endpoint in one large change. Follow the staged feature plan.

## 20. Decisions Still Required

Before endpoint implementation, finalize:

1. Authentication provider and exact authentication mechanism.
2. Search provider and supported search filters.
3. Pagination strategy for each endpoint.
4. Final response schemas and field names.
5. Graph relationship query encoding and limits.
6. Reader evidence response and insufficient-evidence behavior.
7. Workspace duplicate-operation semantics.
8. API rate limits and request-size limits.
9. Caching and freshness indicators.
10. Which endpoints belong in the first runnable vertical slice.

## 21. Acceptance Criteria

The API specification is ready to guide implementation when:

- Routes, methods, and responsibilities are clear.
- Request validation and error behavior are consistent.
- Pagination and resource limits are documented.
- Citation, similarity, and inferred relationships remain distinct.
- Evidence-backed AI behavior is specified.
- Private data has explicit authorization requirements.
- External-service failures are handled honestly.
- Automated tests can verify the contract.
