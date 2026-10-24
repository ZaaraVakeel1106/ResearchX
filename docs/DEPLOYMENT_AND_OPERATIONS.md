# Deployment and Operations — Research X

## 1. Purpose

This document defines how Research X will be configured, deployed, monitored, maintained, and recovered.

The deployment approach should remain simple for the MVP. Avoid unnecessary infrastructure and operational complexity until actual requirements justify it.

This document describes the intended approach. It does not mean that deployment infrastructure or production operations have already been implemented.

## 2. Deployment Principles

- Keep local development reproducible.
- Separate development, testing, staging, and production environments where those environments are needed.
- Keep secrets out of source control.
- Use managed infrastructure where it meaningfully reduces operational work.
- Apply database changes through reviewed migrations.
- Use health checks and actionable logs.
- Make failures visible rather than silently returning fabricated results.
- Protect user workspaces, notes, and saved research.
- Respect research-provider usage terms, rate limits, and licensing restrictions.
- Prefer a straightforward deployment architecture over premature distributed systems.

## 3. Initial Deployment Architecture

The proposed MVP architecture consists of:

- **Frontend:** React, TypeScript, and Vite, built into static assets.
- **Backend:** Python and FastAPI, exposing the documented REST API.
- **Database:** PostgreSQL, preferably through a managed service when appropriate.
- **Research metadata:** An external research-data provider accessed through a backend integration adapter.
- **AI services:** A supported model provider accessed through a backend integration adapter.
- **Source control and automation:** GitHub and a CI workflow.

The frontend communicates with the backend. The backend handles research-provider requests, AI requests, authorization, business logic, and database access.

External provider credentials must never be embedded in frontend code.

The exact hosting provider, database provider, domain, and production topology remain decisions to finalize after validating cost, deployment requirements, and service terms.

## 4. Environment Separation

### Local Development

Purpose:

- Build features.
- Run tests.
- Debug application behavior.
- Use local configuration and isolated development data.

Requirements:

- A documented setup process.
- An environment file excluded from Git.
- A placeholder-only `.env.example`.
- Clear dependency installation commands.
- A local or designated development database.
- Mocked external services for ordinary tests where practical.

### Testing and Continuous Integration

Purpose:

- Validate code changes reproducibly.
- Run unit, integration, type-checking, linting, and build checks.
- Catch regressions before integration.

Requirements:

- Isolated test data.
- No dependency on personal credentials.
- No accidental access to production databases.
- Deterministic tests where practical.
- Explicit configuration for any optional live-provider smoke tests.

### Staging

A staging environment may be introduced when the application needs realistic pre-release verification.

It should resemble production sufficiently to test configuration, migrations, authentication, and integration behavior without exposing production user data unnecessarily.

### Production

Production must use separate credentials, configuration, and data from local development and testing.

Restrict access to operational systems and ensure that production configuration is reviewed before deployment.

## 5. Configuration and Secrets

Configuration values may eventually include:

- Database connection settings.
- Backend environment and logging level.
- Frontend API base URL.
- Research-provider API credentials, if required.
- AI-provider credentials, if required.
- Authentication and session settings.
- CORS allowed origins.
- Rate-limit settings.
- Request and processing timeouts.

The exact variable names must be defined in the implementation and reflected in `.env.example`.

Rules:

1. Commit placeholder values only.
2. Never commit real API keys, passwords, tokens, or private certificates.
3. Never expose backend-only secrets through frontend environment variables.
4. Validate mandatory configuration at startup.
5. Avoid printing complete connection strings or secrets in logs.
6. Rotate credentials if they are exposed.
7. Use the hosting platform's secret-management facility for production credentials.

The application must fail clearly when essential configuration is missing. Optional integrations should degrade gracefully when the product requirements allow it.

## 6. Database Operations

### Schema Management

- Use Alembic migrations for schema changes.
- Review migration scripts before deployment.
- Test migrations against an isolated PostgreSQL database.
- Keep migrations consistent with SQLAlchemy models and application schemas.
- Document changes that affect existing data or application compatibility.

### Deployment Order

For a database-changing release:

1. Review the migration and its compatibility implications.
2. Confirm a recovery plan exists.
3. Verify the target database and environment.
4. Take or confirm a suitable backup where appropriate.
5. Apply the reviewed migration.
6. Deploy the compatible application version.
7. Run health checks and essential smoke tests.
8. Confirm normal operation.

The precise order may differ for backward-compatible, multi-stage migrations. Do not deploy a migration blindly when it could break the currently running application.

### Data Protection

- Do not use production data for routine development.
- Restrict database access to required users and services.
- Use least-privilege database credentials.
- Avoid destructive schema changes without explicit review and a recovery plan.
- Define retention and deletion behavior before collecting significant personal data.

## 7. Backups and Recovery

Before the MVP stores important user-created research data, define a backup and recovery policy.

The policy should specify:

- Which database data is backed up.
- Backup frequency.
- Retention period.
- Backup storage and access controls.
- Recovery Point Objective (RPO): the acceptable amount of data loss measured in time.
- Recovery Time Objective (RTO): the acceptable time to restore service.
- Restoration verification procedure.
- Responsibility for initiating recovery.

A backup is not considered reliable until restoration has been tested.

Recovery procedures should account for workspace data, notes, saved papers, collections, and any other persistent user-created information.

Research metadata cached from external providers may be recoverable by refetching it, subject to provider availability and usage terms. User-created data must not be assumed to be recoverable from an external research provider.

Exact backup frequency, retention, RPO, and RTO remain open decisions based on the hosting service and the importance of stored data.

