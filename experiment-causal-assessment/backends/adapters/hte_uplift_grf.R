#!/usr/bin/env Rscript

# Development-only independent GRF oracle for honest HTE differential parity.
# It is never selected as the production backend and cannot authorize a policy.

EXPECTED_PACKAGE_VERSION <- "2.6.1"
BACKEND_ID <- "hte_uplift"
CANDIDATE_ID <- "hte_uplift_grf"
emit <- function(x) cat(jsonlite::toJSON(x, auto_unbox=TRUE, null="null", na="null", digits=16))
stop_ecae <- function(code,message,details=NULL) stop(structure(list(message=message,call=NULL,code=code,details=details),class=c("ecae_backend_error","error","condition")))
safe_name <- function(x,field) { if (!is.character(x)||length(x)!=1L||!grepl("^[A-Za-z][A-Za-z0-9_]*$",x)) stop_ecae("BACKEND_COLUMN_INVALID",paste(field,"must be a safe column name")); x }

interval <- function(values, level) {
  if (!is.numeric(values)||length(values)<2L||any(!is.finite(values))) stop_ecae("BACKEND_NUMERICAL_INVALID","Interval input is invalid")
  estimate <- mean(values); standard_error <- stats::sd(values)/sqrt(length(values)); z <- stats::qnorm(1-(1-level)/2)
  list(estimate=estimate,standard_error=standard_error,confidence_interval=list(level=level,lower=estimate-z*standard_error,upper=estimate+z*standard_error),sample_size=length(values))
}

ranking_area <- function(scores, effects, target) {
  order_index <- order(scores,decreasing=TRUE); sorted <- effects[order_index]; cumulative <- cumsum(sorted)/seq_along(sorted); baseline <- mean(effects)
  weights <- if (target=="AUTOC") 1/seq_along(sorted) else 2*(1-seq_along(sorted)/length(sorted))
  estimate <- sum(weights*(cumulative-baseline))/sum(abs(weights)); list(estimate=estimate,definition=target)
}

