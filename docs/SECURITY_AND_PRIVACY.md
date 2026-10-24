# Research X — Security and Privacy

**Status:** Proposed design
**Product:** Research X
**Purpose:** Define security, authorization, privacy, secret management, and data-handling requirements before implementation.

## 1. Objectives

Research X must protect:

- User accounts and authentication credentials.
- Private workspaces, collections, and notes.
- Uploaded documents and extracted passages.
- Research questions and AI-generated answers.
- API keys and provider credentials.
- Database records and application infrastructure.
- The integrity and provenance of academic metadata.

Security and privacy are product requirements, not optional improvements to add after launch.

## 2. Security Principles

Follow these principles throughout development:

1. **Least privilege:** grant only the access necessary for a task.
2. **Deny by default:** resources remain inaccessible until authorization is established.
3. **Server-side enforcement:** the backend is the authority for authentication and authorization.
4. **Data minimization:** collect and retain only what the product needs.
5. **Secure defaults:** private user data is private unless an explicit, safe sharing feature is introduced.
6. **Defense in depth:** do not rely on a single control to protect sensitive resources.
7. **Auditable changes:** important security decisions and data-handling behavior should be documented and tested.
8. **No secrets in source control:** credentials must never be committed to the repository.

## 3. Data Classification

Classify application data according to its sensitivity.

### 3.1 Public bibliographic data

Examples:

- Paper titles and authors.
- Public abstracts where permitted.
- Public publication metadata.
- Public citation relationships.

Public availability does not automatically grant permission to redistribute or retain all content. Provider terms and applicable licences still apply.

### 3.2 Private user data

Examples:

- Workspace names and descriptions.
- Personal research notes.
- Saved-paper membership.
- Reading progress.
- Research questions.
- Private AI answers.

This data must be accessible only to the authenticated user and any explicitly authorized collaborators supported by a future sharing feature.

### 3.3 Restricted operational data

Examples:

- API keys.
- Database credentials.
- Authentication tokens.
- Session secrets.
- Internal configuration.
- Security logs containing sensitive diagnostic details.

Restrict access to authorized processes and operators. Never expose these values through public endpoints or frontend bundles.

### 3.4 User-provided documents

Uploaded documents may contain unpublished research, confidential material, personal information, or content subject to copyright.

Treat these documents as private by default. Apply explicit rules to storage, extraction, model processing, retention, and deletion.

## 4. Authentication

Authentication must be selected before implementing private workspace features.

Requirements:

- Use a maintained authentication library or provider.
- Verify authentication on the backend.
- Never trust a user ID supplied in a request as proof of identity.
- Store passwords only through a secure password-hashing mechanism if the application directly manages passwords.
- Never store plaintext passwords.
- Define session expiration, revocation, and sign-out behavior.
- Protect authentication flows against brute-force attempts and abuse.
- Keep authentication secrets outside source control.
- Avoid logging passwords, tokens, or session cookies.

The implementation must document the selected authentication method and its security properties.

Do not build a custom authentication system merely to avoid selecting an established provider.

## 5. Authorization and Workspace Isolation

Every private resource must be checked against the authenticated user's permissions.

For workspace-related requests:

1. Establish the authenticated identity.
2. Retrieve the requested workspace or resource.
3. Verify ownership or explicit authorized membership.
4. Apply the operation only after authorization succeeds.
5. Avoid leaking private resource contents through error messages.

Apply authorization to:

- Workspace reads and updates.
- Saved-paper membership.
- Collections.
- Notes.
- Research questions.
- Private answers.
- Uploaded documents.
- Evidence extracted from private documents.
- Any graph or comparison results that incorporate private content.

Do not rely on frontend route guards as a security boundary.

Test that one user cannot read, modify, or delete another user's resources by changing an identifier in a URL or request body.

## 6. API Security

The FastAPI backend must:

- Validate query parameters, path parameters, and request bodies.
- Enforce request-size and input-length limits.
- Use appropriate HTTP status codes.
- Return structured errors without stack traces or secrets.
- Apply rate limits to expensive or abuse-prone endpoints.
- Set appropriate CORS rules for the deployed frontend origins.
- Avoid accepting arbitrary cross-origin requests with credentials.
- Use secure transport in production.
- Apply timeouts to external requests.
- Avoid forwarding untrusted URLs to server-side fetch operations without validation.

CORS is a browser policy, not authentication or authorization. It must not be treated as the sole protection for an endpoint.

## 7. Secrets and Environment Configuration

Secrets must never be embedded in frontend code, committed to Git, or included in documentation examples as real credentials.

