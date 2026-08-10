import copy
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from ecae_common import ECAEError
from run_scientific_backend import validate_backend_output


def backend():
    return {"backend_id":"cluster_inference","selected_candidate_id":"cluster_cr2_clubsandwich","package":"clubSandwich","version":"0.7.0"}


def output():
    return {"schema_version":"1.0.0","backend_id":"cluster_inference","candidate_id":"cluster_cr2_clubsandwich","package":"clubSandwich","version":"0.7.0","ok":True,"result":{"effect":1.0},"warnings":[]}


class BackendRunnerTests(unittest.TestCase):
    def test_verified_output_binding_passes(self):
        self.assertEqual(validate_backend_output(output(),backend())["result"]["effect"],1.0)

    def test_version_drift_is_rejected(self):
        value=output(); value["version"]="0.7.1"
        with self.assertRaises(ECAEError) as context: validate_backend_output(value,backend())
        self.assertEqual(context.exception.code,"BACKEND_OUTPUT_BINDING_MISMATCH")

    def test_backend_reported_failure_is_not_returned_as_result(self):
        value=output(); value.update({"ok":False,"result":None,"error":{"code":"SINGULAR","message":"design is singular"}})
        with self.assertRaises(ECAEError) as context: validate_backend_output(value,backend())
        self.assertEqual(context.exception.code,"BACKEND_EXECUTION_REPORTED_FAILURE")

    def test_non_finite_backend_output_is_rejected(self):
        value=output(); value["result"]["effect"]=float("nan")
        with self.assertRaises(ECAEError) as context: validate_backend_output(value,backend())
        self.assertEqual(context.exception.code,"NON_FINITE_NUMBER")

    def test_backend_binding_mutation_matrix_is_rejected(self):
        mutations={
            "backend_id":("other_backend","BACKEND_OUTPUT_BINDING_MISMATCH"),
            "candidate_id":("other_candidate","BACKEND_OUTPUT_BINDING_MISMATCH"),
            "package":("other_package","BACKEND_OUTPUT_BINDING_MISMATCH"),
            "version":("99.0.0","BACKEND_OUTPUT_BINDING_MISMATCH"),
            "schema_version":("99.0.0","SCHEMA_VALIDATION_FAILED"),
        }
        for field,(mutated,expected) in mutations.items():
            with self.subTest(field=field):
                value=copy.deepcopy(output()); value[field]=mutated
                with self.assertRaises(ECAEError) as context: validate_backend_output(value,backend())
                self.assertEqual(context.exception.code,expected)


if __name__=="__main__": unittest.main()
