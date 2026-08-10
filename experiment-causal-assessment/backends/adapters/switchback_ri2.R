#!/usr/bin/env Rscript

# ECAE JSON-only adapter for exact sharp-null switchback randomization inference.
# Serial dependence is handled through the registered sequence assignment space;
# carryover and periodicity diagnostics retain independent downgrade authority.

EXPECTED_PACKAGE_VERSION <- "0.5.0"
BACKEND_ID <- "switchback_inference"
CANDIDATE_ID <- "switchback_randomization_ri2"

emit <- function(value) cat(jsonlite::toJSON(value, auto_unbox = TRUE, null = "null", na = "null", digits = 16))

stop_ecae <- function(code, message, details = NULL) {
  stop(structure(list(message = message, call = NULL, code = code, details = details), class = c("ecae_backend_error", "error", "condition")))
}

finite_scalar <- function(value, field) {
  if (!is.numeric(value) || length(value) != 1L || !is.finite(value)) stop_ecae("BACKEND_REQUEST_INVALID", paste(field, "must be finite numeric"))
  as.numeric(value)
}

as_sequence_matrix <- function(value, period_count) {
  matrix_value <- if (is.matrix(value)) value else if (is.list(value) && length(value) > 0L) do.call(rbind, value) else NULL
  if (is.null(matrix_value) || !is.numeric(matrix_value) || ncol(matrix_value) != period_count || nrow(matrix_value) < 2L || any(!is.finite(matrix_value)) || any(!matrix_value %in% c(0, 1))) {
    stop_ecae("SEQUENCE_NOT_REGISTERED", "allowed_sequences must be at least two equal-length numeric 0/1 sequences")
  }
  storage.mode(matrix_value) <- "numeric"
  if (any(duplicated(as.data.frame(matrix_value)))) stop_ecae("SEQUENCE_NOT_REGISTERED", "allowed_sequences cannot contain duplicates")
  arm_counts <- rowSums(matrix_value)
  if (any(arm_counts == 0L | arm_counts == period_count)) stop_ecae("SEQUENCE_NOT_REGISTERED", "Every allowed sequence must contain both arms")
  if (any(apply(matrix_value, 1, function(sequence) all(diff(sequence) == 0)))) stop_ecae("NO_EFFECTIVE_SWITCHES", "Every allowed sequence must contain an effective switch")
  matrix_value
}

difference_in_means <- function(outcome, assignment) mean(outcome[assignment == 1]) - mean(outcome[assignment == 0])

