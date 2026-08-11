import json
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from ecae_common import ECAEError
from validate_schema import validate_object


class SchemaTests(unittest.TestCase):
    def test_all_schema_documents_are_meta_valid(self):
        from jsonschema.validators import validator_for
        paths=list((ROOT/"schemas").glob("*.json"))
        self.assertGreaterEqual(len(paths),20)
        for path in paths:
            schema=json.loads(path.read_text())
            validator_for(schema).check_schema(schema)

    def test_valid_causal_question(self):
        value=json.loads((ROOT/"examples/valid/causal-question.json").read_text())
        result=validate_object(value,"causal-question.schema.json")
        self.assertTrue(result["valid"])

    def test_unknown_semantics_cannot_carry_value(self):
        value=json.loads((ROOT/"examples/valid/causal-question.json").read_text())
        value["minimum_important_effect"]={"state":"unknown","value":0,"reason":"unknown"}
        with self.assertRaises(ECAEError) as context:
            validate_object(value,"causal-question.schema.json")
        self.assertEqual(context.exception.code,"SCHEMA_VALIDATION_FAILED")

    def test_known_semantics_requires_value(self):
        value=json.loads((ROOT/"examples/valid/causal-question.json").read_text())
        value["minimum_important_effect"]={"state":"known","reason":"not enough"}
        with self.assertRaises(ECAEError):
            validate_object(value,"causal-question.schema.json")

    def test_known_semantics_rejects_null(self):
        value=json.loads((ROOT/"examples/valid/causal-question.json").read_text())
        value["minimum_important_effect"]={"state":"known","value":None}
        with self.assertRaises(ECAEError):
            validate_object(value,"causal-question.schema.json")


if __name__=="__main__": unittest.main()
