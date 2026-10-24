# Research X — Data Model

**Status:** Proposed design; initial database foundation implemented
**Product:** Research X
**Purpose:** Define the core entities, relationships, identifiers, constraints, and provenance requirements for database implementation.

## 1. Design Goals

The data model must:

- Represent academic papers and their bibliographic metadata accurately.
- Support authors, references, citations, and paper relationships.
- Distinguish verified bibliographic relationships from inferred or AI-generated relationships.
- Preserve the origin of imported metadata and extracted evidence.
- Support user workspaces, collections, notes, and reading progress.
- Avoid duplicate papers when multiple data providers describe the same work.
- Allow schema changes through reviewed database migrations.
- Avoid storing full paper text unless its source, licence, and permitted use have been established.

## 2. Database Choice

The proposed primary database is PostgreSQL.

Use relational tables and foreign keys for authoritative application data. Use indexed relational queries initially for citation traversal and graph construction. Do not introduce a dedicated graph database unless measured requirements justify it.

Use SQLAlchemy models and Alembic migrations in the backend. Pydantic schemas define API input and output contracts separately from database models.

### Initial database implementation choices

The initial schema uses separate paper and author external-identifier tables, preserving original values and optional normalized values. Metadata snapshots are JSONB on PostgreSQL, one snapshot per paper and source retrieval. The initial workspace schema includes skeletal users and workspaces, flat collections, and notes that can refer to at most one optional paper. A paper-linked note must point to a paper saved in that same workspace. Evidence passages and persisted AI answers are deferred until retention decisions are made. Non-citation relationship scores remain nullable and have no range check until their scale is defined.

These choices define the scope of the initial migration only. Authentication and verification behavior, deletion and retention policy, deduplication, and evidence/AI persistence remain open. The `DECISIONS.md` statuses are not changed by this implementation.

DOI values are stored in the paper external-identifier table; the schema does not duplicate them in a dedicated `papers.doi` column.

## 3. Identifier Rules

### 3.1 Internal IDs

Use UUIDs for internal primary keys where appropriate. Internal identifiers must remain stable even if an external provider changes its identifiers or metadata.

### 3.2 External Identifiers

Store external identifiers with their provider and identifier type. Examples include:

- DOI
- OpenAlex work ID
- Semantic Scholar paper ID
- arXiv ID

External identifiers are not interchangeable. Normalize their formatting where appropriate, but preserve the original provider value when needed for provenance.

A DOI may be used as a strong deduplication signal after normalization and validation. Do not merge papers solely because their titles look similar.

### 3.3 Canonical Paper Identity

A single canonical paper record may be associated with multiple external identifiers.

When identity is uncertain, retain separate records or mark a possible duplicate for review rather than silently merging distinct works.

## 4. Core Entities

### 4.1 Paper

Represents one academic work.

Proposed fields:

- `id`: UUID primary key.
- `title`: normalized display title.
- `abstract`: nullable abstract text.
- `publication_year`: nullable integer.
- `publication_date`: nullable date.
- `venue`: nullable journal, conference, or publication venue.
- `publication_type`: nullable normalized type.
- `language`: nullable language code.
- `doi`: nullable normalized DOI, when available.
- `landing_page_url`: nullable canonical public landing-page URL.
- `open_access_status`: nullable status when reliably supplied.
- `created_at`: timestamp.
- `updated_at`: timestamp.

Rules:

- Missing metadata must remain missing or explicitly unknown; never fabricate values.
- Validate years and URLs.
- Do not assume every paper has an abstract, DOI, PDF, or open-access copy.
- Keep provider-specific metadata in source records or structured provenance rather than continually adding provider-specific columns to `papers`.

A separate identifier table is the preferred long-term way to represent multiple external IDs. The nullable `doi` field above is a convenience proposal, not a requirement to duplicate DOI storage.

### 4.2 Author

Represents a person listed as an author.

Proposed fields:

- `id`: UUID primary key.
- `display_name`: name as supplied by a source.
- `normalized_name`: optional search and matching value.
- `created_at`: timestamp.

Author names alone do not establish identity. Different people may share a name, and one person may have several name variants.

Where supported, associate authors with provider-specific author identifiers.

### 4.3 PaperAuthor

Joins papers to authors and preserves author order.

