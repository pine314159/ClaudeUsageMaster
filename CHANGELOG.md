# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-03-09

### Added

- Core questionnaire scoring pipeline: `questionnaire_adapter`, `dimension_scorer`, `rating_engine`.
- Fusion pipeline: `log_ingestor`, `log_analyzer`, `hooks_tracker`, `fusion_service`.
- Explainability layer: `explain_service`, unified explanation copy templates, and structured output fields.
- Reporting and CLI entrypoint: static HTML report generation and `rate run` one-command flow.
- Strategy configuration via `pydantic-settings` and `.env` (`.env.example` included).
- Regression assets: scenario fixtures and parameterized fixture regression tests.

### Changed

- Moved fusion thresholds and policy switches from code constants to environment-driven settings.
- Unified wording for rating descriptions, ceiling reasons, and conflict reasons.
- Expanded tests for rule boundaries, source fusion contracts, E2E flow, and fixture-driven scenarios.

### Known Limitations

- Log depth signal is still an activity proxy (`sample_size`, `coverage_days`) rather than fine-grained behavior features.
- Report is single-page static HTML without historical trend views.
- No interactive configuration UI; strategy tuning is `.env`-based.

### Next

- Plan and deliver the next-stage backlog (feature-level roadmap and compatibility guardrails).