Examples include:

- AI-provider API keys.
- Metadata-provider API keys, where required.
- Database URLs containing credentials.
- Authentication secrets.
- Deployment credentials.

Requirements:

- Read local secrets from an untracked environment file or another appropriate local secret mechanism.
- Commit only a `.env.example` containing variable names and safe placeholders.
- Add local secret files to `.gitignore`.
- Validate required environment variables at application startup.
- Fail clearly when a required secret is missing.
- Never print secret values in logs or error responses.
- Use a suitable secret manager for production where available.
- Rotate a credential immediately if it is accidentally exposed.

If a real secret is committed, deleting it in a later commit is not sufficient. Treat it as exposed and rotate or revoke it.

## 8. Database Security

- Use parameterized queries through the ORM or another safe database interface.
- Do not construct SQL by concatenating untrusted user input.
- Use separate development and production database environments.
- Restrict database credentials to the minimum required permissions.
- Do not expose the database directly to public clients.
- Validate database migrations before applying them.
- Back up important production data and define recovery procedures.
- Apply retention and deletion policies to private user data.
- Avoid storing unnecessary sensitive information.
- Keep production database credentials out of local configuration examples.

Database-level row security may be considered where appropriate, but application-level authorization must remain explicit and tested. If both are used, their responsibilities must be documented.

## 9. External Providers and AI Services

Research X may use academic metadata providers, document services, and AI providers.

Before integration:

- Review relevant terms, licences, rate limits, and retention policies.
- Confirm which content may be retrieved, cached, displayed, and stored.
- Document whether user questions or documents are sent to external services.
- Avoid sending private content unless necessary and permitted.
- Keep provider credentials on the backend.
- Apply timeouts and controlled retries.
- Handle provider failures without exposing internal configuration.
- Record provider provenance where needed to interpret data correctly.

Never assume that an external service is private, free of retention, or authorized for all types of academic content. Verify the actual provider policy and selected account or service configuration.

## 10. Prompt Injection and Untrusted Documents

Research papers, abstracts, PDFs, web pages, and user-provided documents must be treated as untrusted input.

A document may contain instructions intended to manipulate the AI system.

Requirements:

- Treat retrieved document text as evidence to analyze, not as trusted system instructions.
- Separate trusted application instructions from untrusted source content.
- Never allow document text to authorize access to private data.
- Do not let retrieved instructions override security controls.
- Restrict AI tool access to explicitly permitted operations.
- Validate tool arguments and resource identifiers in backend code.
- Check authorization independently of the AI model.
- Render extracted text safely in the frontend.
- Test malicious instructions embedded in documents.

Prompt wording alone is not a sufficient defense. Enforce security decisions in application code.

## 11. File Uploads and Document Processing

If document uploads are implemented:

- Restrict allowed file types and sizes.
- Do not trust the filename or client-supplied content type.
- Validate file content before processing.
- Generate safe internal storage identifiers.
- Prevent uploaded files from being executed.
- Store files outside publicly served application directories unless public access is explicitly intended.
- Enforce access control when retrieving or deleting files.
- Apply processing timeouts and resource limits.
- Handle malformed, encrypted, scanned, or oversized documents safely.
- Consider malware scanning according to the deployment environment and risk.
- Avoid retaining extracted text longer than necessary.
- Define deletion behavior for the original file, extracted passages, and derived AI outputs.

Do not implement file uploads merely because they appear in the long-term product vision. Add them when the feature plan and permitted processing workflow are ready.

## 12. Copyright and Content Rights

Research X must distinguish access from permission to copy or redistribute.

Before storing or displaying full text, verify:

- The source and its terms.
- The applicable licence or permission.
- Whether storage is allowed.
- Whether excerpts may be displayed.
- Whether derivative processing is permitted.
- Whether content must be deleted after a defined period.

Where rights do not permit retaining full text, prefer permitted metadata, authorized links, or on-demand processing under an approved access model.

User-uploaded content must also be handled according to applicable rights and permissions. User possession of a document does not automatically authorize public redistribution.

## 13. Frontend Security

The React frontend must:

- Avoid embedding server-side secrets.
- Render untrusted text safely.
- Avoid unsafe HTML injection.
- Use secure authentication flows.
- Avoid placing sensitive information in URLs.
- Avoid logging private notes or document content to the browser console in production.
- Handle expired sessions safely.
- Display authorization failures without leaking private data.
- Keep dependencies reasonably current and review security advisories.

If rich text or Markdown rendering is introduced, configure it to prevent unsafe HTML and script execution.

