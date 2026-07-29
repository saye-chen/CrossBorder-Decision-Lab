#!/usr/bin/env python3
from __future__ import annotations
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib, json, math

RUNTIME="SPPQ-2026.07"
DECISIONS={"supplier_selection","procurement_commitment","sample_approval","production_release","batch_quality_release","supplier_recovery_exit"}

class ModelError(ValueError): pass
def dec(v):
    try: return Decimal(str(v))
    except (InvalidOperation,ValueError,TypeError): raise ModelError(f"invalid_decimal:{v}")
def q(v, places="0.0001"): return str(dec(v).quantize(Decimal(places),rounding=ROUND_HALF_UP))
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def require(cond,msg):
    if not cond: raise ModelError(msg)

def normalize_quote(d):
    require(d.get("currency") and dec(d.get("fx_rate",0))>0,"currency_or_fx_missing")
    qty=dec(d.get("quantity",0)); require(qty>0,"quantity_must_be_positive")
    unit=dec(d.get("unit_price",0)); require(unit>=0,"unit_price_negative")
    extras=sum((dec(x) for x in d.get("extra_costs",[])),Decimal("0"))
    total=unit*qty+extras
    return {"base_currency_unit_cost":q(total*dec(d["fx_rate"])/qty),"base_currency_total":q(total*dec(d["fx_rate"]))}

def bom_rollup(d):
    rows=d.get("components",[]); require(rows,"components_required")
    total=Decimal("0")
    for row in rows:
        quantity=dec(row.get("quantity",0)); cost=dec(row.get("unit_cost",0)); scrap=dec(row.get("scrap_rate",0))
        require(quantity>=0 and cost>=0 and Decimal("0")<=scrap<Decimal("1"),"invalid_bom_component")
        total += quantity*cost/(Decimal("1")-scrap)
    return {"bom_cost":q(total),"component_count":len(rows)}

def should_cost(d):
    require(d.get("currency") and d.get("unit") and d.get("as_of_time"),"cost_context_required")
    keys=("direct_material","direct_labor","machine_process","manufacturing_overhead","packaging_testing","risk_allowance")
    require(all(k in d for k in keys),"should_cost_components_required")
    values={k:dec(d[k]) for k in keys};require(all(v>=0 for v in values.values()),"negative_should_cost_component")
    volume=dec(d.get("volume",1));require(volume>0,"volume_must_be_positive")
    selected_tier=None;material_multiplier=Decimal("1");labor_efficiency=Decimal("1")
    tiers=sorted(d.get("volume_tiers",[]),key=lambda row:dec(row.get("min_quantity",0)))
    for row in tiers:
        minimum=dec(row.get("min_quantity",0));require(minimum>=0,"invalid_volume_tier")
        if volume>=minimum:
            material_multiplier=dec(row.get("material_multiplier",1))
            labor_efficiency=dec(row.get("labor_efficiency",1))
            require(material_multiplier>0 and labor_efficiency>0,"invalid_volume_tier_multiplier")
            selected_tier=str(row.get("id",minimum))
    adjusted={**values}
    adjusted["direct_material"]=values["direct_material"]*material_multiplier
    adjusted["direct_labor"]=values["direct_labor"]/labor_efficiency
    tooling=dec(d.get("tooling_cost",0));tooling_units=dec(d.get("tooling_amortization_units",volume))
    depreciation=dec(d.get("equipment_depreciation",0));depreciation_units=dec(d.get("depreciation_units",volume))
    require(tooling>=0 and depreciation>=0 and tooling_units>0 and depreciation_units>0,"invalid_amortization")
    tooling_per_unit=tooling/tooling_units;depreciation_per_unit=depreciation/depreciation_units
    base=sum(adjusted.values(),Decimal("0"))+tooling_per_unit+depreciation_per_unit
    margin=dec(d.get("reasonable_margin_rate",0));require(Decimal("0")<=margin<Decimal("1"),"invalid_margin_rate")
    uncertainty=d.get("uncertainty",{})
    low_rate=dec(uncertainty.get("downside_rate",0));high_rate=dec(uncertainty.get("upside_rate",0))
    require(Decimal("0")<=low_rate<1 and high_rate>=0,"invalid_uncertainty_rate")
    estimate=base*(Decimal("1")+margin)
    return {"currency":d["currency"],"unit":d["unit"],"as_of_time":d["as_of_time"],"cost_before_margin":q(base),"should_cost":q(estimate),"low_case":q(estimate*(Decimal("1")-low_rate)),"high_case":q(estimate*(Decimal("1")+high_rate)),"tooling_amortization_per_unit":q(tooling_per_unit),"depreciation_per_unit":q(depreciation_per_unit),"selected_volume_tier":selected_tier,"component_count":len(keys)+2,"is_supplier_actual_cost":False}

