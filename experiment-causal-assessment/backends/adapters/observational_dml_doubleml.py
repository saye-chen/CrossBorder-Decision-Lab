#!/usr/bin/env python3
"""JSON-only DoubleML IRM adapter; adapter existence is not verification."""

from __future__ import annotations

import importlib.metadata
import json
import math
import re
import sys

EXPECTED_VERSION="0.11.3"
BACKEND_ID="observational_dml"
CANDIDATE_ID="observational_dml_doubleml"
SAFE_NAME=re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


class AdapterError(Exception):
    def __init__(self,code,message,details=None): super().__init__(message); self.code,self.details=code,details


def finite(value,field):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value): raise AdapterError("BACKEND_REQUEST_INVALID",f"{field} must be finite numeric")
    return float(value)


def learner(name,role,seed):
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.linear_model import LogisticRegression, LinearRegression
    if role=="propensity":
        choices={"logistic":LogisticRegression(max_iter=2000,random_state=seed),"random_forest":RandomForestClassifier(n_estimators=300,min_samples_leaf=5,max_depth=8,random_state=seed,n_jobs=1)}
    else:
        choices={"linear":LinearRegression(),"random_forest":RandomForestRegressor(n_estimators=300,min_samples_leaf=5,max_depth=8,random_state=seed,n_jobs=1)}
    if name not in choices: raise AdapterError("DML_LEARNER_UNSUPPORTED",f"Unsupported {role} learner")
    return choices[name]


def run(request):
    if importlib.metadata.version("DoubleML")!=EXPECTED_VERSION: raise AdapterError("BACKEND_VERSION_MISMATCH","DoubleML version differs from adapter lock")
    import numpy as np
    import pandas as pd
    import doubleml as dml
    rows=request.get("rows")
    if not isinstance(rows,list) or len(rows)<50 or not all(isinstance(row,dict) for row in rows): raise AdapterError("BACKEND_REQUEST_INVALID","rows must contain at least 50 objects")
    names={field:request.get(field) for field in ("outcome_column","treatment_column")}
    covariates=request.get("covariate_columns")
    if any(not isinstance(v,str) or not SAFE_NAME.fullmatch(v) for v in names.values()) or not isinstance(covariates,list) or not covariates or any(not isinstance(v,str) or not SAFE_NAME.fullmatch(v) for v in covariates): raise AdapterError("BACKEND_COLUMN_INVALID","Analysis columns must be safe names")
    required=set(names.values())|set(covariates)
    if any(set(row)<required for row in rows): raise AdapterError("BACKEND_COLUMN_MISSING","Every row requires outcome treatment and covariates")
    data=pd.DataFrame(rows)
    try: data[list(required)]=data[list(required)].astype(float)
    except Exception as exc: raise AdapterError("BACKEND_REQUEST_INVALID","Analysis values must be numeric") from exc
    if not np.isfinite(data[list(required)].to_numpy()).all(): raise AdapterError("BACKEND_REQUEST_INVALID","Analysis values must be finite")
    treatment=names["treatment_column"]
    if set(data[treatment].unique())!={0.0,1.0}: raise AdapterError("DML_TREATMENT_INVALID","Treatment must contain both binary arms")
    score=request.get("score")
    score_map={"ATE":"ATE","ATT":"ATTE"}
    if score not in score_map: raise AdapterError("DML_SCORE_INVALID","score must be ATE or ATT")
    folds,repetitions,seed=request.get("folds"),request.get("repetitions"),request.get("seed")
    if not isinstance(folds,int) or isinstance(folds,bool) or not 2<=folds<=20 or not isinstance(repetitions,int) or isinstance(repetitions,bool) or not 1<=repetitions<=20 or not isinstance(seed,int) or isinstance(seed,bool) or not 0<=seed<2**32: raise AdapterError("SEED_CONTRACT_INVALID","folds repetitions or seed are invalid")
    bounds=request.get("propensity_bounds")
    if not isinstance(bounds,list) or len(bounds)!=2: raise AdapterError("PROPENSITY_BOUND_INVALID","propensity_bounds requires [lower,upper]")
    lower,upper=map(lambda x:finite(x,"propensity_bounds"),bounds)
    if not 0<lower<.5 or abs(upper-(1-lower))>1e-12: raise AdapterError("PROPENSITY_BOUND_INVALID","DoubleML adapter requires symmetric propensity bounds")
    level=finite(request.get("confidence_level",.95),"confidence_level")
    if not 0<level<1: raise AdapterError("BACKEND_CONFIDENCE_LEVEL_INVALID","confidence_level must be in (0,1)")
    np.random.seed(seed)
    ml_g=learner(request.get("outcome_learner"),"outcome",seed)
    ml_m=learner(request.get("propensity_learner"),"propensity",seed)
    obj_data=dml.DoubleMLData(data,y_col=names["outcome_column"],d_cols=treatment,x_cols=covariates)
    model=dml.DoubleMLIRM(obj_data,ml_g=ml_g,ml_m=ml_m,n_folds=folds,n_rep=repetitions,score=score_map[score],trimming_rule="truncate",trimming_threshold=lower)
    model.fit(n_jobs_cv=1,store_predictions=True)
    interval=model.confint(level=level)
    effect,se,p=float(model.coef[0]),float(model.se[0]),float(model.pval[0])
    ci_values=[float(x) for x in interval.iloc[0].tolist()]
    losses={name:np.asarray(value,dtype=float).tolist() for name,value in model.nuisance_loss.items()}
    if any(not math.isfinite(x) for x in [effect,se,p,*ci_values]) or se<0 or not 0<=p<=1 or ci_values[0]>ci_values[1]: raise AdapterError("BACKEND_NUMERICAL_INVALID","DML output failed numerical invariants")
    warnings=["observational_identification_depends_on_DAG_exchangeability_consistency_and_positivity","propensity_truncation_changes_the_effective_target_when_active","negative_controls_and_unmeasured_confounding_sensitivity_required_outside_adapter","external_parity_and_simulation_pending"]
    return {"effect":effect,"standard_error":se,"confidence_interval":{"level":level,"lower":ci_values[0],"upper":ci_values[1]},"p_value":p,"score":score,"folds":folds,"repetitions":repetitions,"seed":seed,"propensity_bounds":{"lower":lower,"upper":upper},"nuisance_loss":losses,"out_of_fold_predictions_stored":True,"warnings":warnings}


def response(ok,result=None,error=None): return {"schema_version":"1.0.0","backend_id":BACKEND_ID,"candidate_id":CANDIDATE_ID,"package":"DoubleML","version":EXPECTED_VERSION,"ok":ok,"result":result,"warnings":result.get("warnings",[]) if result else [],"error":error}
try:
    request=json.load(sys.stdin)
    if not isinstance(request,dict): raise AdapterError("BACKEND_REQUEST_INVALID","Request must be a JSON object")
    output=response(True,run(request))
except AdapterError as exc: output=response(False,error={"code":exc.code,"message":str(exc),"details":exc.details})
except Exception as exc: output=response(False,error={"code":"BACKEND_INTERNAL_ERROR","message":str(exc),"details":None})
json.dump(output,sys.stdout,allow_nan=False,separators=(",",":"))