Proposed fields:

- `paper_id`: foreign key to `papers`.
- `author_id`: foreign key to `authors`.
- `author_order`: zero-based or one-based position, chosen consistently.
- `is_corresponding`: nullable Boolean when reliably known.
- `source_record_id`: nullable reference to the metadata source establishing the association.

Constraints:

- Use a composite primary key or an equivalent uniqueness constraint.
- Enforce uniqueness of author order within a paper.
- Preserve the order reported by the source.

### 4.4 ExternalIdentifier

Maps internal entities to external identifiers.

Proposed fields:

- `id`: UUID primary key.
- `entity_type`: supported entity type, initially `paper` or `author`.
- `entity_id`: internal entity identifier.
- `provider`: source system, such as OpenAlex.
- `identifier_type`: DOI, provider work ID, arXiv ID, and so on.
- `identifier_value`: original or normalized external value as appropriate.
- `created_at`: timestamp.

The implementation must enforce identifier uniqueness safely. Because a generic `entity_type`/`entity_id` pair does not provide an ordinary foreign key to multiple tables, consider separate paper and author identifier tables if strict referential integrity is required. Do not implement a polymorphic reference without documenting and testing its integrity rules.

### 4.5 PaperReference

Represents a bibliographic citation from one paper to another.

Proposed fields:

- `id`: UUID primary key.
- `citing_paper_id`: paper that contains the reference.
- `cited_paper_id`: referenced paper, nullable if unresolved.
- `external_reference_key`: nullable provider reference identifier.
- `raw_reference_text`: nullable reference string when permitted.
- `resolution_status`: `resolved`, `unresolved`, or `ambiguous`.
- `source_record_id`: source that supplied the reference.
- `created_at`: timestamp.

Rules:

- A citation direction must be explicit: citing paper → cited paper.
- Prevent a paper from citing itself unless a verified data correction requires an exception.
- Avoid duplicate reference edges from the same source.
- Preserve unresolved references so users can see that a reference exists even when the target paper has not been identified.
- Do not represent an unresolved reference as a verified edge to a guessed paper.

### 4.6 MetadataSource

Represents a provider or source used to retrieve bibliographic information.

Proposed fields:

- `id`: UUID primary key.
- `provider_name`: provider identifier.
- `provider_record_id`: external record ID, where available.
- `source_url`: nullable source record URL.
- `retrieved_at`: retrieval timestamp.
- `license_or_terms_reference`: nullable reference to applicable terms or licence documentation.
- `record_checksum`: nullable checksum of the retained source payload.
- `created_at`: timestamp.

The design must support auditing where a field or relationship came from. Avoid retaining full raw provider payloads indefinitely without a clear purpose, storage policy, and review of applicable terms.

### 4.7 PaperMetadataSnapshot

Preserves selected metadata received from a provider at a point in time.

Proposed fields:

- `id`: UUID primary key.
- `paper_id`: foreign key to `papers`.
- `metadata_source_id`: foreign key to `metadata_sources`.
- `field_name`: metadata field name.
- `field_value`: value in a suitable structured representation.
- `observed_at`: timestamp.

This is a proposed provenance mechanism. The implementation may instead use a well-defined JSON snapshot table if that is simpler and more efficient. Choose one consistent strategy; do not maintain redundant competing representations without a demonstrated need.

### 4.8 PaperRelationship

Represents relationships that are not necessarily direct citations.

Proposed fields:

- `id`: UUID primary key.
- `source_paper_id`: foreign key to `papers`.
- `target_paper_id`: foreign key to `papers`.
- `relationship_type`: controlled value using the canonical top-level types `SIMILAR_TO` or `INFERRED_RELATED_TO`. Direct bibliographic citations are represented by the citation/reference model and must retain the direction citing paper → cited paper. If the implementation later stores all edge types in a unified relationship table, update the schema and documentation together to include `CITES` explicitly.
- `origin_type`: `provider`, `computed`, or `ai_inferred`.
- `score`: nullable numeric score with a documented meaning and range.
- `explanation`: nullable short explanation.
- `evidence_reference`: nullable reference to supporting evidence.
- `model_or_method_version`: nullable identifier for the algorithm or model.
- `created_at`: timestamp.

Rules:

