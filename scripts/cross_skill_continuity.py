#!/usr/bin/env python3
"""Deterministic cross-domain feedback, conflict, concurrency and recovery kernel."""
from __future__ import annotations

FEEDBACK_ROUTES={
 "AAMO.outcome":{"CIDM":["investment_posture"]},
 "PLCO.conversion":{"PIPM":["product_hypothesis","specification"]},
 "CIG.voc_return":{"PIPM":["product_definition"],"SPPQ":["quality_risk"],"PLCO":["listing_content"]},
 "LIFD.fulfillment":{"CIDM":["investment_posture"],"AAMO":["spend_ceiling"],"PPFC":["cost_cash"]},
 "D05.access_change":{"PIPM":["product_definition"],"SPPQ":["production_release"],"PLCO":["claim_use"],"AAMO":["ad_claims"],"CAPM":["creator_claims"],"MBCM":["campaign_claims"]},
 "SPPQ.quality_incident":{"D05":["access_gate"],"LIFD":["inventory_disposition"],"CIG":["service_response"],"CIDM":["investment_posture"]},
 "PPFC.economic_change":{"CIDM":["investment_posture"],"AAMO":["spend_ceiling"],"CAPM":["commercial_terms"],"LIFD":["route_economics"]}}

TRANSITIONS={
 ("proposed","validated"):("activate","reaccept"),("validated","conflicted"):("freeze","recompute"),
 ("validated","expired"):("freeze","recompute"),("validated","superseded"):("replace","reaccept"),
 ("effective","withdrawn"):("stop","rollback"),("blocked","recovered"):("resume_controlled","reaccept")}

def impact(event,state):
 if event not in FEEDBACK_ROUTES: raise ValueError("unknown feedback event")
 return {d:{"invalidated":fields,"recompute":fields,"reaccept":True,"preserved":sorted(set(state)-set(fields))} for d,fields in FEEDBACK_ROUTES[event].items()}

def transition(old,new):
 if (old,new) not in TRANSITIONS: raise ValueError("illegal continuity transition")
 effect,recheck=TRANSITIONS[(old,new)]; return {"effect":effect,"required":recheck,"history_preserved":True}

def adjudicate(claims):
 eligible=[c for c in claims if c.get("object_match") and c.get("current") and c.get("reproducible")]
 if any(c.get("redline") for c in eligible): return {"state":"blocked","winner":None,"reason":"non_compensable_redline"}
 for c in eligible:c["quality_score"]=(c.get("evidence_grade",0),c.get("independent_sources",0),c.get("verified_at",''))
 ranked=sorted(eligible,key=lambda c:c["quality_score"],reverse=True)
 if not ranked:return {"state":"inconclusive","winner":None,"reason":"no_eligible_claim"}
 if len(ranked)>1 and ranked[0]["quality_score"]==ranked[1]["quality_score"] and ranked[0].get("value")!=ranked[1].get("value"):return {"state":"inconclusive","winner":None,"reason":"unresolved_peer_conflict"}
 return {"state":"validated","winner":ranked[0]["id"],"reason":"strongest_eligible_evidence"}

class Ledger:
 def __init__(self): self.current_versions={}; self.current_hashes={}; self.seen=set(); self.accepted=[]
 def receive(self,m):
  if m["message_id"] in self.seen:return "duplicate_no_op"
  self.seen.add(m["message_id"]); current=self.current_versions.get(m["object_id"],0)
  if m["version"]<current:return "late_version_ignored"
  if m["version"]==current and current and m.get("content_hash")!=self.current_hashes.get(m["object_id"]):return "same_version_conflict"
  self.current_versions[m["object_id"]]=m["version"]
  self.current_hashes[m["object_id"]]=m.get("content_hash")
  if m["status"] in {"failed","timeout","partial"}:return "preserved_partial_failure"
  self.accepted.append(m["message_id"]);return "accepted"

def recovery(blocked_requirements,closed_requirements):
 missing=sorted(set(blocked_requirements)-set(closed_requirements))
 return {"state":"recovered" if not missing else "blocked","missing":missing,"resume":"controlled" if not missing else "none"}

def partial_failure(failed_domains,claims):
 affected=sorted(c["id"] for c in claims if set(c.get("depends_on",[]))&set(failed_domains))
 preserved=sorted(c["id"] for c in claims if c["id"] not in affected and c.get("state")=="validated")
 return {"state":"partially_failed","affected":affected,"preserved":preserved,"overall_pass":False}
