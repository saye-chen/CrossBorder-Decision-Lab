import json,unittest
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
class SchemaTests(unittest.TestCase):
 def test_all_schemas_valid_and_external_write_closed(self):
  schemas=list((ROOT/'schemas').glob('*.schema.json'));self.assertEqual(len(schemas),12)
  for path in schemas:
   schema=json.loads(path.read_text());Draft202012Validator.check_schema(schema)
   text=path.read_text()
   if path.name!='common-object.schema.json': self.assertTrue('external_write' in text or 'common-object.schema.json' in text,path.name)
 def test_handoff_rejects_write_and_extra(self):
  schema=json.loads((ROOT/'schemas/localization-handoff.schema.json').read_text());base={'schema_version':'1.0.0','contract':'LCCA-HANDOFF-1.0','handoff_id':'H','source_domain':'D06','target_domain':'D01','scope_ref':'S','comparability_status':'comparable','transfer_status':'L4','source_action_ceiling':'analysis_only','action_ceiling':'analysis_only','claim_upgrade_allowed':False,'limitations':[],'content_hash':'sha256:'+'a'*64,'external_write':False}
  self.assertFalse(list(Draft202012Validator(schema).iter_errors(base)));base['external_write']=True;self.assertTrue(list(Draft202012Validator(schema).iter_errors(base)))
if __name__=='__main__':unittest.main()