def total_cost_of_ownership(d):
    require(d.get("currency") and d.get("unit") and d.get("as_of_time"),"cost_context_required")
    require(d.get("d06_inputs_accepted") is True and d.get("d07_inputs_accepted") is True,"economic_or_logistics_owner_input_not_accepted")
    keys=("purchase","inspection","quality_failure","delay","switch_exit")
    require(all(k in d for k in keys),"tco_components_required")
    costs={k:dec(d[k]) for k in keys};require(all(v>=0 for v in costs.values()),"negative_tco_component")
    logistics=dec(d.get("logistics",0));duties=dec(d.get("duties_taxes",0))
    require(logistics>=0 and duties>=0,"negative_logistics_or_duties")
    financing_base=dec(d.get("financing_base",costs["purchase"]))
    annual_rate=dec(d.get("annual_financing_rate",0));days=dec(d.get("payment_to_recovery_days",0))
    require(financing_base>=0 and annual_rate>=0 and days>=0,"invalid_financing_input")
    financing=financing_base*annual_rate*days/Decimal("365")
    events=d.get("tail_events",[]);mode=d.get("tail_event_mode")
    if events:require(mode in {"mutually_exclusive","independent"},"tail_event_mode_required")
    event_loss=Decimal("0");probability_by_group={}
    for event in events:
        probability=dec(event.get("probability",-1));loss=dec(event.get("loss",-1))
        require(event.get("event_id") and Decimal("0")<=probability<=1 and loss>=0,"invalid_tail_event")
        group=str(event.get("group","default"))
        probability_by_group[group]=probability_by_group.get(group,Decimal("0"))+probability
        event_loss+=probability*loss
    if mode=="mutually_exclusive":require(all(total<=1 for total in probability_by_group.values()),"mutually_exclusive_probability_exceeds_one")
    recoverable=dec(d.get("recoverable_value",0));require(recoverable>=0,"negative_recoverable_value")
    total=sum(costs.values(),Decimal("0"))+logistics+duties+financing+event_loss-recoverable
    require(total>=0,"recoverable_value_exceeds_cost")
    return {"currency":d["currency"],"unit":d["unit"],"as_of_time":d["as_of_time"],"total_cost_of_ownership":q(total),"financing_cost":q(financing),"expected_tail_loss":q(event_loss),"tail_event_mode":mode,"logistics":q(logistics),"duties_taxes":q(duties),"recoverable_value":q(recoverable),"logistics_and_cash_require_owner_inputs":True}

def capacity(d):
    hours=dec(d.get("available_hours",0)); rate=dec(d.get("units_per_hour",0)); yield_rate=dec(d.get("yield_rate",0))
    changeover=dec(d.get("changeover_hours",0)); uptime=dec(d.get("uptime_rate",0))
    require(hours>0 and rate>0 and Decimal("0")<yield_rate<=1 and Decimal("0")<uptime<=1,"invalid_capacity_input")
    require(Decimal("0")<=changeover<hours,"invalid_changeover")
    effective=(hours-changeover)*rate*yield_rate*uptime
    demand=dec(d.get("demand",0)); require(demand>=0,"invalid_demand")
    return {"effective_capacity":q(effective),"capacity_gap":q(effective-demand),"feasible":effective>=demand}

def lead_time(d):
    stages=[dec(x) for x in d.get("stage_days",[])]; require(stages and all(x>=0 for x in stages),"invalid_stage_days")
    buffer=dec(d.get("risk_buffer_days",0)); require(buffer>=0,"invalid_buffer")
    return {"committed_lead_time_days":q(sum(stages,Decimal("0"))+buffer)}

def concentration(d):
    shares=[dec(x) for x in d.get("shares",[])]; require(shares and all(x>=0 for x in shares),"invalid_shares")
    total=sum(shares,Decimal("0")); require(abs(total-1)<=Decimal("0.0001"),"shares_must_sum_to_one")
    return {"hhi":q(sum((x*x for x in shares),Decimal("0"))),"single_source":len([x for x in shares if x>0])==1}

def process_capability(d):
    require(d.get("measurement_system_acceptable") is True,"measurement_system_not_acceptable")
    require(d.get("process_stable") is True,"process_not_stable")
    mean=dec(d["mean"]); sigma=dec(d["sigma"]); lsl=dec(d["lsl"]); usl=dec(d["usl"])
    require(sigma>0 and usl>lsl,"invalid_capability_input")
    cp=(usl-lsl)/(Decimal("6")*sigma); cpk=min((usl-mean)/(Decimal("3")*sigma),(mean-lsl)/(Decimal("3")*sigma))
    return {"cp":q(cp),"cpk":q(cpk)}

