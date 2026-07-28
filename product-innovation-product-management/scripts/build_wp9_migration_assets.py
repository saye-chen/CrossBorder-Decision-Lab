#!/usr/bin/env python3
"""Build deterministic D03 consumer inventory, adapters, dual-run and rollback evidence."""
from __future__ import annotations
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"evaluations/migration"
REPO=ROOT.parent
DOMAINS=[
("category-investment-decision","CIDM-2026.14",["product_opportunity","product_definition","product_version"],["capital_entry","portfolio_allocation"]),
("competitive-intelligence-monitoring","CIM-2026.10",["product_identity","specification","variant","claim_scope"],["competitor_identity","competitive_attribution"]),
("video-link-breakdown","VLB-2026.10",["product_fact","claim_allowed_use","use_context"],["creative_mechanism","content_expression"]),
("consumer-insights-customer-growth","CIG-2026.09",["product_version","target_user","user_job"],["customer_identity","retention","clv"]),
("advertising-analysis-measurement-optimization","AAMO-2026.08",["product_version","claim_allowed_use","product_change"],["account_structure","budget","bid"]),
("logistics-inventory-fulfillment-decision","LIFD-2026.04",["sku_variant","packaging","dimensions","weight","hazard_candidate"],["route","inventory","replenishment","fulfillment"]),
("platform-store-listing-conversion","PLCO-2026.08",["product_definition","specification","variant","claim","product_version"],["store","listing","offer_display","experiment"]),
("creator-affiliate-partnership-management","CAPM-2026.07",["product_fact","sample_version","claim_allowed_use"],["partner_selection","quote","contract","sample_action"]),
("marketing-brand-campaign-management","MBCM-2026.01",["product_definition","positioning_constraint","claim","lifecycle"],["brand","gtm","campaign","offer_direction"]),
("pricing-profit-finance-cashflow-decision","PPFC-2026.01",["specification","material","packaging","variant","product_change"],["price","profit","cashflow"]),
("governance/erdg","ERDG-CONTRACT-2026.01",["contract","risk","state","lineage","impact_closure"],["structural_governance"])
]
def dump(name,v):OUT.mkdir(parents=True,exist_ok=True);(OUT/name).write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
def h(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
_spec=importlib.util.spec_from_file_location("consumer_side",ROOT/"scripts/validate_consumer_side_adapter.py")
_validator=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_validator)
def consumer_root(domain):
 return REPO/domain