- Direct citations belong in the citation/reference model, not as unlabelled similarity edges.
- Every inferred relationship must be distinguishable from a verified bibliographic fact.
- A score is not automatically a probability.
- Record the method or model version when reproducibility matters.
- Avoid storing AI explanations as established facts.

### 4.9 User

Represents an application account when authentication is introduced.

Proposed fields:

- `id`: UUID primary key.
- `email`: verified or pending email according to the authentication design.
- `created_at`: timestamp.
- `updated_at`: timestamp.

Authentication provider identifiers and verification state should be added according to the selected authentication approach. Never store plaintext passwords.

### 4.10 Workspace

Represents a user's research environment.

Proposed fields:

- `id`: UUID primary key.
- `owner_user_id`: foreign key to `users`.
- `name`: workspace name.
- `description`: nullable description.
- `created_at`: timestamp.
- `updated_at`: timestamp.

### 4.11 WorkspacePaper

Joins a workspace to saved papers.

Proposed fields:

- `workspace_id`: foreign key to `workspaces`.
- `paper_id`: foreign key to `papers`.
- `reading_status`: controlled value such as `to_read`, `reading`, or `read`.
- `added_at`: timestamp.
- `personal_summary`: nullable user-authored text.

Constraints:

- A paper should appear at most once in a workspace unless a future product requirement explicitly supports multiple placements.
- Reading status must use documented values.
- User-authored content must remain separate from source metadata and AI-generated content.

### 4.12 Collection

Represents an optional named grouping of papers inside a workspace.

Proposed fields:

- `id`: UUID primary key.
- `workspace_id`: foreign key to `workspaces`.
- `name`: collection name.
- `description`: nullable description.
- `created_at`: timestamp.
- `updated_at`: timestamp.

### 4.13 CollectionPaper

Joins collections to papers.

Proposed fields:

- `collection_id`: foreign key to `collections`.
- `paper_id`: foreign key to `papers`.
- `added_at`: timestamp.

Constraints:

- Prevent duplicate membership in the same collection.
- Validate that collection ownership and workspace membership rules are consistent.

### 4.14 Note

Represents user-authored research notes.

Proposed fields:

- `id`: UUID primary key.
- `workspace_id`: foreign key to `workspaces`.
- `paper_id`: nullable foreign key to `papers`.
- `title`: nullable title.
- `body`: note text.
- `created_at`: timestamp.
- `updated_at`: timestamp.

If a note references a paper, verify that the paper is accessible within the user's workspace according to the product rules. Notes must not be silently overwritten by generated summaries.

### 4.15 EvidencePassage

Represents a passage that can support an answer or research claim, when lawful access and extraction are available.

Proposed fields:

- `id`: UUID primary key.
- `paper_id`: foreign key to `papers`.
- `source_type`: `abstract`, `open_access_full_text`, `user_provided_document`, or another documented type.
- `source_locator`: nullable section, page, paragraph, or character-offset information.
- `passage_text`: only when retention is permitted.
- `content_hash`: optional integrity identifier.
- `extraction_method`: nullable method or parser version.
- `created_at`: timestamp.

Rules:

- Record enough location information to return users to the source passage.
- A citation to a paper alone is not proof that a particular passage supports a claim.
- If full-text retention is not permitted, store permitted references or locators instead of the passage text.
- Do not expose private user-provided documents to other users.

### 4.16 ResearchQuestion

Represents a research question explored by a user.

Proposed fields:

- `id`: UUID primary key.
- `workspace_id`: foreign key to `workspaces`.
- `question_text`: question entered by the user.
- `status`: controlled state, initially `open`, `exploring`, or `resolved`.
- `created_at`: timestamp.
- `updated_at`: timestamp.

A question's status must not imply that a research problem is conclusively solved or that a novelty claim has been verified.

### 4.17 AIAnswer and AnswerEvidence

If AI-generated answers are persisted, store them separately from source records.

`AIAnswer` proposed fields:

- `id`: UUID primary key.
- `workspace_id`: foreign key to `workspaces`.
- `research_question_id`: nullable foreign key to `research_questions`.
- `question`: submitted question.
- `answer_text`: generated response.
- `model_provider`: provider name.
- `model_name`: model identifier.
- `prompt_version`: identifier for the prompt or workflow version.
- `created_at`: timestamp.