def sampling(d):
    require(d.get("lot_id") and int(d.get("lot_size",0))>0 and d.get("sampling_plan_id") and d.get("defect_class"),"sampling_context_required")
    require(d.get("sample_representative") is True and d.get("random_selection") is True,"sampling_chain_not_representative")
    sample=int(d.get("sample_size",0)); defects=int(d.get("defects",0)); accept=int(d.get("accept_number",-1))
    reject=int(d.get("reject_number",-1))
    critical=int(d.get("critical_defects",0))
    require(sample>0 and sample<=int(d["lot_size"]) and 0<=defects<=sample and accept>=0 and reject==accept+1 and critical>=0,"invalid_sampling_input")
    passed=critical==0 and defects<=accept
    return {"decision":"accept" if passed else "reject","observed_defect_rate":q(Decimal(defects)/Decimal(sample)),"zero_defect_claim":False}

def quantity_reconciliation(d):
    require(all(k in d for k in ("input","qualified","nonconforming","rework","scrapped","wip","explained_variance")),"quantity_components_required")
    inp=dec(d.get("input",0)); parts=sum((dec(d.get(k,0)) for k in ("qualified","nonconforming","rework","scrapped","wip","explained_variance")),Decimal("0"))
    require(inp>=0 and parts>=0,"negative_quantity")
    return {"balanced":inp==parts,"difference":q(inp-parts)}

def supplier_gate(d):
    failures=[]
    for key in ("identity_verified","facility_verified","evidence_traceable","conflicts_disclosed","segregation_of_duties"):
        if d.get(key) is not True: failures.append(key)
    if d.get("critical_redline"): failures.append("critical_redline")
    return {"status":"blocked" if failures else "validated","failures":failures}

def measurement_system(d):
    variation=dec(d.get("study_variation",0)); tolerance=dec(d.get("tolerance",0))
    require(variation>=0 and tolerance>0,"invalid_measurement_input")
    ratio=variation/tolerance
    process_variation=d.get("process_variation")
    ndc=None
    if process_variation is not None:
        process=dec(process_variation);require(process>0 and variation>0,"invalid_process_variation")
        ndc=int((Decimal("1.41")*process/variation).to_integral_value(rounding="ROUND_FLOOR"))
    return {"variation_to_tolerance":q(ratio),"ndc":ndc,"acceptable":ratio<=Decimal("0.1") and (ndc is None or ndc>=5),"conditional":Decimal("0.1")<ratio<=Decimal("0.3")}

def process_stability(d):
    values=[dec(x) for x in d.get("values",[])]; require(len(values)>=5,"minimum_five_observations")
    center=sum(values,Decimal("0"))/Decimal(len(values)); span=max(values)-min(values)
    moving_ranges=[abs(values[i]-values[i-1]) for i in range(1,len(values))]
    mrbar=sum(moving_ranges,Decimal("0"))/Decimal(len(moving_ranges))
    sigma=mrbar/Decimal("1.128")
    ucl=center+Decimal("3")*sigma;lcl=center-Decimal("3")*sigma
    outside=[i for i,value in enumerate(values) if value>ucl or value<lcl]
    trend_windows=[]
    for start in range(0,len(values)-5):
        window=values[start:start+6]
        if all(window[i]>window[i-1] for i in range(1,6)) or all(window[i]<window[i-1] for i in range(1,6)):
            trend_windows.append([start,start+5])
    trend=bool(trend_windows)
    limit=dec(d.get("max_range",0)); require(limit>0,"max_range_required")
    return {"center":q(center),"range":q(span),"estimated_sigma":q(sigma),"individual_ucl":q(ucl),"individual_lcl":q(lcl),"special_cause_points":outside,"trend_windows":trend_windows,"monotonic_trend":trend,"stable":span<=limit and not outside and not trend,"specification_limit_used_as_control_limit":False}

def fmea(d):
    severity=int(d.get("severity",0)); occurrence=int(d.get("occurrence",0)); detection=int(d.get("detection",0))
    require(all(1<=x<=10 for x in (severity,occurrence,detection)),"invalid_fmea_scale")
    rpn=severity*occurrence*detection
    return {"rpn":rpn,"hard_redline":severity>=9,"priority":"critical" if severity>=9 else "high" if rpn>=200 else "controlled"}

