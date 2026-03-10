# Rule Consistency Checklist

This checklist maps acceptance requirements to executable tests.

## Rating Tier Consistency

- [x] Tier boundaries use `>= cutoff` with no gaps.
  - Test: `tests/test_rating_engine.py::test_score_to_rating_boundaries_have_no_gaps`
- [x] Rating output stays within allowed grades.
  - Tests: `tests/test_rating_engine.py::test_evaluate_output_shape`, `tests/test_cli_run.py::test_cli_run_writes_result_and_report`

## Ceiling Rule Consistency

- [x] Ceiling rules enforce maximum allowed scores when triggered.
  - Tests: `tests/test_rating_engine.py::test_apply_ceiling_hits_d1_rule`, `tests/test_rating_engine.py::test_apply_ceiling_respects_rule_caps`
- [x] Ceiling hit details are preserved for explainability.
  - Test: `tests/test_explain_service.py::test_assemble_result_adds_contextual_suggestions`

## Source Fusion Contract

- [x] Output contains `source_breakdown`, `confidence`, `conflict_adjustment`.
  - Tests: `tests/test_cli_run.py::test_cli_run_writes_result_and_report`, `tests/test_fusion_service.py`
- [x] No-log scenario uses neutral correction and `no_data` conflict tier.
  - Test: `tests/test_e2e_regression.py::test_e2e_run_without_logs_has_neutral_corrections`

## End-to-End Regression

- [x] Single CLI run writes rating JSON and HTML report.
  - Test: `tests/test_cli_run.py::test_cli_run_writes_result_and_report`
- [x] Repeated CLI runs append history entries.
  - Test: `tests/test_e2e_regression.py::test_e2e_history_appends_on_repeated_runs`
