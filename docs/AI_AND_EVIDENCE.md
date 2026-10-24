# Research X — AI and Evidence Design

**Status:** Proposed design
**Product:** Research X
**Purpose:** Define how AI assists with research while preserving source traceability, uncertainty, and academic integrity.

## 1. Objective

Research X should help users understand academic literature, not merely generate summaries.

The AI system should help users:

- Understand a paper's research question, methods, results, and limitations.
- Ask questions about a paper and receive evidence-backed answers.
- Find relevant passages without manually scanning every page.
- Compare approaches across multiple papers.
- Trace claims back to sources.
- Identify disagreements, missing evidence, and unresolved questions.
- Explore possible research directions without making unsupported novelty claims.

The core principle is:

**Evidence before confidence.**

A fluent answer is not necessarily a correct answer. The system must prioritize traceability and honest uncertainty over sounding confident.

## 2. AI System Principles

### 2.1 Source-grounded answers

Factual claims about a paper must be grounded in retrieved source material.

The system must distinguish:

- What the paper explicitly states.
- What the available evidence supports indirectly.
- What the AI infers from the evidence.
- What remains unknown.

### 2.2 No fabricated evidence

The AI must never invent:

- Paper titles or authors.
- Citations or DOIs.
- Quotations.
- Page or section locations.
- Experimental results.
- Methodological details.
- Research limitations.
- Claims that a paper supports a particular conclusion.

When evidence is missing, the answer must say so.

### 2.3 Evidence is claim-specific

A paper may be relevant to a topic without supporting every claim made in an answer.

Research X should associate important claims with the passages or source records that actually support them.

A citation to a whole paper is not automatically sufficient evidence for a specific factual statement.

### 2.4 Preserve the distinction between fact and inference

The system must not present its own interpretation as a statement made by the authors.

Use clear wording such as:

- "The authors report..."
- "The retrieved passage states..."
- "This suggests..."
- "A possible interpretation is..."
- "The available sources do not establish..."

Use these distinctions where relevant, not as repetitive disclaimers on every sentence.

## 3. Evidence Sources

Potential evidence sources include:

1. Bibliographic metadata.
2. Abstracts retrieved from an authorized provider.
3. Lawfully accessible full text.
4. User-provided documents the user is authorized to use.
5. Specific passages retrieved from permitted documents.
6. Additional academic sources retrieved for a cross-paper question.

Every evidence source should have a known origin.

The implementation must verify provider terms, licensing, access conditions, and retention permissions before storing or displaying source content.

Do not assume that a publicly accessible PDF can automatically be copied, retained, or redistributed.

## 4. Evidence Provenance

Each evidence item should retain sufficient information to identify its source and retrieve the relevant location.

Proposed fields:

- `paper_id`: canonical paper identifier, when available.
- `source_type`: abstract, permitted full text, user-provided document, or another documented source.
- `provider`: source provider, when applicable.
- `source_url`: permitted source or landing-page URL.
- `retrieved_at`: retrieval timestamp.
- `locator`: page, section, paragraph, or character range where available.
- `content_hash`: optional integrity identifier.
- `extraction_method`: parser or extraction method.
- `extraction_version`: version used, where relevant.
- `retention_policy`: applicable handling policy or reference.

The final schema must align with `docs/DATA_MODEL.md`.

If the application cannot preserve passage text lawfully, it should retain only permitted metadata and locators, or retrieve the passage on demand where access permits.

## 5. Retrieval-Augmented Generation

Use a retrieval-augmented generation (RAG) workflow for evidence-based questions.

Proposed workflow:

1. Validate the user's question and authorization context.
2. Identify the paper or permitted set of sources.
3. Retrieve available evidence from the authorized source.
4. Normalize and rank relevant passages.
5. Check that each passage belongs to the intended source.
6. Construct a bounded prompt containing the question and retrieved evidence.
7. Ask the configured model to answer using that evidence.
8. Require the model to associate substantive claims with evidence identifiers.
9. Validate the response structure and evidence references.
10. Return the answer, evidence, and limitations to the frontend.
11. Record appropriate provenance and diagnostic information without unnecessarily retaining private content.

