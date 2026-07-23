#!/usr/bin/env python3
"""MBCM real-skill packet, sovereignty, partial failure and blueprint traceability tests."""
from __future__ import annotations
import json, pathlib, subprocess, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
MBCM=ROOT/"marketing-brand-campaign-management"

class MBCMIntegration(unittest.TestCase):
    def test_real_eight_skill_routes_are_explicit(self):
        skill=(MBCM/"SKILL.md").read_text()
        protocol=(MBCM/"references/skill-integration-protocol.md").read_text()
        for token in ("CIDM","CIM","LIFD","PLCO","AAMO","CAPM","VLB","CIG"):
            self.assertIn(token,skill); self.assertIn(token,protocol)
        for forbidden in ("广告内部预算","达人筛选","个人客户"):
            self.assertIn(forbidden,skill)
    def test_validated_packet_is_actionable_but_proposed_is_not(self):
        base={"packet_id":"P1","packet_version":"v1","source_domain":"AAMO","source_runtime":"AAMO-2026.08",
          "target_domain":"MBCM","object":{"object_id":"O1"},"status":"validated","evidence":[],"calculations":[],
          "allowed_uses":["channel_direction"],"forbidden_uses":["ad_bid"],"lineage":{"decision_id":"D1"}}
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/"p.json"
            for status,actionable in (("validated",True),("proposed",False),("withdrawn",False)):
                p.write_text(json.dumps({**base,"status":status}))
                r=subprocess.run(["python3",str(MBCM/"scripts/validate_handoff_packet.py"),str(p)],capture_output=True,text=True)
                self.assertEqual(r.returncode,0,r.stderr)
                self.assertEqual(json.loads(r.stdout)["result"]["actionable"],actionable)
    def test_partial_failure_is_local_and_common_redline_is_global(self):
        catalog=json.loads((MBCM/"evaluations/fixtures/evaluation-catalog.json").read_text())
        adversarial=[x for x in catalog["cases"] if x["mode"]=="adversarial"]
        self.assertEqual(len(adversarial),8)
        protocol=(MBCM/"references/skill-integration-protocol.md").read_text()
        self.assertIn("只撤回依赖该输入的主张",protocol)
        self.assertIn("共同身份、法律、财务、容量或授权红线扩大阻断",protocol)
    def test_sixteen_sovereignty_mechanisms_are_represented(self):
        catalog=json.loads((MBCM/"evaluations/fixtures/evaluation-catalog.json").read_text())
        cross=[x for x in catalog["cases"] if x["mode"]=="cross_skill"]
        self.assertEqual(len(cross),28)
        participants={p for x in cross for p in x["participants"]}
        self.assertTrue({"CIDM","CIM","LIFD","PLCO","AAMO","CAPM","VLB","CIG","D05","D06","D14","F01"}.issubset(participants))
    def test_blueprint_manifest_has_only_external_l4_open(self):
        m=json.loads((ROOT/"governance/mbcm-blueprint-implementation-manifest.json").read_text())
        statuses={x["status"] for x in m["requirements"]}
        self.assertEqual(statuses,{"fixed","controlled_external_gate"})
        external=[x for x in m["requirements"] if x["status"]=="controlled_external_gate"]
        self.assertEqual([x["id"] for x in external],["D12-L4"])
        self.assertEqual(m["blueprint"]["sha256"],"44f2b44160de407f0035c195cab7d5dc5af339c1f6febf88cd92ae065524580e")
    def test_maturity_is_controlled_pilot_with_zero_replays(self):
        ledger=json.loads((ROOT/"governance/domain-maturity-status.json").read_text())
        row=next(x for x in ledger["domains"] if x["skill"]=="marketing-brand-campaign-management")
        self.assertEqual((row["runtime"],row["maturity"],row["authorized_real_cases"]),("MBCM-2026.01","controlled pilot",0))
        replay=json.loads((MBCM/"evaluations/historical-replay-template.json").read_text())
        self.assertFalse(replay["production_ready"]); self.assertEqual(replay["cases"],[])

    def test_historical_replay_rejects_fake_booleans_duplicates_and_bad_hashes(self):
        base={"production_ready":False,"cases":[{"case_id":"R1","authorized":True,"deidentified":True,
          "decision":{},"action":{},"execution_version":"v1","mature_outcome":{"contribution":1},
          "evidence_hashes":["sha256:"+"a"*64],"independent_review":True,"scenario_type":"failure"}]}
        with tempfile.TemporaryDirectory() as td:
            path=pathlib.Path(td)/"replay.json"
            for bad in (
                {**base,"cases":[{**base["cases"][0],"authorized":"true"}]},
                {**base,"cases":[base["cases"][0],base["cases"][0]]},
                {**base,"cases":[{**base["cases"][0],"evidence_hashes":["not-a-hash"]}]},
            ):
                path.write_text(json.dumps(bad))
                result=subprocess.run(["python3",str(MBCM/"scripts/validate_historical_replay.py"),str(path)],
                                      capture_output=True,text=True)
                self.assertEqual(result.returncode,2,(result.stdout,result.stderr))

if __name__=="__main__": unittest.main(verbosity=2)
