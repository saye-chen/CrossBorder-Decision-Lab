#!/usr/bin/env Rscript

# ECAE JSON-only adapter for clubSandwich CR2/Satterthwaite inference.
# Registry verification remains separate from adapter existence.

EXPECTED_PACKAGE_VERSION <- "0.7.0"
BACKEND_ID <- "cluster_inference"
CANDIDATE_ID <- "cluster_cr2_clubsandwich"

emit <- function(value) {
  cat(jsonlite::toJSON(value, auto_unbox = TRUE, null = "null", na = "null", digits = 16))
}

stop_ecae <- function(code, message, details = NULL) {
  condition <- structure(
    list(message = message, call = NULL, code = code, details = details),
    class = c("ecae_backend_error", "error", "condition")
  )
  stop(condition)
}

safe_name <- function(value, field) {
  if (!is.character(value) || length(value) != 1L || !grepl("^[A-Za-z][A-Za-z0-9_]*$", value)) {
    stop_ecae("BACKEND_COLUMN_INVALID", paste(field, "must be a safe column name"))
  }
  value
}

run_adapter <- function(request) {
  observed_version <- as.character(utils::packageVersion("clubSandwich"))
  if (!identical(observed_version, EXPECTED_PACKAGE_VERSION)) {
    stop_ecae("BACKEND_VERSION_MISMATCH", "clubSandwich version differs from adapter lock", list(expected = EXPECTED_PACKAGE_VERSION, observed = observed_version))
  }
  if (!is.list(request) || !is.data.frame(request$rows) || nrow(request$rows) < 4L) {
    stop_ecae("BACKEND_REQUEST_INVALID", "rows must decode to a data frame with at least four observations")
  }
  outcome <- safe_name(request$outcome_column, "outcome_column")
  treatment <- safe_name(request$treatment_column, "treatment_column")
  cluster <- safe_name(request$cluster_column, "cluster_column")
  covariates <- request$pretreatment_covariates
  if (is.null(covariates)) covariates <- character(0)
  if (!is.character(covariates) || any(!grepl("^[A-Za-z][A-Za-z0-9_]*$", covariates))) {
    stop_ecae("BACKEND_COLUMN_INVALID", "pretreatment_covariates must contain safe column names")
  }
  required_columns <- unique(c(outcome, treatment, cluster, covariates))
  missing_columns <- setdiff(required_columns, names(request$rows))
  if (length(missing_columns) > 0L) {
    stop_ecae("BACKEND_COLUMN_MISSING", "Required analysis columns are absent", as.list(missing_columns))
  }
  data <- request$rows
  if (!is.numeric(data[[outcome]]) || any(!is.finite(data[[outcome]]))) {
    stop_ecae("BACKEND_OUTCOME_INVALID", "Outcome must be finite numeric")
  }
  if (!is.numeric(data[[treatment]]) || !setequal(unique(data[[treatment]]), c(0, 1))) {
    stop_ecae("BACKEND_TREATMENT_INVALID", "Treatment must be numeric 0/1 with both arms observed")
  }
  cluster_ids <- as.character(data[[cluster]])
  if (any(is.na(cluster_ids)) || any(!nzchar(cluster_ids))) {
    stop_ecae("BACKEND_CLUSTER_INVALID", "Cluster ids must be non-missing and non-empty")
  }
  treatment_by_cluster <- split(data[[treatment]], cluster_ids)
  if (any(vapply(treatment_by_cluster, function(x) length(unique(x)) != 1L, logical(1)))) {
    stop_ecae("TREATMENT_VARIES_WITHIN_CLUSTER", "Treatment must be constant within randomized cluster")
  }
  cluster_arm <- vapply(treatment_by_cluster, function(x) x[[1]], numeric(1))
  counts_by_arm <- table(cluster_arm)
  if (length(counts_by_arm) != 2L || any(counts_by_arm < 2L)) {
    stop_ecae("INSUFFICIENT_CLUSTERS_PER_ARM", "Each arm needs at least two randomized clusters")
  }
  confidence_level <- request$confidence_level
  if (!is.numeric(confidence_level) || length(confidence_level) != 1L || !is.finite(confidence_level) || confidence_level <= 0 || confidence_level >= 1) {
    stop_ecae("BACKEND_CONFIDENCE_LEVEL_INVALID", "confidence_level must be in (0,1)")
  }
  null_value <- request$null_value
  if (is.null(null_value)) null_value <- 0
  if (!is.numeric(null_value) || length(null_value) != 1L || !is.finite(null_value)) {
    stop_ecae("BACKEND_NULL_INVALID", "null_value must be finite numeric")
  }
  terms <- c(treatment, covariates)
  formula <- stats::reformulate(terms, response = outcome)
  weights <- NULL
  if (!is.null(request$analysis_weight_column)) {
    weight_column <- safe_name(request$analysis_weight_column, "analysis_weight_column")
    if (!weight_column %in% names(data) || !is.numeric(data[[weight_column]]) || any(!is.finite(data[[weight_column]])) || any(data[[weight_column]] <= 0)) {
      stop_ecae("BACKEND_WEIGHT_INVALID", "Analysis weights must be finite and positive")
    }
    weights <- data[[weight_column]]
  }
  fit <- if (is.null(weights)) stats::lm(formula, data = data) else stats::lm(formula, data = data, weights = weights)
  if (fit$rank != ncol(stats::model.matrix(fit))) {
    stop_ecae("CLUSTER_DESIGN_SINGULAR", "Cluster analysis design matrix is rank deficient")
  }
  if (!treatment %in% names(stats::coef(fit))) {
    stop_ecae("BACKEND_TREATMENT_COEFFICIENT_MISSING", "Treatment coefficient is not identified")
  }
  vcov_cr2 <- clubSandwich::vcovCR(fit, cluster = cluster_ids, type = "CR2")
  test <- as.data.frame(clubSandwich::coef_test(fit, vcov = vcov_cr2, test = "Satterthwaite", null_constants = null_value))
  interval <- as.data.frame(clubSandwich::conf_int(fit, vcov = vcov_cr2, test = "Satterthwaite", level = confidence_level))
  row <- match(treatment, rownames(test))
  interval_row <- match(treatment, rownames(interval))
  if (is.na(row) || is.na(interval_row)) {
    stop_ecae("BACKEND_TREATMENT_COEFFICIENT_MISSING", "Treatment coefficient output is absent")
  }
  estimate <- unname(stats::coef(fit)[[treatment]])
  standard_error <- unname(test[row, "SE"])
  degrees_of_freedom <- unname(test[row, "df_Satt"])
  p_value <- unname(test[row, "p_Satt"])
  lower_name <- grep("^CI_L", names(interval), value = TRUE)[1]
  upper_name <- grep("^CI_U", names(interval), value = TRUE)[1]
  if (is.na(lower_name) || is.na(upper_name)) {
    stop_ecae("BACKEND_INTERVAL_INVALID", "Expected confidence interval columns are absent")
  }
  lower <- unname(interval[interval_row, lower_name])
  upper <- unname(interval[interval_row, upper_name])
  numeric_outputs <- c(estimate, standard_error, degrees_of_freedom, p_value, lower, upper)
  if (any(!is.finite(numeric_outputs)) || standard_error < 0 || degrees_of_freedom <= 0 || p_value < 0 || p_value > 1 || lower > upper) {
    stop_ecae("BACKEND_NUMERICAL_INVALID", "CR2/Satterthwaite output failed numerical invariants")
  }
  leverage <- tapply(stats::hatvalues(fit), cluster_ids, sum)
  warnings <- character(0)
  if (max(leverage) >= 0.5) warnings <- c(warnings, "cluster_leverage_at_least_0.5")
  list(
    effect = estimate,
    standard_error = standard_error,
    confidence_interval = list(level = confidence_level, lower = lower, upper = upper),
    p_value = p_value,
    null_value = null_value,
    degrees_of_freedom = degrees_of_freedom,
    variance_type = "CR2",
    test_type = "Satterthwaite",
    cluster_count = length(unique(cluster_ids)),
    clusters_per_arm = as.list(stats::setNames(as.integer(counts_by_arm), names(counts_by_arm))),
    cluster_leverage = list(maximum = max(leverage), by_cluster = as.list(leverage)),
    warnings = as.list(warnings)
  )
}

