#!/usr/bin/env python3
from plco_common import fail, run_cli

def validate(data):
    nodes=data.get("nodes",[]); ids=[n.get("id") for n in nodes]
    if None in ids or len(ids)!=len(set(ids)): fail("node ids missing or duplicated")
    graph={i:[] for i in ids}; indegree={i:0 for i in ids}; errors=[]
    for e in data.get("edges",[]):
        a=e.get("from"); b=e.get("to")
        if a not in graph or b not in graph: errors.append("edge references unknown node"); continue
        graph[a].append(b); indegree[b]+=1
    queue=sorted([i for i,d in indegree.items() if d==0]); visited=[]
    while queue:
        a=queue.pop(0); visited.append(a)
        for b in sorted(graph[a]):
            indegree[b]-=1
            if indegree[b]==0: queue.append(b); queue.sort()
    if len(visited)!=len(nodes): errors.append("lineage contains cycle")
    current=[n["id"] for n in nodes if n.get("current")]
    if len(current)!=1: errors.append("lineage must have exactly one current version")
    return {"status":"pass" if not errors else "fail","errors":errors,"topological_order":visited,"current":current}
if __name__ == "__main__": run_cli(validate,"PLCO-lineage-1")
