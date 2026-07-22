#!/usr/bin/env python3
import math
from plco_common import integer, number, required, run_cli

def evaluate(data):
    required(data,("control","treatment","primary_metric","mature"))
    c=data["control"]; t=data["treatment"]
    nc=integer(c.get("n"),"control.n"); nt=integer(t.get("n"),"treatment.n")
    xc=integer(c.get("successes"),"control.successes"); xt=integer(t.get("successes"),"treatment.successes")
    errors=[]
    if xc>nc or xt>nt: errors.append("successes exceed exposure")
    if nc==0 or nt==0: errors.append("zero exposure")
    if errors: return {"status":"invalid","errors":errors}
    pc=xc/nc; pt=xt/nt; diff=pt-pc; se=math.sqrt(pc*(1-pc)/nc+pt*(1-pt)/nt); ci=[diff-1.96*se,diff+1.96*se]
    guardrail_breached=bool(data.get("guardrail_breached",False))
    if guardrail_breached: decision="rollback"
    elif not data["mature"]: decision="inconclusive"
    elif ci[0]>0: decision="go"
    elif ci[1]<0: decision="stop"
    else: decision="iterate"
    return {"status":"ok","control_rate":pc,"treatment_rate":pt,"absolute_effect":diff,"ci95":ci,"decision":decision,"guardrail_breached":guardrail_breached}
if __name__ == "__main__": run_cli(evaluate,"PLCO-experiment-1")