`AnswerEvidence` proposed fields:

- `id`: UUID primary key.
- `answer_id`: foreign key to `ai_answers`.
- `evidence_passage_id`: foreign key to `evidence_passages`, where available.
- `paper_id`: foreign key to `papers`.
- `supporting_quote`: nullable, only if permitted.
- `source_locator`: nullable locator.
- `relationship_to_claim`: controlled value such as `supports`, `contradicts`, or `context`.
- `created_at`: timestamp.

Every displayed source-backed claim must be traceable to the evidence actually retrieved for that answer. Do not imply that the existence of a linked paper proves every statement in the answer.

## 5. Relationship Summary

- One paper has many authors through `paper_authors`.
- One author can be associated with many papers.
- One paper can have many external identifiers and metadata snapshots.
- One paper can cite many other papers.
- A reference can remain unresolved until its target is identified.
- Papers can have non-citation relationships with explicit types and provenance.
- One user can own multiple workspaces.
- A workspace can save many papers and contain multiple collections, notes, and research questions.
- A collection can contain many papers.
- An AI answer can reference multiple evidence passages.
- Evidence provenance must be retained wherever it is needed to verify an answer.

## 6. Integrity and Validation Rules

1. Use foreign keys for relationships between relational entities.
2. Define uniqueness constraints for identifiers and join tables.
3. Index common search, filtering, and relationship traversal fields based on actual query patterns.
4. Add indexes for foreign keys where query performance warrants them.
5. Validate controlled status and relationship values at the API and database levels where practical.
6. Use UTC for stored timestamps; convert to the user's timezone at presentation boundaries.
7. Use transactions when a workflow creates or updates multiple related records.
8. Define deletion behavior explicitly for user data, notes, and workspace memberships.
9. Avoid cascade deletion of shared bibliographic records merely because a user deletes a workspace.
10. Treat provider metadata refreshes as updates with provenance, not as permission to erase user notes or annotations.
11. Define a retention policy for AI answers, evidence passages, and imported payloads before production.
12. Never store API keys, access tokens, passwords, or other secrets in bibliographic or provenance tables.

## 7. Search and Deduplication

The initial implementation should prioritize:

- Exact external-identifier matching.
- DOI normalization and validation.
- Provider-ID matching.
- Conservative title and author similarity as a candidate-generation mechanism only.
- Reviewable handling of ambiguous matches.
- Search indexes appropriate to the selected PostgreSQL search strategy.

Fuzzy matching may suggest that two records describe the same work, but it must not silently establish identity.

## 8. Privacy and Ownership

- All workspace-owned records must be authorized through their workspace and owner.
- Never trust a client-supplied `user_id` as proof of authorization.
- Enforce access checks in the backend, not only in the frontend.
- Keep private notes, uploaded documents, and workspace content private by default.
- Define export and deletion behavior for user-owned data.
- Keep public bibliographic metadata logically separate from private user data.

## 9. Migration Strategy

- Use Alembic migrations for schema changes.
- Review generated migrations before applying them.
- Do not modify an already-applied migration to change production schema history.
- Test migrations against a clean database and, where appropriate, an existing database snapshot.
- Update this document whenever an implemented schema materially differs from the design.
- Record major data-model decisions in `docs/DECISIONS.md`.

## 10. Decisions Still Required

Before implementation, decide and document:

1. Authentication provider and account-verification model.
2. Whether identifiers can belong to more entity types and the exact cross-provider identity policy.
3. What full-text content can be retained under provider and publisher terms.
4. The retention policy for AI answers and extracted evidence.
5. The final deduplication and merge-review strategy.
6. Which fields need full-text search, structured filtering, or vector retrieval.
7. Whether evidence passages are persisted or retrieved on demand in the initial release.

These decisions must be resolved before they become implicit assumptions in migrations or API behavior.

## 11. Acceptance Criteria

This data model is ready to guide implementation when:

- Each entity has a clear purpose and stable identity.
- Citation direction and unresolved references are unambiguous.
- Verified metadata, inferred relationships, and AI-generated content remain distinguishable.
- Workspace ownership and privacy rules are explicit.
- Constraints and deletion behavior can be implemented and tested.
- Metadata and evidence provenance are sufficient for auditing.
- Unresolved decisions are tracked rather than silently guessed.