## 14. Logging and Monitoring

Logs should help diagnose errors and security events while minimizing sensitive content.

Potential events include:

- Authentication failures.
- Authorization denials.
- Rate-limit events.
- Provider failures.
- Unexpected application errors.
- Administrative or security-sensitive changes.

Requirements:

- Never log passwords, API keys, access tokens, or session secrets.
- Avoid logging complete private documents or research notes by default.
- Minimize retention of user questions and AI responses in operational logs.
- Use request identifiers to correlate errors.
- Restrict log access.
- Document retention and deletion rules.
- Avoid returning internal stack traces to users.

Production monitoring should detect repeated authorization failures, abnormal request volume, and recurring external-provider errors where the deployment environment supports it.

## 15. Privacy and Data Retention

Before production, define:

- What personal information is collected.
- Why each category is needed.
- Where it is stored.
- Which external services receive it.
- How long it is retained.
- How users can export or delete their data.
- What happens to backups after deletion.
- Whether AI-generated outputs retain references to deleted source content.
- Whether any analytics or telemetry are collected.

Use data minimization. Do not collect additional personal information merely because it might be useful later.

Deleting a workspace should not accidentally delete shared bibliographic records needed by other users. Conversely, deleting private source material should trigger the documented cleanup or invalidation behavior for derived private content.

Applicable legal obligations and the final privacy notice must be reviewed before public launch.

## 16. Dependency and Supply-Chain Security

- Use supported package versions.
- Keep dependency declarations reproducible.
- Review dependency advisories.
- Remove unused packages.
- Avoid installing dependencies without a clear purpose.
- Use lockfiles where supported by the selected package manager.
- Review GitHub Actions and third-party automation permissions.
- Avoid granting CI workflows unnecessary repository or deployment access.
- Pin critical automation dependencies where appropriate.

Do not claim that an application is secure merely because a dependency scanner reports no known vulnerabilities.

## 17. Development and Deployment Safety

- Keep local development and production credentials separate.
- Never run destructive database commands against production as part of ordinary development.
- Review migrations before applying them.
- Protect production deployment credentials.
- Use HTTPS in production.
- Disable debug mode in production.
- Restrict administrative interfaces.
- Document backup and recovery procedures.
- Define how security issues are reported and addressed.
- Do not deploy unfinished authentication or authorization controls to public users.

Codex must inspect the repository and follow `AGENTS.md` before making changes. It must not remove security checks to make tests pass.

## 18. Security Testing

Tests must cover:

- Unauthenticated access to private endpoints.
- Cross-user workspace access.
- Unauthorized modification and deletion.
- Invalid or oversized request payloads.
- Injection attempts in search and filter inputs.
- Malicious document content and prompt injection.
- Secret leakage in API responses and logs.
- File upload validation, if implemented.
- CORS and session behavior.
- Rate limiting for expensive endpoints.
- External-provider failure handling.
- Correct handling of private content in AI workflows.

Use synthetic test data and mock external services where possible. Security tests should be deterministic and safe to run in development.

## 19. Initial Security Scope

Before the first public deployment, prioritize:

1. Secret management and a correct `.gitignore`.
2. Input validation and safe error handling.
3. Safe external-provider integration.
4. Authentication selection and implementation before private workspace features.
5. Backend authorization tests.
6. Database access controls.
7. Dependency and configuration review.
8. Privacy and content-retention decisions for AI features.
9. Deployment configuration review.
10. A documented process for rotating exposed credentials.

Do not postpone authorization until after private user features have been built.

## 20. Decisions Still Required

Before implementing affected features, decide:

1. Authentication provider and session model.
2. Exact data-retention and deletion policy.
3. AI-provider data handling and privacy configuration.
4. Academic metadata and full-text permissions.
5. File upload and storage architecture.
6. CORS origins and production deployment configuration.
7. Rate limits and abuse controls.
8. Logging and analytics policy.
9. Backup and recovery requirements.
10. The process for reporting and responding to security incidents.

Record significant decisions in `docs/DECISIONS.md`.

## 21. Acceptance Criteria

The security and privacy design is ready to guide implementation when:

- Authentication and authorization responsibilities are explicit.
- Private resources cannot be accessed through guessed or modified identifiers.
- Secrets remain outside source control and frontend bundles.
- Provider and AI integrations have defined data-handling rules.
- Untrusted documents cannot override application permissions.
- Copyright and retention constraints are considered in document processing.
- Errors and logs avoid unnecessary sensitive information.
- Security-sensitive behavior is covered by automated tests.
- Production deployment requirements are documented.
