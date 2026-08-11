#!/usr/bin/env Rscript

# Reproduce frozen convention-normalized gsDesign/rpact parity vectors.

EXPECTED_GSDESIGN_VERSION <- "3.10.1"
EXPECTED_RPACT_VERSION <- "4.4.0"
BOUNDARY_TOLERANCE <- 1e-6
ALPHA_TOLERANCE <- 2e-8

if (!requireNamespace("jsonlite", quietly = TRUE)) stop("jsonlite is required")
if (!identical(as.character(utils::packageVersion("gsDesign")), EXPECTED_GSDESIGN_VERSION)) stop("gsDesign version mismatch")
if (!identical(as.character(utils::packageVersion("rpact")), EXPECTED_RPACT_VERSION)) stop("rpact version mismatch")

vector <- function(vector_id, information, spending, sided, alpha_total, gamma = NULL, user_spending = NULL) {
  gs_alpha <- if (sided == 1) alpha_total else alpha_total / 2
  gs_function <- switch(spending, obrien_fleming = gsDesign::sfLDOF, pocock = gsDesign::sfLDPocock, hwang_shih_decani = gsDesign::sfHSD, user_supplied = gsDesign::sfPoints)
  rpact_type <- switch(spending, obrien_fleming = "asOF", pocock = "asP", hwang_shih_decani = "asHSD", user_supplied = "asUser")
  gs_parameter <- if (spending == "hwang_shih_decani") gamma else if (spending == "user_supplied") user_spending / alpha_total else NULL
  gs_arguments <- list(k = length(information), test.type = if (sided == 1) 1 else 2, alpha = gs_alpha, beta = 0.2, timing = if (length(information) == 1L) 1 else information[-length(information)], sfu = gs_function, tol = 1e-6)
  if (!is.null(gs_parameter)) gs_arguments$sfupar <- gs_parameter
  if (sided == 2) {
    gs_arguments$sfl <- gs_function
    if (!is.null(gs_parameter)) gs_arguments$sflpar <- gs_parameter
  }
  gs <- do.call(gsDesign::gsDesign, gs_arguments)
  rpact_arguments <- list(kMax = length(information), sided = sided, alpha = alpha_total, beta = 0.2, informationRates = information, typeOfDesign = rpact_type, tolerance = 1e-8)
  if (spending == "hwang_shih_decani") rpact_arguments$gammaA <- gamma
  if (spending == "user_supplied") rpact_arguments$userAlphaSpending <- user_spending
  rp <- suppressMessages(do.call(rpact::getDesignGroupSequential, rpact_arguments))
  gs_boundaries <- as.numeric(gs$upper$bound)
  rpact_boundaries <- as.numeric(rp$criticalValues)
  gs_alpha_spent <- cumsum(as.numeric(gs$upper$spend)) * if (sided == 2) 2 else 1
  rpact_alpha_spent <- as.numeric(rp$alphaSpent)
  boundary_difference <- max(abs(gs_boundaries - rpact_boundaries))
  alpha_difference <- max(abs(gs_alpha_spent - rpact_alpha_spent))
  list(
    vector_id = vector_id,
    conventions = list(sided = sided, total_alpha = alpha_total, gsDesign_upper_tail_alpha = gs_alpha, spending = spending, information_fractions = as.list(information), hsd_gamma = gamma, user_cumulative_alpha_spending = if (is.null(user_spending)) NULL else as.list(user_spending)),
    gsDesign = list(boundaries = as.list(gs_boundaries), cumulative_total_alpha_spent = as.list(gs_alpha_spent)),
    rpact = list(boundaries = as.list(rpact_boundaries), cumulative_total_alpha_spent = as.list(rpact_alpha_spent)),
    maximum_absolute_boundary_difference = boundary_difference,
    maximum_absolute_cumulative_alpha_difference = alpha_difference,
    accepted = boundary_difference <= BOUNDARY_TOLERANCE && alpha_difference <= ALPHA_TOLERANCE
  )
}

vectors <- list(
  vector("obf_one_sided_three_unequal_looks", c(0.33, 0.67, 1), "obrien_fleming", 1, 0.025),
  vector("pocock_one_sided_three_unequal_looks", c(0.33, 0.67, 1), "pocock", 1, 0.025),
  vector("obf_two_sided_three_unequal_looks", c(0.33, 0.67, 1), "obrien_fleming", 2, 0.05),
  vector("pocock_two_sided_five_equal_looks", c(0.2, 0.4, 0.6, 0.8, 1), "pocock", 2, 0.05),
  vector("hsd_one_sided_four_unequal_looks", c(0.25, 0.5, 0.8, 1), "hwang_shih_decani", 1, 0.025, gamma = -4),
  vector("user_spending_one_sided_four_unequal_looks", c(0.2, 0.5, 0.75, 1), "user_supplied", 1, 0.025, user_spending = c(0.001, 0.006, 0.015, 0.025))
)

output <- list(
  schema_version = "1.0.0",
  report_id = "ECAE-WP06-GROUP-SEQUENTIAL-DUAL-ENGINE-PARITY-2026-08-10",
  generated_at = "2026-08-10T00:00:00+08:00",
  qualification = "development_parity_not_independent_external_verification",
  runtimes = list(R = as.character(getRversion()), gsDesign = EXPECTED_GSDESIGN_VERSION, rpact = EXPECTED_RPACT_VERSION),
  normalization = list(rpact_alpha_is_total_type_I_error = TRUE, gsDesign_alpha_is_one_sided = TRUE, two_sided_gsDesign_alpha_equals_total_alpha_divided_by_two = TRUE, gsDesign_incremental_spending_is_cumulatively_summed = TRUE, rpact_alpha_spent_is_already_cumulative = TRUE, boundary_scale = "z_statistic", efficacy_only = TRUE),
  tolerances = list(maximum_absolute_boundary_difference = BOUNDARY_TOLERANCE, maximum_absolute_cumulative_alpha_difference = ALPHA_TOLERANCE),
  vectors = vectors,
  all_vectors_accepted = all(vapply(vectors, function(item) isTRUE(item$accepted), logical(1))),
  release_effect = list(registry_verified = FALSE, external_review_pending = TRUE, operating_characteristic_simulation_pending = TRUE)
)
cat(jsonlite::toJSON(output, auto_unbox = TRUE, null = "null", digits = 16, pretty = TRUE))
