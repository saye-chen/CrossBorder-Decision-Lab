#!/usr/bin/env Rscript

# ECAE JSON-only adapter for canonical efficacy and beta-spending designs.
# Backend verification remains separate from adapter existence.

EXPECTED_PACKAGE_VERSION <- "3.10.1"
BACKEND_ID <- "group_sequential"
CANDIDATE_ID <- "group_sequential_gsdesign"

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

finite_scalar <- function(value, field) {
  if (!is.numeric(value) || length(value) != 1L || !is.finite(value)) {
    stop_ecae("BACKEND_REQUEST_INVALID", paste(field, "must be finite numeric"))
  }
  as.numeric(value)
}

run_adapter <- function(request) {
  observed_version <- as.character(utils::packageVersion("gsDesign"))
  if (!identical(observed_version, EXPECTED_PACKAGE_VERSION)) {
    stop_ecae("BACKEND_VERSION_MISMATCH", "gsDesign version differs from adapter lock", list(expected = EXPECTED_PACKAGE_VERSION, observed = observed_version))
  }
  if (!is.list(request)) stop_ecae("BACKEND_REQUEST_INVALID", "Request must be a JSON object")

  sided <- finite_scalar(request$sided, "sided")
  if (!sided %in% c(1, 2)) stop_ecae("SEQUENTIAL_SIDEDNESS_INVALID", "sided must equal 1 or 2")
  alpha_total <- finite_scalar(request$alpha, "alpha")
  power <- finite_scalar(request$power, "power")
  if (alpha_total <= 0 || alpha_total >= 1 || power <= 0 || power >= 1) {
    stop_ecae("ALPHA_SPENDING_INVALID", "alpha and power must be in (0,1)")
  }
  information <- request$information_fractions
  if (!is.numeric(information) || length(information) < 1L || any(!is.finite(information)) || any(information <= 0) || any(information > 1) || any(diff(information) <= 0) || abs(tail(information, 1) - 1) > 1e-12) {
    stop_ecae("INFORMATION_FRACTION_INVALID", "information_fractions must strictly increase in (0,1] and end at one")
  }
  if (!is.character(request$effect_scale) || length(request$effect_scale) != 1L || request$effect_scale != "z_statistic") {
    stop_ecae("BOUNDARY_SCALE_MISMATCH", "This adapter supports only z_statistic boundaries")
  }
  if (!is.logical(request$futility_binding) || length(request$futility_binding) != 1L || is.na(request$futility_binding)) {
    stop_ecae("SEQUENTIAL_FUTILITY_INVALID", "futility_binding must be boolean")
  }
  futility_enabled <- !is.null(request$futility_spending)
  if (futility_enabled && sided != 1) stop_ecae("SEQUENTIAL_FUTILITY_INVALID", "Beta-spending futility currently requires a one-sided efficacy design")
  if (!is.null(request$direction_upper) && !identical(request$direction_upper, TRUE)) {
    stop_ecae("SEQUENTIAL_DIRECTION_UNSUPPORTED", "One-sided lower-direction designs are not yet supported")
  }

  spending <- request$efficacy_spending
  if (!is.character(spending) || length(spending) != 1L || !spending %in% c("obrien_fleming", "pocock", "hwang_shih_decani", "user_supplied")) {
    stop_ecae("ALPHA_SPENDING_INVALID", "Unknown efficacy_spending family")
  }
  alpha_per_upper_tail <- if (sided == 1) alpha_total else alpha_total / 2
  spending_function <- switch(
    spending,
    obrien_fleming = gsDesign::sfLDOF,
    pocock = gsDesign::sfLDPocock,
    hwang_shih_decani = gsDesign::sfHSD,
    user_supplied = gsDesign::sfPoints
  )
  spending_parameter <- NULL
  if (spending == "hwang_shih_decani") {
    gamma <- finite_scalar(request$spending_parameters$gamma, "spending_parameters.gamma")
    if (gamma < -40 || gamma > 40) stop_ecae("ALPHA_SPENDING_INVALID", "HSD gamma must be in [-40,40]")
    spending_parameter <- gamma
  }
  if (spending == "user_supplied") {
    cumulative <- request$spending_parameters$user_cumulative_alpha_spending
    if (!is.numeric(cumulative) || length(cumulative) != length(information) || any(!is.finite(cumulative)) || any(cumulative < 0) || any(diff(cumulative) < 0) || abs(tail(cumulative, 1) - alpha_total) > 1e-12) {
      stop_ecae("ALPHA_SPENDING_INVALID", "User cumulative alpha spending must be nondecreasing, match all looks, and end at total alpha")
    }
    spending_parameter <- cumulative / alpha_total
  }

  futility_function <- NULL
  futility_parameter <- NULL
  if (futility_enabled) {
    futility_spending <- request$futility_spending
    if (!is.character(futility_spending) || length(futility_spending) != 1L || !futility_spending %in% c("obrien_fleming", "pocock", "hwang_shih_decani", "user_supplied")) {
      stop_ecae("SEQUENTIAL_FUTILITY_INVALID", "Unknown futility_spending family")
    }
    futility_function <- switch(
      futility_spending,
      obrien_fleming = gsDesign::sfLDOF,
      pocock = gsDesign::sfLDPocock,
      hwang_shih_decani = gsDesign::sfHSD,
      user_supplied = gsDesign::sfPoints
    )
    if (futility_spending == "hwang_shih_decani") {
      futility_parameter <- finite_scalar(request$futility_parameters$gamma, "futility_parameters.gamma")
      if (futility_parameter < -40 || futility_parameter > 40) stop_ecae("SEQUENTIAL_FUTILITY_INVALID", "Futility HSD gamma must be in [-40,40]")
    }
    if (futility_spending == "user_supplied") {
      cumulative_beta <- request$futility_parameters$user_cumulative_beta_spending
      beta_total <- 1 - power
      if (!is.numeric(cumulative_beta) || length(cumulative_beta) != length(information) || any(!is.finite(cumulative_beta)) || any(cumulative_beta < 0) || any(diff(cumulative_beta) < 0) || abs(tail(cumulative_beta, 1) - beta_total) > 1e-12) {
        stop_ecae("SEQUENTIAL_FUTILITY_INVALID", "User cumulative beta spending must be nondecreasing, match all looks, and end at one minus power")
      }
      futility_parameter <- cumulative_beta / beta_total
    }
  } else if (isTRUE(request$futility_binding)) {
    stop_ecae("SEQUENTIAL_FUTILITY_INVALID", "futility_binding requires an explicit futility_spending family")
  }

  arguments <- list(
    k = length(information),
    test.type = if (futility_enabled) if (isTRUE(request$futility_binding)) 3 else 4 else if (sided == 1) 1 else 2,
    alpha = alpha_per_upper_tail,
    beta = 1 - power,
    timing = if (length(information) == 1L) 1 else information[-length(information)],
    sfu = spending_function,
    tol = 1e-6
  )
  if (!is.null(spending_parameter)) arguments$sfupar <- spending_parameter
  if (futility_enabled) {
    arguments$sfl <- futility_function
    if (!is.null(futility_parameter)) arguments$sflpar <- futility_parameter
  } else if (sided == 2) {
    arguments$sfl <- spending_function
    if (!is.null(spending_parameter)) arguments$sflpar <- spending_parameter
  }
  design <- do.call(gsDesign::gsDesign, arguments)

  upper <- as.numeric(design$upper$bound)
  cumulative_alpha <- cumsum(as.numeric(design$upper$spend)) * if (sided == 2) 2 else 1
  lower <- if (futility_enabled) as.numeric(design$lower$bound) else if (sided == 2) -upper else rep(NA_real_, length(upper))
  cumulative_beta <- if (futility_enabled) cumsum(as.numeric(design$lower$spend)) else rep(NA_real_, length(upper))
  nominal_p <- if (sided == 1) stats::pnorm(upper, lower.tail = FALSE) else 2 * stats::pnorm(upper, lower.tail = FALSE)
  numeric_outputs <- c(upper, cumulative_alpha, nominal_p, if (futility_enabled) c(lower, cumulative_beta) else numeric(0))
  if (any(!is.finite(numeric_outputs)) || any(diff(cumulative_alpha) < -1e-12) || max(cumulative_alpha) > alpha_total + 1e-8 || abs(tail(cumulative_alpha, 1) - alpha_total) > 1e-8) {
    stop_ecae("BACKEND_NUMERICAL_INVALID", "Group-sequential output failed numerical invariants")
  }

  crossing <- list(status = "not_evaluated_design_only", first_crossing_look = NULL, direction = NULL)
  if (!is.null(request$observed_z_statistics)) {
    observed <- request$observed_z_statistics
    if (!is.numeric(observed) || length(observed) != length(information) || any(!is.finite(observed))) {
      stop_ecae("SEQUENTIAL_OBSERVED_STATISTIC_INVALID", "observed_z_statistics must provide one finite value per look")
    }
    crossed_upper <- observed >= upper
    crossed_lower <- if (sided == 2 || futility_enabled) observed <= lower else rep(FALSE, length(observed))
    crossed <- which(crossed_upper | crossed_lower)
    if (length(crossed) > 0L) {
      first <- crossed[[1]]
      crossing <- list(status = if (crossed_upper[[first]]) "efficacy_boundary_crossed" else if (futility_enabled) "futility_boundary_crossed" else "efficacy_boundary_crossed", first_crossing_look = first, direction = if (crossed_upper[[first]]) "upper" else "lower")
    } else {
      crossing <- list(status = "no_efficacy_boundary_crossed", first_crossing_look = NULL, direction = NULL)
    }
  }
  efficacy_boundaries <- lapply(seq_along(upper), function(index) list(upper = upper[[index]], lower = if (sided == 2 && !futility_enabled) lower[[index]] else NULL))
  futility_boundaries <- lapply(seq_along(lower), function(index) if (futility_enabled) lower[[index]] else NULL)
  null_rejection <- as.numeric(design$upper$prob[, 1])
  alternative_rejection <- as.numeric(design$upper$prob[, 2])
  if (sided == 2) {
    null_rejection <- null_rejection + as.numeric(design$lower$prob[, 1])
    alternative_rejection <- alternative_rejection + as.numeric(design$lower$prob[, 2])
  }
  maximum_information <- tail(as.numeric(design$n.I), 1)
  warnings <- c(if (futility_enabled) if (isTRUE(request$futility_binding)) "binding_futility_requires_strict_stop_compliance" else "nonbinding_futility_may_be_overridden_without_type_I_inflation" else "efficacy_only_no_futility", "external_parity_and_simulation_still_required_for_verification")
  list(
    looks = length(information),
    sided = sided,
    alpha = alpha_total,
    power = power,
    effect_scale = "z_statistic",
    efficacy_spending = spending,
    futility_spending = if (futility_enabled) futility_spending else NULL,
    futility_binding = isTRUE(request$futility_binding),
    information_fractions = as.list(as.numeric(information)),
    efficacy_boundaries = efficacy_boundaries,
    futility_boundaries = futility_boundaries,
    nominal_p_values = as.list(nominal_p),
    cumulative_alpha_spent = as.list(cumulative_alpha),
    cumulative_beta_spent = if (futility_enabled) as.list(cumulative_beta) else rep(list(NULL), length(information)),
    crossing_decision = crossing,
    design_operating_characteristics = list(
      null_rejection_probability_by_look = as.list(null_rejection),
      alternative_rejection_probability_by_look = as.list(alternative_rejection),
      total_null_rejection_probability = sum(null_rejection),
      total_alternative_rejection_probability = sum(alternative_rejection),
      expected_information_fraction_under_null = as.numeric(design$en[[1]]) / maximum_information,
      expected_information_fraction_under_alternative = as.numeric(design$en[[2]]) / maximum_information,
      maximum_information_relative_to_fixed_horizon = maximum_information
    ),
    warnings = as.list(warnings)
  )
}