This is a proposed pipeline. Implement it incrementally and test each stage independently.

### 5.1 Retrieval must precede generation

Do not let the model invent its own supporting sources.

The model should receive evidence retrieved by the application. The application must verify that any returned evidence identifiers refer to items actually provided to the model.

### 5.2 Bounded context

Do not send an entire large document to the model by default.

Retrieve a manageable set of relevant passages, preserve source locators, and respect the context limits of the configured model.

### 5.3 Retrieval limitations

Retrieval can miss relevant passages because of poor text extraction, incomplete source access, chunk boundaries, terminology differences, or ranking errors.

The answer system must not interpret a failed retrieval as proof that the paper does not discuss a topic.

## 6. Evidence Chunking and Retrieval

When permitted document text is available, divide it into passages suitable for retrieval.

The initial strategy should prioritize:

- Preserving section headings.
- Keeping paragraphs and meaningful structural units intact.
- Avoiding chunks that split important definitions or results unnecessarily.
- Retaining page or section locators.
- Recording extraction errors.
- Deduplicating overlapping passages where appropriate.

Chunk size and overlap must be selected through evaluation rather than arbitrary assumptions.

If a PDF is scanned, extraction may require OCR. OCR-derived evidence must be treated as potentially error-prone, especially for equations, tables, symbols, and mathematical notation.

Do not silently present unreadable or incorrectly extracted content as reliable evidence.

## 7. Answer Structure

Use a structured internal response rather than accepting arbitrary model prose as the complete application result.

Proposed conceptual structure:

- `answer`: user-facing response.
- `claims`: important factual claims, when claim-level traceability is supported.
- `evidence`: retrieved source passages associated with claims.
- `limitations`: relevant gaps or uncertainty.
- `answer_status`: answered, partially answered, or insufficient evidence.
- `model_metadata`: internal operational metadata where appropriate.

This is a design proposal. The final API schema belongs in `docs/API_SPEC.md`.

### 7.1 Answer statuses

Use clearly defined statuses:

- `answered`: sufficient relevant evidence was retrieved for the requested answer.
- `partially_answered`: some parts are supported, but important parts remain unresolved.
- `insufficient_evidence`: the available evidence cannot responsibly answer the question.

These statuses should be assigned through explicit application logic and validation rules, not solely by trusting a model's self-assessment.

### 7.2 Evidence relationships

Each displayed evidence item should indicate its relationship to the claim when feasible:

- `supports`
- `contradicts`
- `context`

Do not label a passage as supporting a claim unless the relationship has been checked sufficiently for the feature's stated reliability level.

## 8. Insufficient Evidence Behavior

When evidence is insufficient, Research X must not force a complete-sounding answer.

It should:

1. State what could not be established.
2. Explain the relevant limitation briefly.
3. Distinguish missing evidence from evidence of absence.
4. Offer a useful next step when appropriate.

Examples of appropriate behavior:

- "The available abstract does not specify the dataset size."
- "I could not verify the exact page because the accessible text lacks page-level information."
- "The retrieved passages do not establish whether the method outperforms the baseline."
- "I found evidence about the proposed method, but not enough to compare its performance across both papers."

These are illustrative examples, not claims about any particular paper.

## 9. Paper Understanding

The reader may provide structured explanations of a paper, such as:

- Research problem.
- Motivation.
- Main contribution.
- Proposed method.
- Experimental setup.
- Dataset.
- Baselines.
- Reported results.
- Limitations stated by the authors.
- Future work stated by the authors.

Each field must be marked unavailable if the relevant information cannot be established.

The system must distinguish author-reported limitations from limitations inferred by the AI.

When reporting numerical results, preserve the metric, unit, dataset, experimental conditions, and baseline context where available. Avoid comparing numbers that were measured under incompatible conditions.

