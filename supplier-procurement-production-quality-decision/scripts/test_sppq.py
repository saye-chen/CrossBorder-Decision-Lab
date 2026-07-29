#!/usr/bin/env python3
import importlib.util,json,pathlib,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
core=load("core",ROOT/"scripts/sppq_core.py");contract=load("contract",ROOT/"scripts/validate_decision_contract.py");continuity=load("continuity",ROOT/"scripts/update_continuous_decision.py");cross=load("cross",ROOT/"scripts/validate_cross_domain_envelope.py");report_validator=load("report",ROOT/"scripts/validate_professional_report.py");dirty=load("dirty",ROOT/"scripts/normalize_dirty_inputs.py");engines=load("engines",ROOT/"scripts/decision_engines.py");oracle=load("oracle",ROOT/"scripts/independent_oracles.py")
COST_CONTEXT={"currency":"USD","unit":"piece","as_of_time":"2026-07-29T00:00:00Z"}
OWNER_CONTEXT={**COST_CONTEXT,"d06_inputs_accepted":True,"d07_inputs_accepted":True}
SAMPLE_CONTEXT={"lot_id":"L1","lot_size":1000,"sampling_plan_id":"PLAN-1","defect_class":"major","sample_representative":True,"random_selection":True,"reject_number":2}
class SPPQTest(unittest.TestCase):
 def test_quote(self): self.assertEqual(core.normalize_quote({"currency":"CNY","fx_rate":"0.14","quantity":"100","unit_price":"10","extra_costs":["100"]})["base_currency_total"],"154.0000")
 def test_bom(self): self.assertEqual(core.bom_rollup({"components":[{"quantity":2,"unit_cost":3,"scrap_rate":0}]})["bom_cost"],"6.0000")
 def test_should_cost(self): self.assertEqual(core.should_cost({**COST_CONTEXT,"direct_material":5,"direct_labor":2,"machine_process":1,"manufacturing_overhead":1,"packaging_testing":.5,"risk_allowance":.5,"reasonable_margin_rate":.1})["should_cost"],"11.0000")
 def test_should_cost_is_not_actual_cost(self): self.assertFalse(core.should_cost({**COST_CONTEXT,"direct_material":5,"direct_labor":2,"machine_process":1,"manufacturing_overhead":1,"packaging_testing":.5,"risk_allowance":.5})["is_supplier_actual_cost"])
 def test_should_cost_volume_tier_and_amortization(self):
  out=core.should_cost({**COST_CONTEXT,"direct_material":5,"direct_labor":2,"machine_process":1,"manufacturing_overhead":1,"packaging_testing":.5,"risk_allowance":.5,"volume":1000,"tooling_cost":1000,"tooling_amortization_units":1000,"equipment_depreciation":500,"depreciation_units":1000,"volume_tiers":[{"id":"base","min_quantity":1},{"id":"scale","min_quantity":500,"material_multiplier":.9,"labor_efficiency":1.25}],"uncertainty":{"downside_rate":.1,"upside_rate":.2}})
  self.assertEqual(out["selected_volume_tier"],"scale");self.assertEqual(out["tooling_amortization_per_unit"],"1.0000");self.assertLess(core.dec(out["low_case"]),core.dec(out["should_cost"]));self.assertGreater(core.dec(out["high_case"]),core.dec(out["should_cost"]))
 def test_tco(self): self.assertEqual(core.total_cost_of_ownership({**OWNER_CONTEXT,"purchase":100,"inspection":3,"quality_failure":7,"delay":5,"switch_exit":10,"recoverable_value":2})["total_cost_of_ownership"],"123.0000")
 def test_tco_financing_and_tail_loss(self):
  out=core.total_cost_of_ownership({**OWNER_CONTEXT,"purchase":100,"inspection":3,"quality_failure":7,"delay":5,"switch_exit":10,"logistics":8,"duties_taxes":2,"annual_financing_rate":.12,"payment_to_recovery_days":30,"tail_event_mode":"mutually_exclusive","tail_events":[{"event_id":"late","group":"delivery","probability":.1,"loss":50}],"recoverable_value":2})
  self.assertEqual(out["expected_tail_loss"],"5.0000");self.assertGreater(core.dec(out["financing_cost"]),0);self.assertGreater(core.dec(out["total_cost_of_ownership"]),core.dec("138"))
 def test_tco_missing_component_rejected(self):
  with self.assertRaisesRegex(core.ModelError,"cost_context_required"):core.total_cost_of_ownership({})
 def test_tco_overlapping_probability_rejected(self):
  with self.assertRaisesRegex(core.ModelError,"probability_exceeds_one"):core.total_cost_of_ownership({**OWNER_CONTEXT,"purchase":100,"inspection":1,"quality_failure":1,"delay":1,"switch_exit":1,"tail_event_mode":"mutually_exclusive","tail_events":[{"event_id":"a","group":"incident","probability":.8,"loss":100},{"event_id":"b","group":"incident","probability":.8,"loss":100}]})
 def test_dirty_input_normalizes_explicit_units(self):
  out=dirty.normalize_record({"field_specs":{"quantity":{"unit":"pcs"},"defect_rate":{"type":"percent"}},"record":{"quantity":"1,200 pcs","defect_rate":"10%"}})
  self.assertEqual(out["status"],"normalized");self.assertEqual(out["normalized"],{"quantity":"1200","defect_rate":"0.1"})
 def test_dirty_input_missing_is_not_zero(self):
  out=dirty.normalize_record({"field_specs":{"quantity":{"unit":"pcs"}},"record":{"quantity":"N/A"}})
  self.assertEqual(out["status"],"blocked");self.assertEqual(out["errors"]["quantity"],"missing_is_not_zero")
 def test_dirty_input_ambiguous_percent_blocks(self):
  out=dirty.normalize_record({"field_specs":{"rate":{"type":"percent"}},"record":{"rate":"10"}})
  self.assertEqual(out["status"],"blocked");self.assertEqual(out["errors"]["rate"],"ambiguous_percent_scale")
 def test_dirty_input_unknown_field_blocks(self):
  out=dirty.normalize_record({"field_specs":{"quantity":{"unit":"pcs"}},"record":{"quantity":"10 pcs","currency":"USD"}})
  self.assertEqual(out["status"],"blocked");self.assertEqual(out["unknown_fields"],["currency"])
 def test_operator_routes_resolve_to_agent_readable_knowledge(self):
  skill=(ROOT/"SKILL.md").read_text();package=json.loads((ROOT/"evaluations/operator-routing-cases.json").read_text());cases=package["cases"]
  self.assertTrue(package["blind_review_contract"]["reviewer_must_not_be_implementer"])
  self.assertEqual(len(cases),6)
  for case in cases:
   self.assertTrue(case["forbidden_claims"],case["id"])
   for ref in case["required_references"]:
    paths=list((ROOT/"references").rglob(ref));self.assertEqual(len(paths),1,case["id"]);self.assertIn(ref,skill,case["id"])
   corpus="\n".join(path.read_text() for ref in case["required_references"] for path in (ROOT/"references").rglob(ref))
   for concept in case["required_concepts"]:self.assertIn(concept,corpus,case["id"])
 def test_real_replay_gate_cannot_be_claimed_closed(self):
  replay=json.loads((ROOT/"evaluations/historical-replay-template.json").read_text())
  self.assertFalse(replay["production_ready"]);self.assertEqual(replay["authorized_real_cases"],0);self.assertTrue(replay["closure_gate"]["non_implementer_review_required"])
 def test_capacity(self): self.assertTrue(core.capacity({"available_hours":10,"units_per_hour":10,"yield_rate":.9,"changeover_hours":1,"uptime_rate":.8,"demand":60})["feasible"])
 def test_lead(self): self.assertEqual(core.lead_time({"stage_days":[2,3,4],"risk_buffer_days":1})["committed_lead_time_days"],"10.0000")
 def test_hhi(self): self.assertEqual(core.concentration({"shares":[.5,.5]})["hhi"],"0.5000")
 def test_msa_before_capability(self):
  with self.assertRaisesRegex(core.ModelError,"measurement_system"):core.process_capability({"measurement_system_acceptable":False,"process_stable":True,"mean":10,"sigma":1,"lsl":5,"usl":15})
 def test_stability_before_capability(self):
  with self.assertRaisesRegex(core.ModelError,"process_not_stable"):core.process_capability({"measurement_system_acceptable":True,"process_stable":False,"mean":10,"sigma":1,"lsl":5,"usl":15})
 def test_capability(self): self.assertEqual(core.process_capability({"measurement_system_acceptable":True,"process_stable":True,"mean":10,"sigma":1,"lsl":4,"usl":16})["cpk"],"2.0000")
 def test_sampling_never_zero_defect_claim(self): self.assertFalse(core.sampling({**SAMPLE_CONTEXT,"sample_size":80,"defects":0,"accept_number":1,"critical_defects":0})["zero_defect_claim"])
 def test_critical_defect_rejects(self): self.assertEqual(core.sampling({**SAMPLE_CONTEXT,"sample_size":80,"defects":0,"accept_number":1,"critical_defects":1})["decision"],"reject")
 def test_sampling_without_plan_rejected(self):
  with self.assertRaisesRegex(core.ModelError,"sampling_context_required"):core.sampling({"sample_size":80,"defects":0,"accept_number":1,"critical_defects":0})
 def test_quantity_balance(self): self.assertTrue(core.quantity_reconciliation({"input":100,"qualified":90,"nonconforming":5,"rework":2,"scrapped":1,"wip":1,"explained_variance":1})["balanced"])
 def test_supplier_gate(self): self.assertEqual(core.supplier_gate({"identity_verified":True,"facility_verified":True,"evidence_traceable":True,"conflicts_disclosed":True,"segregation_of_duties":False})["status"],"blocked")
 def test_decision_requires_evidence_and_models(self):
  out=engines.decide("supplier_selection",{"identity_verified":True,"facility_verified":True,"network_disclosed":True,"evidence_traceable":True,"segregation_of_duties":True})
  self.assertEqual(out["status"],"blocked");self.assertIn("evidence_bindings_required",out["failures"]);self.assertIn("missing_model_input:capacity",out["failures"])
 def test_decision_rejects_unrelated_evidence_hash_binding(self):
  case=next(x for x in json.loads((ROOT/"evaluations/evaluation-catalog.json").read_text())["cases"] if x["group"]=="decision" and x["executable"]["expected"]=="validated")
  payload=case["executable"]["input"];model=next(iter(payload["evidence_bindings"][0]["input_hashes"]));payload["evidence_bindings"][0]["input_hashes"][model]="f"*64
  self.assertIn(f"evidence_input_hash_mismatch:{model}",engines.decide(case["decision_type"],payload)["failures"])
 def decision(self,kind="supplier_selection"):
  return {"runtime_version":"SPPQ-2026.07","erdg_contract":"ERDG-CONTRACT-2026.07","decision_id":"D1","decision_type":kind,"decision_owner":"supplier-procurement-production-quality-decision","object":{"object_id":"O1","object_version":"v1","as_of_time":"2026-07-29T00:00:00+08:00"},"status":"validated","evidence":[{"id":"E1","object_version":"v1","hash":"c"*64}],"calculations":[{"model":"capacity","input_hash":"d"*64,"output_hash":"e"*64}],"gates":{"identity":True,"sovereignty":True,"version":True,"evidence":True,"segregation":True,"external_action":False,"compliance":"not_applicable"},"lineage":{"input_hash":"a"*64,"output_hash":"b"*64},"external_write":False,"production_ready":False}
 def test_owned_contract(self): self.assertEqual(contract.validate(self.decision()),[])
 def test_validated_contract_requires_calculations(self):
  d=self.decision();d["calculations"]=[];self.assertIn("validated_requires_calculations",contract.validate(d))
 def test_compliance_fail_closed(self): self.assertIn("compliance_gate_required",contract.validate(self.decision("production_release")))
 def test_external_write_rejected(self):
  d=self.decision();d["external_write"]=True;self.assertTrue(any("external write" in x for x in contract.validate(d)))
 def test_production_claim_rejected(self):
  d=self.decision();d["production_ready"]=True;self.assertTrue(any("production_ready" in x for x in contract.validate(d)))
 def test_continuity_preserves(self):
  state={"object_id":"O","current_version":"v1","current_effective_decision":{"id":"old"},"history":[],"open_gates":[],"active_actions":[],"accepted_fields":[],"invalidated_fields":[],"recompute_scope":[]}
  out=continuity.update({"object_id":"O","expected_version":"v1","delta_type":"Recalculation","state":state,"new_version":"v2","new_decision":{"id":"new"},"changed_fields":["quote"],"all_fields":["quote","spec"],"impact_map":{"quote":["economics"]}})
  self.assertEqual(out["last_delta"]["preserved"],["spec"]);self.assertEqual(out["history"][0]["status"],"superseded")
 def test_continuity_rejects_stale_version(self):
  state={"object_id":"O","current_version":"v2","current_effective_decision":{"id":"old"},"history":[],"open_gates":[],"active_actions":[],"accepted_fields":[],"invalidated_fields":[],"recompute_scope":[]}
  with self.assertRaisesRegex(ValueError,"stale_or_concurrent_version"):continuity.update({"object_id":"O","expected_version":"v1","delta_type":"Revision","state":state,"new_version":"v3","new_decision":{"id":"new"},"changed_fields":[],"all_fields":[],"impact_map":{}})
 def test_deterministic_hash(self):
  p={"model":"lead_time","input":{"stage_days":[1,2],"risk_buffer_days":1}};self.assertEqual(core.evaluate(p),core.evaluate(p))
 def test_measurement_system(self): self.assertTrue(core.measurement_system({"study_variation":1,"tolerance":10})["acceptable"])
 def test_process_stability(self): self.assertTrue(core.process_stability({"values":[10,10.1,9.9,10,10.05],"max_range":.3})["stable"])
 def test_process_trend_is_unstable(self): self.assertFalse(core.process_stability({"values":[1,2,3,4,5,6],"max_range":10})["stable"])
 def test_local_six_point_trend_is_unstable(self): self.assertFalse(core.process_stability({"values":[10,10.1,9.9,10,10,10.01,10.02,10.03,10.04,10.05,10,10.1,9.9,10],"max_range":.3})["stable"])
 def test_fmea_severity_is_hard_redline(self): self.assertTrue(core.fmea({"severity":9,"occurrence":1,"detection":1})["hard_redline"])
 def test_escape_risk_nonzero(self): self.assertEqual(core.escape_risk({"sample_size":100,"defects":0})["residual_risk"],"nonzero")
 def test_quality_cost_includes_recall(self): self.assertEqual(core.cost_of_quality({"prevention":1,"appraisal":2,"internal_failure":3,"external_failure":4,"recall":5})["total_cost_of_quality"],"15.0000")
 def test_quality_cost_missing_component_rejected(self):
  with self.assertRaisesRegex(core.ModelError,"quality_cost_components_required"):core.cost_of_quality({})
 def test_reliability_zero_failure_not_zero_risk(self): self.assertFalse(core.reliability({"test_hours":100,"failures":0})["zero_failure_proves_zero_risk"])
 def test_delivery_reliability(self): self.assertEqual(core.delivery_reliability({"orders":10,"on_time_in_full":9})["otif"],"0.9000")
 def test_recovery_choice(self): self.assertEqual(core.recovery_choice({"options":[{"id":"A","feasible":True,"loss":10,"days":3},{"id":"B","feasible":True,"loss":9,"days":5}]})["selected_option"],"B")
 def test_cross_domain_overreach_rejected(self):
  d={"message_id":"M","source_domain":"D04","target_domain":"D01","object_id":"O","object_version":"v1","as_of_time":"2026-07-29T00:00:00Z","authority":"capital_allocation","allowed_uses":["support"],"forbidden_uses":["rewrite"],"requested_fields":["capital"],"consumer_response":"pending","accepted_fields":[],"rejection_reasons":[],"lineage":{"input_hash":"a"*64,"packet_hash":"b"*64}}
  self.assertIn("D04_authority_overreach",cross.validate(d))
 def test_cross_domain_missing_requested_fields_rejected(self):
  d={"message_id":"M","source_domain":"D04","target_domain":"D07","object_id":"O","object_version":"v1","as_of_time":"2026-07-29T00:00:00Z","authority":"supplier_quality","allowed_uses":["support"],"forbidden_uses":["rewrite"],"consumer_response":"accepted","accepted_fields":[],"rejection_reasons":[],"lineage":{"input_hash":"a"*64,"packet_hash":"b"*64}}
  self.assertTrue(any("requested_fields" in error for error in cross.validate(d)))
 def test_six_golden_reports_validate(self):
  rows=json.loads((ROOT/"evaluations/golden-professional-reports.json").read_text())["reports"];self.assertEqual(len(rows),6)
  self.assertTrue(all(not report_validator.validate(x) for x in rows))
 def test_hollow_report_rejected(self):
  row=json.loads((ROOT/"evaluations/golden-professional-reports.json").read_text())["reports"][0]
  row["professional_analysis"]["mechanisms"]=["建议优化"]
  self.assertTrue(any("missing_mechanisms" in error for error in report_validator.validate(row)))
 def test_tampered_calculation_ledger_rejected(self):
  row=json.loads((ROOT/"evaluations/golden-professional-reports.json").read_text())["reports"][0]
  row["ledgers"]["calculation"][0]["input_hash"]="tampered"
  self.assertTrue(any("invalid_calculation_hash" in error for error in report_validator.validate(row)))
 def test_arbitrary_valid_hashes_are_replayed_and_rejected(self):
  row=json.loads((ROOT/"evaluations/golden-professional-reports.json").read_text())["reports"][0]
  for calculation in row["ledgers"]["calculation"]:calculation["input_hash"]="d"*64;calculation["output_hash"]="e"*64
  self.assertTrue(any("calculation_replay_mismatch" in error for error in report_validator.validate(row)))
 def test_independent_oracle_rejects_jointly_tampered_production_result(self):
  row=json.loads((ROOT/"evaluations/golden-professional-reports.json").read_text())["reports"][0];calculation=next(x for x in row["ledgers"]["calculation"] if x["model"]=="capacity")
  original=report_validator.CORE.evaluate
  def fake(payload):
   result=original(payload)
   if payload["model"]=="capacity":result["output"]["effective_capacity"]="999.0000";result["output_hash"]=core.digest(result["output"])
   return result
  replay=fake({"model":"capacity","input":calculation["input"]});calculation.update(output=replay["output"],output_hash=replay["output_hash"])
  report_validator.CORE.evaluate=fake
  try:self.assertTrue(any("independent_oracle_mismatch" in error for error in report_validator.validate(row)))
  finally:report_validator.CORE.evaluate=original
 def test_all_18_models_match_independent_oracle(self):
  cases=json.loads((ROOT/"evaluations/evaluation-catalog.json").read_text())["cases"];valid=[x["executable"] for x in cases if x["group"]=="calculation" and x["executable"]["expected"]=="pass"]
  self.assertEqual(len({x["model"] for x in valid}),18)
  for case in valid:
   production=core.evaluate({"model":case["model"],"input":case["input"]});independent=oracle.calculate(case["model"],case["input"])
   self.assertEqual(independent,{"output":production["output"],"input_hash":production["input_hash"],"output_hash":production["output_hash"]},case["model"])
 def test_validated_report_with_blocked_gates_rejected(self):
  row=json.loads((ROOT/"evaluations/golden-professional-reports.json").read_text())["reports"][0]
  for gate in row["hard_gates"]:gate["status"]="blocked"
  self.assertTrue(any("validated_with_unpassed_gates" in error for error in report_validator.validate(row)))
 def test_validated_report_with_adverse_replayed_model_rejected(self):
  row=next(x for x in json.loads((ROOT/"evaluations/golden-professional-reports.json").read_text())["reports"] if x["decision_type"]=="production_release")
  calculation=next(x for x in row["ledgers"]["calculation"] if x["model"]=="capacity");calculation["input"]["demand"]=100
  replay=core.evaluate({"model":"capacity","input":calculation["input"]});calculation.update(input_hash=replay["input_hash"],output_hash=replay["output_hash"],output=replay["output"])
  self.assertTrue(any("validated_with_adverse_calculation" in error for error in report_validator.validate(row)))
 def test_report_rejects_evidence_not_bound_to_gate(self):
  row=json.loads((ROOT/"evaluations/golden-professional-reports.json").read_text())["reports"][0];row["ledgers"]["evidence"][0]["supports"]=[]
  self.assertTrue(any("gate_evidence_lineage_missing" in error for error in report_validator.validate(row)))
if __name__=="__main__":unittest.main(verbosity=2)