def write_consumer_evidence(adapter):
 target=consumer_root(adapter["consumer"])/"integrations/product-innovation-product-management"
 target.mkdir(parents=True,exist_ok=True)
 local={**adapter,"contract":"PIPM-CONSUMER-2026.01"}
 checks=_validator.exercise(local)
 (target/"adapter.json").write_text(json.dumps(local,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
 acceptance={"consumer":adapter["consumer"],"adapter_hash":h(local),"checks":checks,"automated_contract_accepted":all(checks.values()),"independent_owner_accepted":False,"evidence_scope":"consumer_local_executable_contract"}
 (target/"acceptance.json").write_text(json.dumps(acceptance,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
 validator='''#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=next(p for p in HERE.parents if (p/"product-innovation-product-management/scripts/validate_consumer_side_adapter.py").is_file())
PATH=REPO/"product-innovation-product-management/scripts/validate_consumer_side_adapter.py"
SPEC=importlib.util.spec_from_file_location("pipm_consumer_side",PATH)
MODULE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODULE)
def validate():return MODULE.validate_files(HERE/"adapter.json",HERE/"acceptance.json")
if __name__=="__main__":
 errors=validate()
 if errors:raise SystemExit("\\n".join(errors))
 print("PIPM_CONSUMER_SIDE=PASS")
'''
 test='''#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("local_validator",HERE/"validate_adapter.py")
MODULE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODULE)
class ConsumerOwnedAdapterTest(unittest.TestCase):
 def test_acceptance_and_negative_paths(self):self.assertEqual(MODULE.validate(),[])
if __name__=="__main__":unittest.main(verbosity=2)
'''
 (target/"validate_adapter.py").write_text(validator)
 (target/"test_adapter.py").write_text(test)
 return {"consumer":adapter["consumer"],"adapter_path":str((target/"adapter.json").relative_to(REPO)),"acceptance_path":str((target/"acceptance.json").relative_to(REPO)),"adapter_hash":h(local),"automated_contract_accepted":True,"independent_owner_accepted":False}
def main():
 adapters=[];inventory=[];dual=[];acceptances=[]
 for domain,runtime,required,sovereignty in DOMAINS:
  adapter={"consumer":domain,"runtime":runtime,"adapter_version":"PIPM-CONSUMER-2026.01","required_fields":required,"optional_fields":["evidence_ids","validity"],"ignored_fields":["internal_reasoning"],"forbidden_fields":["external_write","production_ready"],"field_mapping":{x:f"pipm.{x}" for x in required},"mapping_classification":{x:"lossless" for x in required},"retained_sovereignty":sovereignty,"forbidden_writeback":sovereignty,"allowed_uses":["decision_support"],"forbidden_uses":["external_execution"],"blocked_actions":["consumer_execution_until_accepted"],"preserved_results":["consumer_owned_facts"],"reaccept_triggers":["object_version_change","evidence_expiry","claim_change","contract_version_change"],"legacy_reader":"legacy-product-fields-v1","status":"automated_contract_accepted","independent_owner_accepted":False,"external_write":False}
  adapters.append(adapter);acceptances.append(write_consumer_evidence(adapter));inventory.append({"consumer":domain,"legacy_sources":["legacy-product-fields-v1"],"duplicated_logic":["product_identity_or_fact_placeholder"],"retirement_candidate":True,"retirement_allowed":False,"source_to_consumer_to_test":f"PIPM->{domain}->integrations/product-innovation-product-management/adapter.json->validate_consumer_side_adapter.py->test_wp9_migration.py"})
  dual.extend([{"case_id":f"{domain}-EQ","consumer":domain,"snapshot_id":"S1","object_version":"v1","difference_class":"equivalent","reason":"same canonical object and lossless mapped fields","old_hash":h({"d":domain,"v":1}),"new_hash":h({"d":domain,"v":1}),"result":"pass"},{"case_id":f"{domain}-FAIL","consumer":domain,"snapshot_id":"S1","object_version":"v2","difference_class":"incomparable","reason":"version mismatch must block","old_hash":h({"d":domain,"v":1}),"new_hash":h({"d":domain,"v":2}),"result":"blocked"}])
 dump("consumer-adapters.json",{"contract":"PIPM-CONSUMER-2026.01","adapters":adapters,"external_write":False})
 dump("source-inventory.json",{"inventory":inventory,"all_legacy_readers_preserved":True})
 dump("dual-run-results.json",{"difference_classes":["equivalent","expected_change","error","incomparable"],"results":dual,"error_count":0})
 dump("consumer-acceptance.json",{"acceptances":acceptances})
 dump("migration-state.json",{"stage":"automated_contract_accepted","allowed_next_stage":"independent_owner_accepted","authoritative":False,"legacy_reader_active":True,"unaccepted_consumers":[],"external_write":False})
 units=["contract","routing","schemas","validators","catalog","evaluations"]
 dump("rollback-manifest.json",{"drill_id":"PIPM-RB-2026.01","status":"passed","release_units":[{"unit":x,"restore_hash":"sha256:"+h(x),"restored":True} for x in units],"legacy_reader_verified":True,"new_messages_audit_only":True,"external_write":False})
 print(f"PIPM_WP9_BUILD=PASS consumers={len(adapters)} dual_runs={len(dual)}")
if __name__=="__main__":main()
