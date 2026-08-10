#!/usr/bin/env Rscript

# JSON-only Callaway-Sant'Anna group-time ATT adapter.
# Adapter existence and development execution do not create a verified backend.

EXPECTED_PACKAGE_VERSION <- "2.5.1"
BACKEND_ID <- "staggered_did"
CANDIDATE_ID <- "staggered_did_callaway_santanna"
emit <- function(x) cat(jsonlite::toJSON(x, auto_unbox=TRUE, null="null", na="null", digits=16))
stop_ecae <- function(code,message,details=NULL) stop(structure(list(message=message,call=NULL,code=code,details=details),class=c("ecae_backend_error","error","condition")))
safe_name <- function(x,field) { if (!is.character(x)||length(x)!=1L||!grepl("^[A-Za-z][A-Za-z0-9_]*$",x)) stop_ecae("BACKEND_COLUMN_INVALID",paste(field,"must be a safe column name")); x }

run_adapter <- function(request) {
  observed <- as.character(utils::packageVersion("did"))
  if (!identical(observed,EXPECTED_PACKAGE_VERSION)) stop_ecae("BACKEND_VERSION_MISMATCH","did version differs from adapter lock",list(expected=EXPECTED_PACKAGE_VERSION,observed=observed))
  if (!is.list(request)||!is.data.frame(request$rows)||nrow(request$rows)<20L) stop_ecae("BACKEND_REQUEST_INVALID","rows must decode to at least 20 observations")
  y <- safe_name(request$outcome_column,"outcome_column"); t <- safe_name(request$time_column,"time_column"); id <- safe_name(request$unit_column,"unit_column"); g <- safe_name(request$first_treatment_time_column,"first_treatment_time_column")
  covariates <- request$pretreatment_covariates; if (is.null(covariates)) covariates <- character(0)
  if (!is.character(covariates)||any(!grepl("^[A-Za-z][A-Za-z0-9_]*$",covariates))) stop_ecae("BACKEND_COLUMN_INVALID","pretreatment_covariates are invalid")
  data <- request$rows; missing <- setdiff(c(y,t,id,g,covariates),names(data)); if (length(missing)>0L) stop_ecae("BACKEND_COLUMN_MISSING","Required columns are absent",as.list(missing))
  if (!is.numeric(data[[y]])||any(!is.finite(data[[y]]))||!is.numeric(data[[t]])||any(!is.finite(data[[t]]))||!is.numeric(data[[g]])||any(!is.finite(data[[g]]))) stop_ecae("BACKEND_REQUEST_INVALID","Outcome time and first-treatment time must be finite numeric")
  timing_by_unit <- split(data[[g]],as.character(data[[id]])); if (any(vapply(timing_by_unit,function(x) length(unique(x))!=1L,logical(1)))) stop_ecae("TREATMENT_TIMING_INVALID","First treatment time must be constant within unit")
  control <- request$control_group; if (!control %in% c("never_treated","not_yet_treated")) stop_ecae("INVALID_STAGGERED_CONTROL","Unsupported control group")
  package_control <- if (control=="never_treated") "nevertreated" else "notyettreated"
  anticipation <- request$anticipation_periods; if (!is.numeric(anticipation)||length(anticipation)!=1L||anticipation<0||anticipation!=floor(anticipation)) stop_ecae("ANTICIPATION_WINDOW_INVALID","anticipation_periods must be a non-negative integer")
  level <- request$confidence_level; biters <- request$bootstrap_iterations
  if (!is.numeric(level)||length(level)!=1L||level<=0||level>=1||!is.numeric(biters)||length(biters)!=1L||biters<999||biters!=floor(biters)) stop_ecae("BACKEND_REQUEST_INVALID","Invalid confidence level or bootstrap iterations")
  cluster <- request$cluster_column; clustervars <- NULL
  if (!is.null(cluster)) { cluster <- safe_name(cluster,"cluster_column"); if (!cluster %in% names(data)) stop_ecae("BACKEND_COLUMN_MISSING","cluster_column is absent"); clustervars <- cluster }
  xformla <- if (length(covariates)==0L) stats::as.formula("~1") else stats::reformulate(covariates)
  panel <- identical(request$panel_structure,"panel")
  fit <- did::att_gt(yname=y,tname=t,idname=if(panel) id else NULL,gname=g,xformla=xformla,data=data,panel=panel,control_group=package_control,anticipation=anticipation,bstrap=TRUE,cband=TRUE,biters=as.integer(biters),clustervars=clustervars,allow_unbalanced_panel=isTRUE(request$allow_unbalanced_panel),print_details=FALSE)
  dynamic <- did::aggte(fit,type="dynamic",bstrap=TRUE,cband=TRUE,biters=as.integer(biters),clustervars=clustervars)
  overall <- did::aggte(fit,type="simple",bstrap=TRUE,cband=TRUE,biters=as.integer(biters),clustervars=clustervars)
  group_time <- lapply(seq_along(fit$att),function(i) list(group=unname(fit$group[[i]]),time=unname(fit$t[[i]]),att=unname(fit$att[[i]]),standard_error=unname(fit$se[[i]])))
  event <- lapply(seq_along(dynamic$egt),function(i) list(event_time=unname(dynamic$egt[[i]]),att=unname(dynamic$att.egt[[i]]),standard_error=unname(dynamic$se.egt[[i]])))
  critical <- unname(dynamic$crit.val.egt); if (is.null(critical)||!is.finite(critical)) stop_ecae("BACKEND_NUMERICAL_INVALID","Simultaneous-band critical value is absent")
  intervals <- lapply(event,function(x) list(event_time=x$event_time,lower=x$att-critical*x$standard_error,upper=x$att+critical*x$standard_error))
  numeric_values <- c(fit$att,fit$se,dynamic$att.egt,dynamic$se.egt,overall$overall.att,overall$overall.se,critical)
  if (any(!is.finite(numeric_values))||any(fit$se<0)||any(dynamic$se.egt<0)||overall$overall.se<0) stop_ecae("BACKEND_NUMERICAL_INVALID","DiD outputs failed numerical invariants")
  unit_timing <- data[!duplicated(data[[id]]),c(id,g),drop=FALSE]; group_share <- table(unit_timing[[g]])/nrow(unit_timing)
  post <- fit$group <= fit$t; raw_weight <- ifelse(post,as.numeric(group_share[as.character(fit$group)]),0); normalized_weight <- raw_weight/sum(raw_weight)
  aggregation_weights <- lapply(seq_along(normalized_weight),function(i) list(group=unname(fit$group[[i]]),time=unname(fit$t[[i]]),weight=unname(normalized_weight[[i]])))
  if (any(!is.finite(normalized_weight))||abs(sum(normalized_weight)-1)>1e-10) stop_ecae("BACKEND_NUMERICAL_INVALID","Aggregation weights failed invariants")
  warnings <- c("parallel_trends_no_anticipation_and_composition_remain_identification_assumptions","pretrend_nonrejection_is_not_identification_proof","external_parity_and_simulation_pending")
  list(group_time_ATT=group_time,aggregation=list(type="simple",effect=unname(overall$overall.att),standard_error=unname(overall$overall.se)),aggregation_weights=aggregation_weights,event_time_effects=event,simultaneous_intervals=list(level=level,critical_value=critical,intervals=intervals),pretrend_diagnostics=list(p_value=unname(fit$Wpval),status="diagnostic_not_proof"),control_group=control,anticipation_periods=anticipation,warnings=as.list(warnings))
}

if (!requireNamespace("jsonlite",quietly=TRUE)) stop("jsonlite is required")
input <- paste(readLines(file("stdin"),warn=FALSE),collapse="\n")
response <- tryCatch({ result<-run_adapter(jsonlite::fromJSON(input,simplifyDataFrame=TRUE)); list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="did",version=EXPECTED_PACKAGE_VERSION,ok=TRUE,result=result,warnings=result$warnings,error=NULL) },ecae_backend_error=function(e) list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="did",version=EXPECTED_PACKAGE_VERSION,ok=FALSE,result=NULL,warnings=list(),error=list(code=e$code,message=e$message,details=e$details)),error=function(e) list(schema_version="1.0.0",backend_id=BACKEND_ID,candidate_id=CANDIDATE_ID,package="did",version=EXPECTED_PACKAGE_VERSION,ok=FALSE,result=NULL,warnings=list(),error=list(code="BACKEND_INTERNAL_ERROR",message=conditionMessage(e),details=NULL)))
emit(response)
