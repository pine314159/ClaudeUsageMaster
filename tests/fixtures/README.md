# Scenario Fixtures

These fixture files provide stable, reusable scenario inputs for regression tests.

## File Format

Each `*.json` file contains:

- `case_id`: unique scenario id
- `questionnaire`: full questionnaire payload (`q1..q22`, `q10_depth`)
- `fusion`: source-fusion inputs (`sample_size`, `coverage_days`)
- `expected`: range- or keyword-based assertions

## Scenario Set

- `high_score.json`: high score with high-confidence logs
- `median_neutral.json`: neutral median user with no logs
- `conflict_high_conf.json`: conflict with high-confidence logs (full penalty)
- `conflict_low_conf.json`: conflict with low-confidence logs (half penalty + cap)

