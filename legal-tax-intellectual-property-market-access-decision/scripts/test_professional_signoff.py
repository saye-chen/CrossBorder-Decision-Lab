#!/usr/bin/env python3
import importlib.util,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]; s=importlib.util.spec_from_file_location("v",R/"scripts/validate_professional_signoff.py"); v=importlib.util.module_from_spec(s); s.loader.exec_module(v)
class T(unittest.TestCase):
 def test_template_fails_closed(self): self.assertTrue(v.validate(json.loads((R/"evaluations/qualified-professional-signoff-template.json").read_text()),"2026-08-05T00:00:00Z"))
 def test_valid_bounded_signoff(self):
  x=json.loads((R/"evaluations/qualified-professional-signoff-template.json").read_text()); x.update(reviewer_identity_ref="reviewer:1",professional_role="licensed counsel",credential_authority="bar",credential_identifier_ref="credential:1",decision="approved",evidence_index_hash="a"*64,credential_verified_at="2026-08-03T00:00:00Z",signed_at="2026-08-04T00:00:00Z",signature_ref="signature:1"); x["jurisdictions"]=["US-CA"];x["object_refs"]=["P1@v2"];x["intended_uses"]=["market_entry"];x["credential_scope"]=["legal_market_access"]; self.assertEqual(v.validate(x,"2026-08-05T00:00:00Z"),[])
 def test_scope_and_time_mismatch_block(self):
  x=json.loads((R/"evaluations/qualified-professional-signoff-template.json").read_text());x["credential_scope"]=["tax"];x["credential_verified_at"]="2026-08-04T00:00:00Z";x["signed_at"]="2026-08-03T00:00:00Z";e=v.validate(x,"2026-08-05T00:00:00Z");self.assertIn("credential scope does not cover review topic",e);self.assertIn("signature predates credential verification",e)
if __name__=="__main__": unittest.main(verbosity=2)
