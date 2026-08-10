#!/usr/bin/env Rscript

# JSON-only classic SCM adapter with in-space placebo, time placebo, and LOO.
# Adapter existence is development evidence only.

EXPECTED_PACKAGE_VERSION <- "1.1-10"
BACKEND_ID <- "synthetic_control"; CANDIDATE_ID <- "synthetic_control_synth"
emit <- function(x) cat(jsonlite::toJSON(x,auto_unbox=TRUE,null="null",na="null",digits=16))
stop_ecae <- function(code,message,details=NULL) stop(structure(list(message=message,call=NULL,code=code,details=details),class=c("ecae_backend_error","error","condition")))
safe_name <- function(x,field) { if (!is.character(x)||length(x)!=1L||!grepl("^[A-Za-z][A-Za-z0-9_]*$",x)) stop_ecae("BACKEND_COLUMN_INVALID",paste(field,"must be a safe column name")); x }

run_adapter <- function(request) {
  observed <- utils::packageDescription("Synth",fields="Version"); if (!identical(observed,EXPECTED_PACKAGE_VERSION)) stop_ecae("BACKEND_VERSION_MISMATCH","Synth version differs from adapter lock",list(expected=EXPECTED_PACKAGE_VERSION,observed=observed))
  data <- request$rows; if (!is.data.frame(data)||nrow(data)<20L) stop_ecae("BACKEND_REQUEST_INVALID","rows must decode to a panel data frame")
  unit <- safe_name(request$unit_column,"unit_column"); time <- safe_name(request$time_column,"time_column"); outcome <- safe_name(request$outcome_column,"outcome_column")
  predictors <- request$predictor_columns; if (!is.character(predictors)||length(predictors)<1L||any(!grepl("^[A-Za-z][A-Za-z0-9_]*$",predictors))) stop_ecae("BACKEND_COLUMN_INVALID","predictor_columns are invalid")
  missing <- setdiff(c(unit,time,outcome,predictors),names(data)); if (length(missing)>0L) stop_ecae("BACKEND_COLUMN_MISSING","Required columns are absent",as.list(missing))
  numeric_columns <- c(unit,time,outcome,predictors)
  if (any(!vapply(data[,numeric_columns,drop=FALSE],is.numeric,logical(1)))) stop_ecae("BACKEND_REQUEST_INVALID","SCM adapter requires numeric ids times outcomes and predictors")
  if (any(!is.finite(as.matrix(data[,numeric_columns,drop=FALSE])))) stop_ecae("BACKEND_REQUEST_INVALID","SCM adapter requires finite ids times outcomes and predictors")
  treated <- request$treated_unit; donors <- as.numeric(request$donor_pool); pre <- as.numeric(request$pre_periods); post <- as.numeric(request$post_periods); placebo_pre <- as.numeric(request$time_placebo_pre_periods); placebo_post <- as.numeric(request$time_placebo_post_periods)
  if (!is.numeric(treated)||length(treated)!=1L||!is.numeric(donors)||length(donors)<3L||anyDuplicated(donors)||treated %in% donors) stop_ecae("DONOR_POOL_INADEQUATE","One treated unit and at least three distinct donors are required")
  if (length(pre)<4L||length(post)<1L||length(placebo_pre)<3L||length(placebo_post)<1L||length(intersect(pre,post))>0L||length(intersect(placebo_pre,placebo_post))>0L||!all(c(placebo_pre,placebo_post)%in%pre)) stop_ecae("SCM_TIME_WINDOW_INVALID","Primary and placebo windows are invalid")
  observed_units <- unique(data[[unit]]); if (!all(c(treated,donors)%in%observed_units)) stop_ecae("DONOR_POOL_INADEQUATE","Treated or donor unit is absent")

  fit_once <- function(target,controls,optimize_periods,plot_periods) {
    prepared <- Synth::dataprep(foo=data,predictors=predictors,predictors.op="mean",dependent=outcome,unit.variable=unit,time.variable=time,treatment.identifier=target,controls.identifier=controls,time.predictors.prior=optimize_periods,time.optimize.ssr=optimize_periods,time.plot=plot_periods)
    capture.output(fit <- Synth::synth(prepared,verbose=FALSE))
    weights <- as.numeric(fit$solution.w); names(weights) <- rownames(fit$solution.w)
    if (any(!is.finite(weights))||any(weights < -1e-10)||abs(sum(weights)-1)>1e-6) stop_ecae("SCM_WEIGHT_INVALID","SCM donor weights failed invariants")
    observed_path <- as.numeric(prepared$Y1plot); synthetic_path <- as.numeric(prepared$Y0plot %*% fit$solution.w); gaps <- observed_path-synthetic_path
    times <- as.numeric(rownames(prepared$Y1plot)); pre_index <- times %in% optimize_periods; post_index <- !pre_index
    pre_rmspe <- sqrt(mean(gaps[pre_index]^2)); post_rmspe <- if (any(post_index)) sqrt(mean(gaps[post_index]^2)) else NA_real_
    list(weights=weights,times=times,observed=observed_path,synthetic=synthetic_path,gaps=gaps,pre_RMSPE=pre_rmspe,post_RMSPE=post_rmspe,ratio=post_rmspe/max(pre_rmspe,.Machine$double.eps))
  }

  primary <- fit_once(treated,donors,pre,c(pre,post))
  placebo <- lapply(donors,function(pseudo) { fit<-fit_once(pseudo,setdiff(donors,pseudo),pre,c(pre,post)); list(unit=pseudo,pre_RMSPE=fit$pre_RMSPE,post_RMSPE=fit$post_RMSPE,post_pre_RMSPE_ratio=fit$ratio) })
  placebo_ratios <- vapply(placebo,function(x) x$post_pre_RMSPE_ratio,numeric(1)); rank <- 1L+sum(placebo_ratios>=primary$ratio); p_value <- rank/(length(placebo_ratios)+1L)
  loo <- lapply(donors,function(excluded) { fit<-fit_once(treated,setdiff(donors,excluded),pre,c(pre,post)); post_index<-fit$times %in% post; list(excluded_donor=excluded,post_average_gap=mean(fit$gaps[post_index]),pre_RMSPE=fit$pre_RMSPE) })
  time_placebo <- fit_once(treated,donors,placebo_pre,c(placebo_pre,placebo_post)); tp_index <- time_placebo$times %in% placebo_post
  post_index <- primary$times %in% post; effective <- 1/sum(primary$weights^2)
  if (!is.finite(primary$pre_RMSPE)||!is.finite(effective)||effective<=0||any(!is.finite(primary$gaps))) stop_ecae("BACKEND_NUMERICAL_INVALID","SCM output failed numerical invariants")
  warnings <- c("placebo_rank_is_design_based_diagnostic_not_universal_sampling_interval","short_pre_fit_or_donor_dominance_limits_claim_to_CE3","external_parity_simulation_and_independent_review_pending")
  list(unit_weights=as.list(primary$weights),effective_donor_count=effective,weight_concentration=list(maximum=max(primary$weights),herfindahl=sum(primary$weights^2)),pre_RMSPE=primary$pre_RMSPE,post_gap=list(times=as.list(primary$times[post_index]),values=as.list(primary$gaps[post_index]),average=mean(primary$gaps[post_index])),placebo_rank=list(rank=rank,total=length(placebo_ratios)+1L,p_value=p_value,treated_post_pre_RMSPE_ratio=primary$ratio,placebos=placebo),time_placebo=list(average_gap=mean(time_placebo$gaps[tp_index]),pre_RMSPE=time_placebo$pre_RMSPE),leave_one_out=loo,warnings=as.list(warnings))
}

if (!requireNamespace("jsonlite",quietly=TRUE)) stop("jsonlite is required")
input <- paste(readLines(file("stdin"),warn=FALSE),collapse="\n")
response <- tryCatch({ result<-run_adapter(jsonlite::fromJSON(input,simplifyDataFrame=TRUE)); list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="Synth",version=EXPECTED_PACKAGE_VERSION,ok=TRUE,result=result,warnings=result$warnings,error=NULL) },ecae_backend_error=function(e) list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="Synth",version=EXPECTED_PACKAGE_VERSION,ok=FALSE,result=NULL,warnings=list(),error=list(code=e$code,message=e$message,details=e$details)),error=function(e) list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="Synth",version=EXPECTED_PACKAGE_VERSION,ok=FALSE,result=NULL,warnings=list(),error=list(code="BACKEND_INTERNAL_ERROR",message=conditionMessage(e),details=NULL)))
emit(response)