run_adapter <- function(request) {
  observed_version <- as.character(utils::packageVersion("ri2"))
  if (!identical(observed_version, EXPECTED_PACKAGE_VERSION)) stop_ecae("BACKEND_VERSION_MISMATCH", "ri2 version differs from adapter lock", list(expected = EXPECTED_PACKAGE_VERSION, observed = observed_version))
  if (!is.list(request)) stop_ecae("BACKEND_REQUEST_INVALID", "Request must be a JSON object")
  if (!request$randomization_scheme %in% c("complete_sequence", "blocked_sequence", "custom_sequence")) stop_ecae("SEQUENCE_NOT_REGISTERED", "Unsupported randomization_scheme")

  period_id <- request$period_id
  observed <- request$observed_sequence
  arm <- request$arm
  outcome <- request$outcome
  washout <- request$washout_excluded
  period_count <- length(period_id)
  if (!is.character(period_id) || period_count < 4L || any(!nzchar(period_id)) || anyDuplicated(period_id)) stop_ecae("INVALID_PERIOD_ID", "period_id must contain at least four unique non-empty ids")
  if (!is.numeric(observed) || length(observed) != period_count || any(!observed %in% c(0, 1)) || length(unique(observed)) != 2L) stop_ecae("SEQUENCE_NOT_REGISTERED", "observed_sequence must be a two-arm numeric 0/1 sequence")
  if (!is.numeric(arm) || length(arm) != period_count || any(arm != observed)) stop_ecae("SEQUENCE_NOT_REGISTERED", "arm must exactly equal observed_sequence")
  if (!is.numeric(outcome) || length(outcome) != period_count || any(!is.finite(outcome))) stop_ecae("BACKEND_OUTCOME_INVALID", "outcome must contain one finite period aggregate per period")
  if (!is.logical(washout) || length(washout) != period_count || any(is.na(washout)) || any(!washout)) stop_ecae("WASHOUT_REINTRODUCED", "Every analyzed period must certify washout exclusion")
  for (field in c("period_start", "period_end")) {
    values <- request[[field]]
    if (!is.character(values) || length(values) != period_count || any(!nzchar(values))) stop_ecae("PERIOD_TIME_INVALID", paste(field, "must contain one non-empty timestamp per period"))
  }
  if (!identical(request$test_statistic, "difference_in_period_means")) stop_ecae("TEST_STATISTIC_UNSUPPORTED", "Only the preregistered difference_in_period_means statistic is supported")
  sharp_null <- finite_scalar(request$sharp_null, "sharp_null")
  if (sharp_null != 0) stop_ecae("SHARP_NULL_UNSUPPORTED", "Development adapter currently supports only the zero additive sharp null")

  allowed <- as_sequence_matrix(request$allowed_sequences, period_count)
  observed_matches <- which(apply(allowed, 1, function(sequence) identical(as.numeric(sequence), as.numeric(observed))))
  if (length(observed_matches) != 1L) stop_ecae("SEQUENCE_NOT_REGISTERED", "observed_sequence must occur exactly once in allowed_sequences")
  maximum <- request$maximum_enumerations
  if (is.null(maximum)) maximum <- 10000L
  if (!is.numeric(maximum) || length(maximum) != 1L || !is.finite(maximum) || maximum != floor(maximum) || maximum < 2 || maximum > 100000) stop_ecae("MAXIMUM_ENUMERATIONS_INVALID", "maximum_enumerations must be an integer from 2 through 100000")
  if (nrow(allowed) > maximum) stop_ecae("EXACT_ENUMERATION_LIMIT_EXCEEDED", "Sampling is blocked until a Monte Carlo p-value contract is separately verified", list(allowed_sequence_count = nrow(allowed), maximum_enumerations = maximum))
  if (!is.list(request$seed_contract) || !identical(request$seed_contract$mode, "exact_enumeration") || !is.null(request$seed_contract$seed)) stop_ecae("SEED_CONTRACT_INVALID", "Exact enumeration requires seed_contract mode exact_enumeration and null seed")

  marginal_probability <- colMeans(allowed)
  if (any(marginal_probability <= 0 | marginal_probability >= 1)) stop_ecae("ASSIGNMENT_PROBABILITY_INVALID", "Every period must have positive probability for both arms across allowed sequences")
  permutation_matrix <- t(allowed)
  data <- data.frame(period_id = period_id, outcome = outcome, arm = observed, stringsAsFactors = FALSE)
  inference <- ri2::conduct_ri(
    formula = outcome ~ arm,
    assignment = "arm",
    permutation_matrix = permutation_matrix,
    data = data,
    sims = ncol(permutation_matrix),
    sharp_hypothesis = sharp_null,
    progress_bar = FALSE,
    p = "two-tailed"
  )
  tidy <- ri2::tidy(inference)
  if (nrow(tidy) != 1L || !all(c("estimate", "p.value") %in% names(tidy))) stop_ecae("BACKEND_OUTPUT_INVALID", "ri2 returned an unexpected result shape")
  observed_statistic <- difference_in_means(outcome, observed)
  hand_statistics <- apply(allowed, 1, function(sequence) difference_in_means(outcome, sequence))
  hand_p_value <- mean(abs(hand_statistics) >= abs(observed_statistic) - 1e-12)
  backend_p_value <- as.numeric(tidy$p.value[[1]])
  if (!is.finite(backend_p_value) || abs(as.numeric(tidy$estimate[[1]]) - observed_statistic) > 1e-12 || abs(backend_p_value - hand_p_value) > 1e-12) {
    stop_ecae("RANDOMIZATION_PARITY_FAILED", "ri2 result differs from exhaustive hand enumeration", list(hand_p_value = hand_p_value, backend_p_value = backend_p_value))
  }
  periodicity_terms <- request$periodicity_terms
  if (is.null(periodicity_terms)) periodicity_terms <- character(0)
  lagged_terms <- request$lagged_treatment_terms
  if (is.null(lagged_terms)) lagged_terms <- character(0)
  if (!is.character(periodicity_terms) || any(!nzchar(periodicity_terms)) || !is.character(lagged_terms) || any(!nzchar(lagged_terms))) stop_ecae("BACKEND_REQUEST_INVALID", "Diagnostic term lists must contain non-empty strings")
  warnings <- c("sharp_null_p_value_only_no_average_effect_confidence_interval", "uniform_probability_over_registered_allowed_sequences")
  if (length(periodicity_terms) == 0L) warnings <- c(warnings, "periodicity_diagnostic_open")
  if (length(lagged_terms) == 0L) warnings <- c(warnings, "carryover_and_lag_sensitivity_open")
  list(
    observed_statistic = observed_statistic,
    estimand_label = "difference_in_period_means_under_zero_additive_sharp_null",
    randomization_p_value = backend_p_value,
    p_value_sidedness = "two_tailed_absolute_statistic",
    enumerated_or_sampled = "exact_enumeration",
    permutation_count = nrow(allowed),
    observed_sequence_probability = 1 / nrow(allowed),
    assignment_probabilities = list(treatment_by_period = as.list(marginal_probability), sequence_probability = 1 / nrow(allowed), probability_model = "uniform_over_registered_allowed_sequences"),
    seed_proof = list(mode = "exact_enumeration", seed = NULL, rng_used = FALSE),
    internal_hand_enumeration_parity = list(status = "pass", hand_p_value = hand_p_value, absolute_difference = abs(backend_p_value - hand_p_value)),
    lag_sensitivity = list(status = if (length(lagged_terms) > 0L) "terms_registered_not_estimated_by_primary_adapter" else "open", registered_terms = as.list(lagged_terms), downgrade_authority = TRUE),
    periodicity_diagnostic = list(status = if (length(periodicity_terms) > 0L) "terms_registered_not_estimated_by_primary_adapter" else "open", registered_terms = as.list(periodicity_terms), downgrade_authority = TRUE),
    serial_dependence_diagnostic = list(status = "handled_for_sharp_null_test_by_sequence_level_randomization_distribution", iid_period_standard_errors_used = FALSE, general_average_effect_interval_supported = FALSE),
    carryover_diagnostic = list(status = if (length(lagged_terms) > 0L) "external_sensitivity_required" else "open", downgrade_authority = TRUE),
    warnings = as.list(warnings)
  )
}