run_adapter <- function(request) {
  observed <- as.character(utils::packageVersion("grf")); if (!identical(observed,EXPECTED_PACKAGE_VERSION)) stop_ecae("BACKEND_VERSION_MISMATCH","grf version differs from adapter lock",list(expected=EXPECTED_PACKAGE_VERSION,observed=observed))
  data <- request$rows; if (!is.data.frame(data)||nrow(data)<200L) stop_ecae("BACKEND_REQUEST_INVALID","rows must decode to at least 200 observations")
  outcome <- safe_name(request$outcome_column,"outcome_column"); treatment <- safe_name(request$treatment_column,"treatment_column"); partition <- safe_name(request$partition_column,"partition_column"); group <- safe_name(request$group_column,"group_column")
  covariates <- request$covariate_columns; if (!is.character(covariates)||length(covariates)<1L||any(!grepl("^[A-Za-z][A-Za-z0-9_]*$",covariates))) stop_ecae("BACKEND_COLUMN_INVALID","covariate_columns are invalid")
  missing <- setdiff(c(outcome,treatment,partition,group,covariates),names(data)); if (length(missing)>0L) stop_ecae("BACKEND_COLUMN_MISSING","Required columns are absent",as.list(missing))
  numeric_columns <- c(outcome,treatment,covariates); if (any(!vapply(data[,numeric_columns,drop=FALSE],is.numeric,logical(1)))||any(!is.finite(as.matrix(data[,numeric_columns,drop=FALSE])))) stop_ecae("BACKEND_REQUEST_INVALID","Outcome treatment and covariates must be finite numeric")
  if (!setequal(unique(data[[treatment]]),c(0,1))) stop_ecae("HTE_TREATMENT_INVALID","Treatment must contain both binary arms")
  partitions <- as.character(data[[partition]]); if (!setequal(unique(partitions),c("development","evaluation"))) stop_ecae("HTE_PARTITION_INVALID","partition must contain development and evaluation")
  development <- data[partitions=="development",,drop=FALSE]; evaluation <- data[partitions=="evaluation",,drop=FALSE]
  if (nrow(development)<100L||nrow(evaluation)<100L) stop_ecae("HTE_PARTITION_INVALID","Both partitions require at least 100 rows")
  probability <- request$known_treatment_probability; if (!is.numeric(probability)||length(probability)!=1L||!is.finite(probability)||probability<=0||probability>=1) stop_ecae("BACKEND_REQUEST_INVALID","known_treatment_probability must be in (0,1)")
  trees <- request$num_trees; seed <- request$seed; level <- request$confidence_level
  if (!is.numeric(trees)||length(trees)!=1L||trees!=floor(trees)||trees<500||!is.numeric(seed)||length(seed)!=1L||seed!=floor(seed)||seed<0) stop_ecae("HTE_CONFIGURATION_INVALID","num_trees or seed is invalid")
  if (!is.numeric(level)||length(level)!=1L||level<=0||level>=1) stop_ecae("BACKEND_CONFIDENCE_LEVEL_INVALID","confidence_level must be in (0,1)")
  X <- as.matrix(development[,covariates,drop=FALSE]); Y <- development[[outcome]]; W <- development[[treatment]]
  forest <- grf::causal_forest(X,Y,W,W.hat=rep(probability,length(W)),num.trees=as.integer(trees),honesty=TRUE,seed=as.integer(seed))
  predictions <- predict(forest,as.matrix(evaluation[,covariates,drop=FALSE]),estimate.variance=TRUE)
  cate <- as.numeric(predictions$predictions); variance <- as.numeric(predictions$variance.estimates)
  if (any(!is.finite(c(cate,variance)))||any(variance<0)) stop_ecae("BACKEND_NUMERICAL_INVALID","GRF predictions failed numerical invariants")
  eval_y <- evaluation[[outcome]]; eval_w <- evaluation[[treatment]]
  randomized_score <- eval_w*eval_y/probability-(1-eval_w)*eval_y/(1-probability)
  labels <- as.character(evaluation[[group]]); groups <- sort(unique(labels)); if (length(groups)<2L||any(table(labels)<20L)) stop_ecae("HTE_GROUP_INADEQUATE","At least two groups with twenty evaluation rows are required")
  gate <- lapply(groups,function(label) { result<-interval(randomized_score[labels==label],level); result$group<-label; result })
  calibration <- grf::test_calibration(forest)
  qini <- ranking_area(cate,randomized_score,"Qini"); autoc <- ranking_area(cate,randomized_score,"AUTOC")
  warnings <- c("development_oracle_not_selected_backend","randomized_evaluation_score_used_for_independent_holdout","row_level_CATE_not_emitted","external_parity_simulation_and_independent_review_pending")
  list(GATE=gate,CATE_distribution=list(quantiles=as.list(as.numeric(stats::quantile(cate,c(0,.1,.25,.5,.75,.9,1)))),row_level_predictions_emitted=FALSE),calibration=list(mean_forest_prediction=unname(calibration["mean.forest.prediction","Estimate"]),differential_forest_prediction=unname(calibration["differential.forest.prediction","Estimate"])),Qini=qini,AUTOC=autoc,split_binding=list(development_sample_size=nrow(development),evaluation_sample_size=nrow(evaluation),evaluation_outcomes_used_for_training=FALSE,honest_forest=TRUE,seed=as.integer(seed)),business_action_authorized=FALSE,warnings=as.list(warnings))
}

if (!requireNamespace("jsonlite",quietly=TRUE)) stop("jsonlite is required")
input <- paste(readLines(file("stdin"),warn=FALSE),collapse="\n")
response <- tryCatch({ result<-run_adapter(jsonlite::fromJSON(input,simplifyDataFrame=TRUE)); list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="grf",version=EXPECTED_PACKAGE_VERSION,ok=TRUE,result=result,warnings=result$warnings,error=NULL) },ecae_backend_error=function(e) list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="grf",version=EXPECTED_PACKAGE_VERSION,ok=FALSE,result=NULL,warnings=list(),error=list(code=e$code,message=e$message,details=e$details)),error=function(e) list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="grf",version=EXPECTED_PACKAGE_VERSION,ok=FALSE,result=NULL,warnings=list(),error=list(code="BACKEND_INTERNAL_ERROR",message=conditionMessage(e),details=NULL)))
emit(response)
