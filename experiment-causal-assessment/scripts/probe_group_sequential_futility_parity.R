#!/usr/bin/env Rscript

# Convention-normalized gsDesign/rpact beta-spending futility parity.

EXPECTED_GSDESIGN_VERSION <- "3.10.1"
EXPECTED_RPACT_VERSION <- "4.4.0"
BOUNDARY_TOLERANCE <- 3e-5
SPENDING_TOLERANCE <- 2e-8

if (!requireNamespace("jsonlite",quietly=TRUE)) stop("jsonlite is required")
if (!identical(utils::packageDescription("gsDesign",fields="Version"),EXPECTED_GSDESIGN_VERSION)) stop("gsDesign version mismatch")
if (!identical(utils::packageDescription("rpact",fields="Version"),EXPECTED_RPACT_VERSION)) stop("rpact version mismatch")

vector <- function(vector_id,information,binding,beta_spending,gamma=NULL) {
  gs_lower <- switch(beta_spending,pocock=gsDesign::sfLDPocock,obrien_fleming=gsDesign::sfLDOF,hwang_shih_decani=gsDesign::sfHSD)
  rpact_beta <- switch(beta_spending,pocock="bsP",obrien_fleming="bsOF",hwang_shih_decani="bsHSD")
  gs_arguments <- list(k=length(information),test.type=if(binding) 3 else 4,alpha=.025,beta=.2,timing=information[-length(information)],sfu=gsDesign::sfLDOF,sfl=gs_lower,tol=1e-6)
  rpact_arguments <- list(kMax=length(information),sided=1,alpha=.025,beta=.2,informationRates=information,typeOfDesign="asOF",typeBetaSpending=rpact_beta,bindingFutility=binding,tolerance=1e-8)
  if (!is.null(gamma)) { gs_arguments$sflpar<-gamma; rpact_arguments$gammaB<-gamma }
  gs <- do.call(gsDesign::gsDesign,gs_arguments); rp <- suppressMessages(do.call(rpact::getDesignGroupSequential,rpact_arguments))
  gs_upper <- as.numeric(gs$upper$bound); gs_lower_bound <- as.numeric(gs$lower$bound); gs_alpha <- cumsum(as.numeric(gs$upper$spend)); gs_beta <- cumsum(as.numeric(gs$lower$spend))
  rp_upper <- as.numeric(rp$criticalValues); rp_lower <- c(as.numeric(rp$futilityBounds),tail(rp_upper,1)); rp_alpha <- as.numeric(rp$alphaSpent); rp_beta_spent <- as.numeric(rp$betaSpent)
  differences <- list(upper=max(abs(gs_upper-rp_upper)),lower=max(abs(gs_lower_bound-rp_lower)),alpha=max(abs(gs_alpha-rp_alpha)),beta=max(abs(gs_beta-rp_beta_spent)))
  list(vector_id=vector_id,binding_futility=binding,beta_spending=beta_spending,information_fractions=as.list(information),gsDesign=list(upper_boundaries=as.list(gs_upper),futility_boundaries=as.list(gs_lower_bound),cumulative_alpha=as.list(gs_alpha),cumulative_beta=as.list(gs_beta)),rpact=list(upper_boundaries=as.list(rp_upper),futility_boundaries=as.list(rp_lower),cumulative_alpha=as.list(rp_alpha),cumulative_beta=as.list(rp_beta_spent)),maximum_absolute_differences=differences,accepted=differences$upper<=BOUNDARY_TOLERANCE&&differences$lower<=BOUNDARY_TOLERANCE&&differences$alpha<=SPENDING_TOLERANCE&&differences$beta<=SPENDING_TOLERANCE)
}

vectors <- list(
  vector("binding_hsd_three_looks",c(.33,.67,1),TRUE,"hwang_shih_decani",-2),
  vector("nonbinding_hsd_three_looks",c(.33,.67,1),FALSE,"hwang_shih_decani",-2),
  vector("binding_pocock_four_looks",c(.25,.5,.75,1),TRUE,"pocock"),
  vector("nonbinding_obf_four_looks",c(.25,.5,.75,1),FALSE,"obrien_fleming")
)
report <- list(schema_version="1.0.0",report_id="ECAE-WP06-GROUP-SEQUENTIAL-FUTILITY-PARITY-2026-08-10",status="development_pass_external_verification_open",qualification="development_parity_not_independent_external_verification",source_script_ref="scripts/probe_group_sequential_futility_parity.R",runtimes=list(R=as.character(getRversion()),gsDesign=EXPECTED_GSDESIGN_VERSION,rpact=EXPECTED_RPACT_VERSION),normalization=list(one_sided_alpha=.025,beta=.2,rpact_final_futility_equals_final_efficacy=TRUE,binding_test_type=3,nonbinding_test_type=4),tolerances=list(boundary=BOUNDARY_TOLERANCE,spending=SPENDING_TOLERANCE),vectors=vectors,all_vectors_accepted=all(vapply(vectors,function(x)isTRUE(x$accepted),logical(1))),release_effect=list(registry_verified=FALSE,external_review_pending=TRUE,operating_characteristic_simulation_pending=TRUE))
cat(jsonlite::toJSON(report,auto_unbox=TRUE,null="null",digits=16,pretty=TRUE))
