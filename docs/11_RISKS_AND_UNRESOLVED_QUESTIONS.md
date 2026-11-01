# StayWise AI — Risk Register & Unresolved Questions

## 1. Technical & Analytical Risk Register

| Risk ID | Risk Category | Description | Likelihood | Impact | Mitigation Strategy |
|---|---|---|---|---|---|
| **R-01** | Data Integrity | Re-opening source CSV files in Microsoft Excel could introduce additional scientific-notation corruption. | Medium | High | Maintain source dataset as read-only; perform all ETL strictly via programmatic Python loaders with explicit string typing. |
| **R-02** | Financial Framing | Stakeholders or AI mistakenly treating `Estimated Booking Value` (`adr * nights`) as actual realized revenue. | High | High | Enforce strict naming conventions across all schemas, APIs, and UI cards. Include automated disclaimer banners. |
| **R-03** | Analytical Paradox | Non-Refundable bookings show a **99.36% cancellation rate** (travel agency group tour blocks). Uninformed analysis could infer that non-refundable deposits cause cancellations. | High | Medium | Explicitly document this correlation vs causation nuance in KPI definitions, dashboard tooltips, and AI assistant system prompts. |
| **R-04** | Security / Prompt Injection | Adversarial user prompts in the AI assistant attempting to execute destructive SQL or exfiltrate database catalogs. | Medium | Critical | Implement multi-layer defense: SQLGlot AST validation rejecting non-SELECT statements, restricted read-only database user role, statement timeouts, and parameter limits. |
| **R-05** | SQL Dialect Incompatibility | LLM hallucinating MySQL or SQLite dialect syntax (e.g. `IFNULL`, backticks) instead of PostgreSQL standard syntax. | Medium | Medium | Provide comprehensive PostgreSQL schema context and SQLGlot transpilation/validation gate that catches dialect errors before execution. |
| **R-06** | Outlier Distortion | A single booking with ADR = $5,400.00 skews average ADR calculations in City Hotel March 2016. | Low | Low | Expose both Mean ADR and Median ADR in analytics services; support optional outlier filtering flags in API endpoints. |
| **R-07** | Local Environment Divergence | Differences in local PostgreSQL installations (Windows service vs Docker) causing connection issues. | Medium | Medium | Provide both native Windows `.env` configuration and optional Docker Compose specifications in Phase 2. |

---

## 2. Unresolved Questions & Clarifications for User Approval

Before initiating Phase 2, we request user confirmation on the following implementation preferences:

1. **PostgreSQL Deployment Method**:
   - Would you prefer connecting to an already installed local PostgreSQL instance on Windows (e.g., standard `localhost:5432`), or would you prefer a `docker-compose.yml` configuration to spin up the database container automatically?
2. **OpenAI Model Preference**:
   - Do you have a preference between `gpt-4o-mini` (fast, economical, highly proficient at SQL) or `gpt-4o` (maximum reasoning capacity) as the default model for the LangGraph assistant?
3. **LangSmith Integration**:
   - Do you plan to provide a `LANGSMITH_API_KEY` for active tracing during development, or should the platform be configured to operate smoothly with LangSmith in dormant mode when the key is omitted?
4. **Extreme ADR Outlier Handling**:
   - For the single reservation with ADR = $5,400.00 (`75ac1e61`), our recommendation is to preserve the exact raw value in the database, but report Median ADR alongside Mean ADR in the dashboard and analytics layer to maintain historical integrity without skewing operational decisions. Does this approach align with your expectations?