## 8. Application Health and Monitoring

### Health Checks

The backend should expose the documented health endpoint:

`GET /api/v1/health`

The response must follow `API_SPEC.md`.

The health check should establish that the application process is responding. Any deeper dependency checks must be designed carefully so that a temporary external provider failure does not necessarily make the entire application appear unavailable.

Readiness and liveness checks may be separated if the chosen hosting platform requires them.

### Operational Signals

Monitor, where supported:

- Request volume and latency.
- HTTP error rates.
- Backend exceptions.
- Database connection failures.
- External provider timeouts and rate limits.
- AI-provider failures and latency.
- Search success and empty-result rates.
- Evidence retrieval failures.
- Resource usage and deployment health.

Do not log private paper annotations, workspace notes, full prompts, document contents, credentials, or other sensitive payloads by default.

### Alerts

Introduce alerts for actionable issues, such as sustained application failures, elevated error rates, database unavailability, or exhausted provider quotas.

Alert thresholds should be based on observed behavior and operational requirements rather than arbitrary assumptions.

## 9. Logging and Error Handling

Logs should help diagnose failures without exposing private information.

Use consistent structured fields where practical:

- Timestamp.
- Severity.
- Request or correlation ID.
- Route or operation.
- Outcome.
- Duration.
- Sanitized error category.

Never record authentication secrets or full authorization headers.

Client-facing errors should follow the response format in `API_SPEC.md`. Internal diagnostics must not be returned to clients.

External provider failures must remain distinguishable from valid empty search results.

## 10. External Provider Reliability

Research metadata and AI services may fail independently of Research X.

For each integration:

- Set reasonable connection and request timeouts.
- Handle rate limits and retryable failures.
- Avoid unbounded retries.
- Use bounded retries with backoff where appropriate.
- Respect provider-specific retry instructions.
- Avoid duplicate side effects when retrying operations.
- Track provider errors and latency.
- Return actionable errors when a requested capability is unavailable.

Do not silently fabricate metadata or AI responses when a provider fails.

Caching, request coalescing, and circuit-breaking behavior may be introduced when justified by actual load and reliability requirements.

## 11. Deployment Pipeline

The intended deployment workflow is:

1. Changes are developed and reviewed in Git.
2. CI runs the configured quality checks.
3. The application build is verified.
4. Database migrations are reviewed when applicable.
5. A release is deployed to the intended environment.
6. Health checks and smoke tests run.
7. Errors and core workflows are monitored after release.

Production deployment must not depend on manually copying unreviewed source files to a server.

Automatic production deployment, deployment approvals, and rollback mechanisms will be selected when the hosting environment is finalized.

## 12. Rollback and Incident Handling

When a deployment causes a significant problem:

1. Identify the affected environment and scope.
2. Review recent deployments and error signals.
3. Stop further rollout if necessary.
4. Roll back the application version when safe.
5. Evaluate whether database changes are backward-compatible.
6. Restore data only through a reviewed recovery procedure.
7. Verify health checks and critical user workflows.
8. Record the cause and follow-up actions.

Do not assume rolling back application code automatically reverses a database migration.

For incidents involving exposed credentials or unauthorized access, secure the affected credentials and systems first, then investigate the scope and impact.

## 13. Cost Management

The MVP should avoid unnecessary recurring infrastructure costs.

Track costs that may arise from:

- Frontend and backend hosting.
- Managed database storage and compute.
- Research-provider API usage.
- AI model input and output tokens.
- Document storage and processing.
- Logging and monitoring.
- Backups and data transfer.

Use request limits, sensible timeouts, bounded result sizes, and controlled AI context sizes to avoid accidental excessive usage.

Before adopting a paid provider, verify its current pricing, free-tier restrictions, usage limits, and terms.

Do not assume that a free tier will remain available or be sufficient for production.

## 14. Copyright and Research Content

Operational behavior must respect the rights and terms governing research content.

- Store and display only content that the application is permitted to use.
- Preserve required attribution and source information.
- Distinguish metadata access from full-text access.
- Do not assume that publicly accessible content is unrestricted.
- Respect provider rate limits, caching rules, and redistribution restrictions.
- Keep any future document-storage policy consistent with applicable licenses and terms.

A deployment change must not bypass these restrictions.

## 15. Pre-Release Checklist

Before an MVP release, verify:

- [ ] Production configuration contains no placeholder secrets.
- [ ] Required environment variables are documented.
- [ ] The frontend points to the intended backend.
- [ ] CORS and authentication settings are appropriate.
- [ ] Database migrations have been reviewed and tested.
- [ ] A suitable backup and restoration plan exists.
- [ ] Health checks and logs work.
- [ ] Essential automated tests and builds pass.
- [ ] External provider failure paths have been tested.
- [ ] Rate limits and request-size limits are configured where needed.
- [ ] User data and evidence are handled according to documented privacy rules.
- [ ] No sensitive information is exposed in client errors or logs.
- [ ] A rollback or recovery procedure is documented.

## 16. Decisions to Finalize

- Frontend and backend hosting providers.
- Managed PostgreSQL provider and configuration.
- Production domain and HTTPS setup.
- Secret-management mechanism.
- Authentication and session deployment settings.
- Backup frequency, retention, RPO, and RTO.
- Monitoring and alerting tools.
- CI/CD and production approval policy.
- Deployment rollback strategy.
- Budget limits and provider usage thresholds.

Record significant choices in `DECISIONS.md` and update this document as the actual deployment design becomes known.