## 10. Cross-Paper Comparison

Cross-paper comparison should use evidence from each selected paper.

Potential comparison dimensions include:

- Research objective.
- Methodology.
- Dataset.
- Evaluation metrics.
- Baselines.
- Reported results.
- Assumptions.
- Limitations.
- Computational requirements, when reported.

Requirements:

- Identify which paper supports each substantive comparison.
- Preserve differences in experimental setup.
- Do not treat unreported values as zero.
- Do not claim one method is superior without comparable evidence.
- Explicitly mark missing or incompatible information.
- Distinguish author-reported conclusions from the system's synthesis.

The application should prefer a structured comparison table before generating a broad narrative.

## 11. Research Gaps and Novelty Exploration

Research X may help users investigate possible gaps in a literature area, but it must not guarantee novelty.

A responsible workflow should:

1. Define the research question and scope.
2. Retrieve relevant literature.
3. Explain the sources and search coverage used.
4. Group relevant work by method, problem, dataset, or another meaningful dimension.
5. Identify patterns, disagreements, limitations, and underexplored combinations.
6. Present candidate gaps as hypotheses.
7. Provide the evidence and counterexamples a researcher should inspect.
8. Recommend further searches before any novelty conclusion.

Use wording such as:

- "Potential gap suggested by the retrieved literature."
- "This area appears less represented in the sources examined."
- "Further searching is needed before concluding that this is novel."

Avoid absolute claims such as "No one has researched this before" unless the claim can genuinely be established, which is generally difficult.

A lack of retrieved papers is not proof that no relevant work exists.

## 12. AI-Generated Graph Relationships

If AI is used to infer that one paper extends, challenges, replicates, or applies another, the inference must be handled separately from bibliographic facts.

Requirements:

- Keep the relationship explicitly marked as inferred.
- Preserve the evidence used.
- Record the model or method version where appropriate.
- Avoid generating edges from title similarity alone when the relationship implies a substantive scholarly claim.
- Permit contradictory evidence.
- Do not treat a model confidence score as a calibrated probability unless validated.
- Make uncertain relationships easy to inspect or dismiss.

Consider deferring these edges until reliable evidence retrieval and evaluation are available.

## 13. Prompt and Model Management

- Keep prompts in version-controlled source files.
- Assign explicit prompt versions.
- Validate model outputs against structured schemas.
- Treat retrieved documents and user-provided text as untrusted data, not as system instructions.
- Instruct models to ignore instructions embedded in source documents that attempt to override application behavior.
- Never include secrets in prompts.
- Keep model-specific behavior behind a backend adapter.
- Avoid unnecessary coupling between application logic and a single model provider.

Model-provider changes must not silently alter the meaning of evidence or citation fields.

## 14. Security and Prompt Injection

Research documents, abstracts, uploaded files, and retrieved passages may contain malicious or irrelevant instructions.

The AI pipeline must:

- Treat all retrieved content as data to analyze, not trusted instructions.
- Separate system instructions from source content.
- Restrict model tools and permissions.
- Never let document text authorize access to private resources.
- Never allow a retrieved instruction to reveal secrets or override access controls.
- Validate every tool call and resource reference in application code.
- Escape or safely render untrusted text in the frontend.
- Apply the same authorization checks whether a request originates from the UI or an AI-assisted workflow.

Prompt instructions alone are not a sufficient security boundary. Enforce permissions and validation in ordinary backend code.

## 15. Privacy and Data Retention

- Do not send private documents to an external model provider unless the configured integration and user-facing policy permit it.
- Minimize the personal or private content sent to the model.
- Document what the selected provider retains and how its data controls apply.
- Keep workspace notes and user-uploaded content private by default.
- Avoid logging full questions, passages, or answers unless there is a defined and justified need.
- Establish retention and deletion behavior for stored answers and evidence.
- Never place credentials or API keys in frontend code or browser-delivered configuration.
- Provide clear disclosure when external AI processing is used.

