#!/usr/bin/env python3
from plco_common import fail, run_cli

def evaluate(data):
    tasks=data.get("tasks",[]); modules=data.get("modules",[])
    if not tasks: fail("tasks must not be empty")
    by_id={m.get("module_id"):m for m in modules}; rows=[]
    for task in tasks:
        tid=task.get("task_id"); required=set(task.get("required_evidence",[])); covering=[]; evidence=set()
        for m in modules:
            if tid in m.get("task_ids",[]): covering.append(m.get("module_id")); evidence.update(m.get("evidence_ids",[]))
        rows.append({"task_id":tid,"modules":covering,"missing_evidence":sorted(required-evidence),"covered":bool(covering) and required.issubset(evidence)})
    return {"status":"pass" if all(r["covered"] for r in rows) else "fail","coverage":rows,"module_count":len(by_id)}
if __name__ == "__main__": run_cli(evaluate,"PLCO-task-1")
