#!/usr/bin/env python3
"""Compute the deterministic downstream invalidation/recompute closure."""

from __future__ import annotations

from collections import defaultdict,deque

from ecae_common import ECAEError, cli_main


def compute_invalidation_closure(value:dict)->dict:
    changed=value.get("changed_refs")
    edges=value.get("dependency_graph")
    if not isinstance(changed,list) or not changed or not isinstance(edges,list): raise ECAEError("INVALID_DEPENDENCY_INPUT","changed_refs and dependency_graph are required")
    downstream=defaultdict(list)
    for edge in edges:
        if not all(field in edge for field in ["from","to","relation"]): raise ECAEError("INVALID_DEPENDENCY_EDGE","Dependency edge is incomplete")
        if edge["relation"] in {"consumes","produces","invalidates","recomputes"}: downstream[edge["from"]].append((edge["to"],edge["relation"]))
    queue=deque((ref,[ref]) for ref in changed); visited=set(changed); affected=[]
    while queue:
        source,path=queue.popleft()
        for target,relation in sorted(downstream[source]):
            if target not in visited:
                visited.add(target); new_path=path+[target]; affected.append({"ref":target,"via":relation,"path":new_path}); queue.append((target,new_path))
    return {"changed_refs":changed,"affected_refs":affected,"required_action":"mark_stale_then_recompute","silent_continued_consumption_forbidden":True}


if __name__=="__main__":
    cli_main(compute_invalidation_closure,__doc__ or "Compute invalidation closure")
