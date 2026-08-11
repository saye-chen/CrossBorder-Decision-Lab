#!/usr/bin/env Rscript

# JSON-only cross-fitted AIPW adapter. Identification, negative controls, and
# unmeasured-confounding sensitivity remain outside-backend gates.

EXPECTED_PACKAGE_VERSION <- "0.6.9.3"
BACKEND_ID <- "observational_aipw"; CANDIDATE_ID <- "observational_aipw_r"
emit <- function(x) cat(jsonlite::toJSON(x,auto_unbox=TRUE,null="null",na="null",digits=16))
stop_ecae <- function(code,message,details=NULL) stop(structure(list(message=message,call=NULL,code=code,details=details),class=c("ecae_backend_error","error","condition")))

run_adapter <- function(request) {
  observed <- as.character(utils::packageVersion("AIPW")); if (!identical(observed,EXPECTED_PACKAGE_VERSION)) stop_ecae("BACKEND_VERSION_MISMATCH","AIPW version differs from adapter lock",list(expected=EXPECTED_PACKAGE_VERSION,observed=observed))
  if (!requireNamespace("SuperLearner",quietly=TRUE)) stop_ecae("BACKEND_DEPENDENCY_MISSING","SuperLearner is required by the locked AIPW adapter")
  suppressPackageStartupMessages(library("SuperLearner",character.only=TRUE))
  Y <- as.numeric(request$outcome); A <- as.numeric(request$treatment); W <- request$covariates; if (is.list(W)) W <- do.call(rbind,W)
  if (!is.numeric(Y)||length(Y)<50L||any(!is.finite(Y))||!is.numeric(A)||length(A)!=length(Y)||!setequal(unique(A),c(0,1))||!is.matrix(W)||!is.numeric(W)||nrow(W)!=length(Y)||ncol(W)<1L||any(!is.finite(W))) stop_ecae("BACKEND_REQUEST_INVALID","Outcome treatment and covariate matrix are invalid")
  estimand <- request$estimand; if (!estimand %in% c("ATE","ATT")) stop_ecae("OBSERVATIONAL_ESTIMAND_UNSUPPORTED","estimand must be ATE or ATT")
  folds <- request$folds; seed <- request$seed; if (!is.numeric(folds)||length(folds)!=1L||folds!=floor(folds)||folds<2||folds>20||!is.numeric(seed)||length(seed)!=1L||seed!=floor(seed)||seed<0) stop_ecae("SEED_CONTRACT_INVALID","folds or seed is invalid")
  allowed <- c("SL.mean","SL.glm","SL.glmnet"); qlearners <- request$outcome_learners; glearners <- request$propensity_learners
  if (!is.character(qlearners)||length(qlearners)<1L||!all(qlearners%in%allowed)||!is.character(glearners)||length(glearners)<1L||!all(glearners%in%allowed)) stop_ecae("AIPW_LEARNER_UNSUPPORTED","Learners must come from the frozen supported SuperLearner set")
  bounds <- as.numeric(request$propensity_bounds); if (length(bounds)!=2L||any(!is.finite(bounds))||bounds[[1]]<=0||bounds[[2]]>=1||bounds[[1]]>=bounds[[2]]) stop_ecae("PROPENSITY_BOUND_INVALID","propensity_bounds must be an interior ordered pair")
  if (abs(bounds[[2]]-(1-bounds[[1]]))>1e-12) stop_ecae("PROPENSITY_BOUND_INVALID","Selected AIPW adapter requires symmetric propensity bounds")
  level <- request$confidence_level; if (!is.numeric(level)||length(level)!=1L||abs(level-.95)>1e-12) stop_ecae("BACKEND_CONFIDENCE_LEVEL_INVALID","AIPW 0.6.9.3 adapter currently exposes its native 95% interval only")
  set.seed(as.integer(seed))
  fit <- AIPW::aipw_wrapper(Y=Y,A=A,W=W,Q.SL.library=qlearners,g.SL.library=glearners,k_split=as.integer(folds),g.bound=bounds[[1]],stratified_fit=identical(estimand,"ATT"),verbose=FALSE)
  label <- if (estimand=="ATE") "Risk Difference" else "ATT Risk Difference"; if (!label %in% rownames(fit$result)) label <- if (estimand=="ATE") "Mean Difference" else "ATT Mean Difference"
  if (!label %in% rownames(fit$result)) stop_ecae("BACKEND_OUTPUT_INVALID","Requested estimand row is absent")
  row <- fit$result[label,,drop=FALSE]; effect <- as.numeric(row[1,"Estimate"]); se <- as.numeric(row[1,"SE"]); lower <- as.numeric(row[1,"95% LCL"]); upper <- as.numeric(row[1,"95% UCL"])
  propensity <- as.numeric(fit$obs_est$p_score); weights <- as.numeric(fit$obs_est$ip_weights); eif <- as.numeric(fit$obs_est$aipw_eif1-fit$obs_est$aipw_eif0)
  if (estimand=="ATT") eif <- rep(NA_real_,length(Y))
  numeric_outputs <- c(effect,se,lower,upper,propensity,weights); if (any(!is.finite(numeric_outputs))||se<0||lower>upper||any(propensity<bounds[[1]]-1e-12)||any(propensity>bounds[[2]]+1e-12)||any(weights<=0)) stop_ecae("BACKEND_NUMERICAL_INVALID","AIPW output failed numerical invariants")
  ic_summary <- if (estimand=="ATE") list(mean=mean(eif-effect),standard_deviation=stats::sd(eif-effect),maximum_absolute=max(abs(eif-effect))) else list(status="package_ATT_influence_curve_not_exposed_by_selected_API")
  warnings <- c("double_robustness_is_an_assumption_not_empirical_proof","truncation_may_change_the_effective_target_population","negative_controls_and_unmeasured_confounding_sensitivity_required_outside_adapter","external_parity_and_simulation_pending")
  list(effect=effect,standard_error=se,confidence_interval=list(level=.95,lower=lower,upper=upper),influence_curve_summary=ic_summary,propensity_summary=list(minimum=min(propensity),q01=unname(stats::quantile(propensity,.01)),median=stats::median(propensity),q99=unname(stats::quantile(propensity,.99)),maximum=max(propensity),clipped_count=sum(fit$obs_est$raw_p_score<bounds[[1]]|fit$obs_est$raw_p_score>bounds[[2]])),effective_sample=(sum(weights)^2)/sum(weights^2),folds=as.integer(folds),seed=as.integer(seed),outcome_learners=as.list(qlearners),propensity_learners=as.list(glearners),warnings=as.list(warnings))
}

if (!requireNamespace("jsonlite",quietly=TRUE)) stop("jsonlite is required")
input <- paste(readLines(file("stdin"),warn=FALSE),collapse="\n")
response <- tryCatch({ result<-run_adapter(jsonlite::fromJSON(input,simplifyDataFrame=FALSE)); list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="AIPW",version=EXPECTED_PACKAGE_VERSION,ok=TRUE,result=result,warnings=result$warnings,error=NULL) },ecae_backend_error=function(e) list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="AIPW",version=EXPECTED_PACKAGE_VERSION,ok=FALSE,result=NULL,warnings=list(),error=list(code=e$code,message=e$message,details=e$details)),error=function(e) list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="AIPW",version=EXPECTED_PACKAGE_VERSION,ok=FALSE,result=NULL,warnings=list(),error=list(code="BACKEND_INTERNAL_ERROR",message=conditionMessage(e),details=NULL)))
emit(response)
