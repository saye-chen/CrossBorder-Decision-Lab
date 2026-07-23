# Shared Statistical Primitive Contract

Contract version: `CBSTAT-2026.01`

This repository uses formula parity rather than a shared runtime dependency. Each Skill remains independently installable and keeps a local implementation, while the repository gate verifies common definitions against identical fixtures.

## Normative definitions

- `mean`: arithmetic mean of finite numeric observations.
- `variance`: unbiased sample variance with denominator `n-1`; at least two observations.
- `covariance`: aligned sample covariance with denominator `n-1`.
- `ols`: simple linear regression with intercept; slope is covariance divided by predictor variance; slope standard error uses residual degrees of freedom `n-2`.
- `project_simplex`: Euclidean projection onto non-negative weights summing to one.
- Invalid, non-finite, unaligned or underidentified inputs fail closed.

## Ownership and change control

- AAMO owns advertising assignment, incrementality and media-response conclusions.
- MBCM owns market, brand, campaign and portfolio conclusions.
- Neither domain imports the other domain at runtime.
- A formula change requires: contract version change, both local implementations, parity fixtures, domain-specific tests and change-impact review.
- Parity does not establish causal identification. Every estimator must still report its estimand, assumptions, diagnostics, uncertainty and action limit.