if (!requireNamespace("jsonlite", quietly = TRUE)) stop("jsonlite is required before the adapter can emit a structured result")
input_text <- paste(readLines(file("stdin"), warn = FALSE), collapse = "\n")
response <- tryCatch(
  {
    request <- jsonlite::fromJSON(input_text, simplifyDataFrame = TRUE)
    result <- run_adapter(request)
    list(schema_version = "1.0.0", backend_id = BACKEND_ID, candidate_id = CANDIDATE_ID, package = "ri2", version = EXPECTED_PACKAGE_VERSION, ok = TRUE, result = result, warnings = result$warnings, error = NULL)
  },
  ecae_backend_error = function(error) list(schema_version = "1.0.0", backend_id = BACKEND_ID, candidate_id = CANDIDATE_ID, package = "ri2", version = EXPECTED_PACKAGE_VERSION, ok = FALSE, result = NULL, warnings = list(), error = list(code = error$code, message = error$message, details = error$details)),
  error = function(error) list(schema_version = "1.0.0", backend_id = BACKEND_ID, candidate_id = CANDIDATE_ID, package = "ri2", version = EXPECTED_PACKAGE_VERSION, ok = FALSE, result = NULL, warnings = list(), error = list(code = "BACKEND_INTERNAL_ERROR", message = conditionMessage(error), details = NULL))
)
emit(response)