def escape_risk(d):
    sample=dec(d.get("sample_size",0)); defects=dec(d.get("defects",0)); require(sample>0 and 0<=defects<=sample,"invalid_escape_input")
    upper_95=min(Decimal("1"),(defects+Decimal("3"))/sample)
    return {"observed_rate":q(defects/sample),"approximate_upper_95_rate":q(upper_95),"residual_risk":"nonzero","zero_defect_claim":False}

def cost_of_quality(d):
    keys=("prevention","appraisal","internal_failure","external_failure","recall")
    require(all(k in d for k in keys),"quality_cost_components_required")
    values={k:dec(d.get(k,0)) for k in keys};require(all(v>=0 for v in values.values()),"negative_quality_cost")
    total=sum(values.values(),Decimal("0"))
    return {"total_cost_of_quality":q(total),"external_failure_included":True,"recall_included":True}

def reliability(d):
    hours=dec(d.get("test_hours",0));failures=dec(d.get("failures",0));require(hours>0 and 0<=failures<=hours,"invalid_reliability_input")
    rate=failures/hours
    upper_95=(failures+Decimal("3"))/hours
    return {"observed_failure_rate_per_hour":q(rate),"approximate_upper_95_failure_rate":q(upper_95),"mtbf_observed":None if failures==0 else q(hours/failures),"zero_failure_proves_zero_risk":False}

def delivery_reliability(d):
    total=int(d.get("orders",0));on_time=int(d.get("on_time_in_full",0));require(total>0 and 0<=on_time<=total,"invalid_delivery_input")
    return {"otif":q(Decimal(on_time)/Decimal(total)),"orders":total}

def recovery_choice(d):
    rows=d.get("options",[]);require(rows,"recovery_options_required")
    feasible=[x for x in rows if x.get("feasible") is True]
    require(feasible,"no_feasible_recovery")
    for x in feasible: require(dec(x.get("loss",0))>=0 and dec(x.get("days",0))>=0,"invalid_recovery_option")
    chosen=min(feasible,key=lambda x:(dec(x["loss"]),dec(x["days"]),str(x["id"])))
    return {"selected_option":chosen["id"],"residual_risk":chosen.get("residual_risk","unknown")}

def scenario_gate(d):
    failures=[];warnings=[];preserved=list(d.get("independent_results",[]))
    checks=(
        ("identity_match","identity_conflict"),
        ("facility_disclosed","undisclosed_subcontract"),
        ("sources_independent","correlated_supply_sources"),
        ("material_matches_approved","unapproved_material_change"),
        ("sample_representative","sample_not_representative"),
        ("measurement_acceptable","measurement_system_failure"),
        ("batch_lineage_complete","batch_lineage_break"),
        ("quantity_balanced","quantity_not_conserved"),
        ("segregation_of_duties","self_approval"),
        ("current_version","stale_or_concurrent_version"),
    )
    for field,code in checks:
        if d.get(field,True) is not True:failures.append(code)
    if int(d.get("critical_defects",0))>0:failures.append("critical_defect")
    if d.get("capacity_feasible",True) is not True:failures.append("capacity_overload")
    if d.get("compliance_required") and d.get("compliance_gate")!="passed":failures.append("compliance_gate_missing")
    if d.get("capa_recurrence"):failures.append("capa_not_effective")
    if d.get("bypass_requested"):failures.append("gate_bypass_requested")
    if d.get("evidence_conflict"):warnings.append("evidence_conflict_requires_review")
    return {"status":"blocked" if failures else "inconclusive" if warnings else "validated","failures":failures,"warnings":warnings,"preserved_results":preserved}

ROUTES={"quote_normalization":normalize_quote,"bom_rollup":bom_rollup,"should_cost":should_cost,"total_cost_of_ownership":total_cost_of_ownership,"capacity":capacity,"lead_time":lead_time,"concentration":concentration,"measurement_system":measurement_system,"process_stability":process_stability,"process_capability":process_capability,"fmea":fmea,"sampling":sampling,"escape_risk":escape_risk,"cost_of_quality":cost_of_quality,"reliability":reliability,"delivery_reliability":delivery_reliability,"recovery_choice":recovery_choice,"quantity_reconciliation":quantity_reconciliation,"supplier_gate":supplier_gate,"scenario_gate":scenario_gate}
def evaluate(payload):
    route=payload.get("model"); require(route in ROUTES,"unknown_model")
    result=ROUTES[route](payload.get("input",{}))
    return {"runtime_version":RUNTIME,"model":route,"input_hash":digest(payload.get("input",{})),"output":result,"output_hash":digest(result)}
