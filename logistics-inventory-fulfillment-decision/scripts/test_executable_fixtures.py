#!/usr/bin/env python3
import json,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).parent
FIX=ROOT.parent.parent/"logistics-inventory-fulfillment-decision/evaluations/executable-fixtures.json"
REG=ROOT.parent/"references/expert-scenarios.json"

def pick(obj,path):
    for key in path.split("."): obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    return obj

class ExecutableFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle=json.loads(FIX.read_text(encoding="utf-8"));cls.registry=json.loads(REG.read_text(encoding="utf-8"))

    def test_exactly_all_registered_scenarios_are_executable(self):
        registered={x["id"] for x in self.registry};cases=[x[0] for x in self.bundle["cases"]]
        self.assertEqual(len(cases),60);self.assertEqual(len(set(cases)),60);self.assertEqual(set(cases),registered)

    def test_every_fixture_executes_and_asserts(self):
        failures=[];registry={x["id"]:x for x in self.registry}
        for case_id,profile_id in self.bundle["cases"]:
            p=self.bundle["profiles"][profile_id]
            with tempfile.TemporaryDirectory() as td:
                i=Path(td)/"in.json";o=Path(td)/"out.json";i.write_text(json.dumps(p["input"]),encoding="utf-8")
                proc=subprocess.run(["python3",str(ROOT/p["script"]),"--input",str(i),"--output",str(o)],capture_output=True,text=True)
                out=json.loads(o.read_text(encoding="utf-8"))
                if proc.returncode and not p.get("allow_error"): failures.append(f"{case_id}: process failed {out}");continue
                a=p["assert"];actual=pick(out,a["path"]);op=a["op"]
                ok=(actual==a["value"]) if op=="eq" else (actual>=pick(out,a["value"]) if op=="gte_path" else False)
                if not ok: failures.append(f"{case_id}: {a} actual={actual} output={out}")
                expected=registry[case_id]["expected_gate"]
                signal=out.get("decision",out.get("decision_gate",out.get("continuity",out.get("status"))))
                blocked=signal in {"blocked","constrain","fail","error"} or (signal=="hold" and any(not x.get("eligible",True) for x in out.get("paths",[])))
                if expected=="blocked" and not blocked: failures.append(f"{case_id}: expected blocked but signal={signal}")
                if expected=="pass" and blocked: failures.append(f"{case_id}: expected pass but signal={signal}")
        self.assertFalse(failures,"\n".join(failures))

if __name__=="__main__": unittest.main(verbosity=2)