if (!requireNamespace("jsonlite", quietly = TRUE)) stop("jsonlite is required before the adapter can emit a structured result")

input_text <- paste(readLines(file("stdin"), warn = FALSE), collapse = "\n")
response <- tryCatch(
  {
    request <- jsonlite::fromJSON(input_text, simplifyDataFrame = TRUE)
    result <- run_adapter(request)
    list(schema_version = "1.0.0", backend_id = BACKEND_ID, candidate_id = CANDIDATE_ID, package = "gsDesign", version = EXPECTED_PACKAGE_VERSION, ok = TRUE, result = result, warnings = result$warnings, error = NULL)
  },
  ecae_backend_error = function(error) list(schema_version = "1.0.0", backend_id = BACKEND_ID, candidate_id = CANDIDATE_ID, package = "gsDesign", version = EXPECTED_PACKAGE_VERSION, ok = FALSE, result = NULL, warnings = list(), error = list(code = error$code, message = error$message, details = error$details)),
  error = function(error) list(schema_version = "1.0.0", backend_id = BACKEND_ID, candidate_id = CANDIDATE_ID, package = "gsDesign", version = EXPECTED_PACKAGE_VERSION, ok = FALSE, result = NULL, warnings = list(), error = list(code = "BACKEND_INTERNAL_ERROR", message = conditionMessage(error), details = NULL))
)
emit(response)