Final privacy behavior must be consistent with `docs/SECURITY_AND_PRIVACY.md`.

## 16. Evaluation Strategy

Evaluate the AI system with a small, version-controlled test dataset before relying on it for substantive research workflows.

The dataset should include questions whose answers can be checked against known source passages.

Evaluate at least:

### Retrieval quality
- Whether relevant passages are retrieved.
- Whether important supporting passages are missed.
- Whether source locators are correct.
- Whether retrieved passages are from the intended paper.

### Answer quality
- Factual correctness against the source.
- Evidence coverage for substantive claims.
- Citation and passage correctness.
- Correct handling of conflicting evidence.
- Correct abstention when evidence is insufficient.
- Preservation of numerical and methodological context.

### Safety and robustness
- Prompt-injection attempts inside retrieved documents.
- Unsupported user assumptions.
- Malformed model output.
- Provider timeouts and rate limits.
- Missing or inaccessible full text.
- OCR and parsing errors.
- Cross-workspace access attempts.

Prefer repeatable evaluation cases over subjective judgments that an answer merely sounds convincing.

## 17. Testing Requirements

Automated tests must cover:

- Valid and invalid structured model responses.
- Evidence IDs not present in the retrieved context.
- Fabricated or malformed source locators.
- Insufficient-evidence behavior.
- Partial-answer behavior.
- Conflicting evidence.
- Missing abstracts and full text.
- Provider failures.
- Prompt-injection content in documents.
- User authorization and private document access.
- Correct association between claims and evidence.
- Copyright-aware passage retention and display rules.
- Logging that excludes secrets and unnecessary private content.

Mock model calls in unit tests. Keep tests deterministic and do not require paid external model calls in the normal test suite.

## 18. Initial Implementation Scope

Implement AI in stages.

### Stage 1: Evidence-safe foundation

- Create the backend model-provider interface.
- Define request and response schemas.
- Add a mocked provider for tests.
- Implement source metadata and evidence references.
- Return an explicit insufficient-evidence response when usable evidence is unavailable.

### Stage 2: Single-paper questions

- Retrieve authorized abstract or permitted text.
- Implement bounded passage retrieval.
- Generate structured answers.
- Validate evidence references.
- Display source links and available locators.

### Stage 3: Paper comparison

- Retrieve evidence from each selected paper.
- Generate structured comparisons.
- Track which source supports each comparison point.
- Handle incomplete and incompatible evidence.

### Stage 4: Broader research exploration

- Add multi-paper synthesis.
- Evaluate disagreement detection.
- Explore candidate research gaps.
- Consider inferred graph relationships only after evidence and evaluation are reliable.

The feature plan may adjust the order, but later stages must not be treated as prerequisites for a working, tested initial application.

## 19. Decisions Still Required

Before implementation, decide:

1. Which AI provider will be used initially.
2. Which model is suitable for the expected budget and workload.
3. Which metadata and full-text sources may legally be used.
4. How text extraction and OCR will work.
5. The retrieval strategy and chunking configuration.
6. Which answer fields are mandatory.
7. How claim-level evidence association will be represented.
8. Which content is persisted and for how long.
9. Which model-evaluation dataset and acceptance thresholds will be used.
10. Which AI capabilities are included in the first release.

Record material choices in `docs/DECISIONS.md`. Keep unresolved choices explicit rather than inventing credentials, access permissions, or provider capabilities.

## 20. Acceptance Criteria

The AI and evidence design is ready to guide implementation when:

- Answers are grounded in retrieved evidence.
- Evidence links resolve to the correct source.
- Unsupported claims are not presented as established facts.
- Missing evidence leads to transparent limitations.
- Author statements and AI interpretations remain distinct.
- Cross-paper comparisons preserve experimental context.
- Research gaps are presented as hypotheses.
- Prompt injection and private-data access are addressed.
- Copyright and provider restrictions shape retrieval and retention.
- Evaluation tests measure correctness and evidence quality, not fluency alone.
