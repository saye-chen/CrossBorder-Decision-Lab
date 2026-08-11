#!/usr/bin/env Rscript

# JSON-only synthdid common-adoption adapter. The selected package is beta;
# adapter existence cannot promote the backend without parity and review.

EXPECTED_PACKAGE_VERSION <- "0.0.9"
EXPECTED_SOURCE_REVISION <- "70c1ce3eac58e28c30b67435ca377bb48baa9b8a"
BACKEND_ID <- "synthetic_did"; CANDIDATE_ID <- "synthetic_did_synthdid"
emit <- function(x) cat(jsonlite::toJSON(x,auto_unbox=TRUE,null="null",na="null",digits=16))
stop_ecae <- function(code,message,details=NULL) stop(structure(list(message=message,call=NULL,code=code,details=details),class=c("ecae_backend_error","error","condition")))

run_adapter <- function(request) {
  observed <- as.character(utils::packageVersion("synthdid")); if (!identical(observed,EXPECTED_PACKAGE_VERSION)) stop_ecae("BACKEND_VERSION_MISMATCH","synthdid version differs from adapter lock",list(expected=EXPECTED_PACKAGE_VERSION,observed=observed))
  Y <- request$outcome_matrix; if (is.list(Y)) Y <- do.call(rbind,Y)
  if (!is.matrix(Y)||!is.numeric(Y)||any(!is.finite(Y))||nrow(Y)<4L||ncol(Y)<5L) stop_ecae("SDID_MATRIX_INVALID","outcome_matrix must be a finite numeric matrix of adequate size")
  N0 <- request$control_unit_count; T0 <- request$pre_period_count
  if (!is.numeric(N0)||length(N0)!=1L||N0!=floor(N0)||N0<2||N0>=nrow(Y)||!is.numeric(T0)||length(T0)!=1L||T0!=floor(T0)||T0<4||T0>=ncol(Y)) stop_ecae("SDID_MATRIX_INVALID","Control and pre-period counts do not partition the matrix")
  method <- request$uncertainty_method; if (!method %in% c("placebo","bootstrap","jackknife")) stop_ecae("SDID_UNCERTAINTY_INVALID","Unknown uncertainty method")
  reps <- request$replications; seed <- request$seed
  if (!is.numeric(reps)||length(reps)!=1L||reps!=floor(reps)||reps<200||!is.numeric(seed)||length(seed)!=1L||seed!=floor(seed)||seed<0) stop_ecae("SEED_CONTRACT_INVALID","replications or seed are invalid")
  if (method=="placebo" && N0 <= nrow(Y)-N0) stop_ecae("SDID_UNCERTAINTY_INVALID","Placebo variance requires more controls than treated units")
  set.seed(as.integer(seed)); estimate <- synthdid::synthdid_estimate(Y,as.integer(N0),as.integer(T0)); variance <- as.numeric(stats::vcov(estimate,method=method,replications=as.integer(reps)))
  effect <- as.numeric(estimate); se <- sqrt(variance); level <- request$confidence_level
  if (!is.numeric(level)||length(level)!=1L||level<=0||level>=1) stop_ecae("BACKEND_CONFIDENCE_LEVEL_INVALID","confidence_level must be in (0,1)")
  z <- stats::qnorm(1-(1-level)/2); weights <- attr(estimate,"weights"); omega <- as.numeric(weights$omega); lambda <- as.numeric(weights$lambda)
  if (any(!is.finite(c(effect,se,omega,lambda)))||se<0||any(omega< -1e-10)||any(lambda< -1e-10)||abs(sum(omega)-1)>1e-6||abs(sum(lambda)-1)>1e-6) stop_ecae("SDID_WEIGHT_INVALID","SDID output or weights failed invariants")
  warnings <- c("candidate_package_is_beta_and_common_start_only","excellent_pre_fit_does_not_establish_identification","external_parity_simulation_and_independent_review_pending")
  list(effect=effect,standard_error=se,confidence_interval=list(level=level,lower=effect-z*se,upper=effect+z*se),uncertainty_method=method,replications=as.integer(reps),seed=as.integer(seed),unit_weights=as.list(omega),time_weights=as.list(lambda),effective_donor_count=1/sum(omega^2),weight_concentration=list(maximum_unit_weight=max(omega),maximum_time_weight=max(lambda)),source_revision_expected=EXPECTED_SOURCE_REVISION,warnings=as.list(warnings))
}

if (!requireNamespace("jsonlite",quietly=TRUE)) stop("jsonlite is required")
input <- paste(readLines(file("stdin"),warn=FALSE),collapse="\n")
response <- tryCatch({ result<-run_adapter(jsonlite::fromJSON(input,simplifyDataFrame=FALSE)); list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="synthdid",version=EXPECTED_PACKAGE_VERSION,ok=TRUE,result=result,warnings=result$warnings,error=NULL) },ecae_backend_error=function(e) list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="synthdid",version=EXPECTED_PACKAGE_VERSION,ok=FALSE,result=NULL,warnings=list(),error=list(code=e$code,message=e$message,details=e$details)),error=function(e) list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="synthdid",version=EXPECTED_PACKAGE_VERSION,ok=FALSE,result=NULL,warnings=list(),error=list(code="BACKEND_INTERNAL_ERROR",message=conditionMessage(e),details=NULL)))
emit(response)