if (!requireNamespace("jsonlite", quietly = TRUE)) {
  stop("jsonlite is required before the adapter can emit a structured result")
}

input_text <- paste(readLines(file("stdin"), warn = FALSE), collapse = "\n")
response <- tryCatch(
  {
    request <- jsonlite::fromJSON(input_text, simplifyDataFrame = TRUE)
    result <- run_adapter(request)
    list(
      schema_version = "1.0.0",
      backend_id = BACKEND_ID,
      candidate_id = CANDIDATE_ID,
      package = "clubSandwich",
      version = EXPECTED_PACKAGE_VERSION,
      ok = TRUE,
      result = result,
      warnings = result$warnings,
      error = NULL
    )
  },
  ecae_backend_error = function(error) {
    list(
      schema_version = "1.0.0",
      backend_id = BACKEND_ID,
      candidate_id = CANDIDATE_ID,
      package = "clubSandwich",
      version = EXPECTED_PACKAGE_VERSION,
      ok = FALSE,
      result = NULL,
      warnings = list(),
      error = list(code = error$code, message = error$message, details = error$details)
    )
  },
  error = function(error) {
    list(
      schema_version = "1.0.0",
      backend_id = BACKEND_ID,
      candidate_id = CANDIDATE_ID,
      package = "clubSandwich",
      version = EXPECTED_PACKAGE_VERSION,
      ok = FALSE,
      result = NULL,
      warnings = list(),
      error = list(code = "BACKEND_INTERNAL_ERROR", message = conditionMessage(error), details = NULL)
    )
  }
)
emit(response)
