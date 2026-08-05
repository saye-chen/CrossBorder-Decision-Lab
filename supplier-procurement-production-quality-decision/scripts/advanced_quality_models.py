#!/usr/bin/env python3
"""Advanced quality-engineering diagnostics with explicit applicability gates."""
from __future__ import annotations
import math

class QualityModelError(ValueError): pass
def req(x,msg):
 if not x: raise QualityModelError(msg)

def anova_grr(d):
 """Balanced crossed two-way random-effects ANOVA GR&R without interaction pooling."""
 rows=d.get("measurements",[]); parts=sorted({r["part"] for r in rows}); ops=sorted({r["operator"] for r in rows}); reps=sorted({r["replicate"] for r in rows})
 req(len(parts)>=2 and len(ops)>=2 and len(reps)>=2,"balanced_two_operator_two_replicate_minimum")
 cells={(p,o):[float(r["value"]) for r in rows if r["part"]==p and r["operator"]==o] for p in parts for o in ops}
 req(all(len(v)==len(reps) for v in cells.values()),"balanced_crossed_design_required")
 values=[x for v in cells.values() for x in v]; grand=sum(values)/len(values); nr=len(reps); np=len(parts); no=len(ops)
 part_means={p:sum(x for (pp,_),v in cells.items() if pp==p for x in v)/(no*nr) for p in parts}; op_means={o:sum(x for (_,oo),v in cells.items() if oo==o for x in v)/(np*nr) for o in ops}
 ss_part=no*nr*sum((x-grand)**2 for x in part_means.values()); ss_op=np*nr*sum((x-grand)**2 for x in op_means.values())
 ss_repeat=sum(sum((x-sum(v)/len(v))**2 for x in v) for v in cells.values()); df_repeat=np*no*(nr-1); ms_repeat=ss_repeat/df_repeat
 var_repeat=max(0,ms_repeat); var_op=max(0,(ss_op/(no-1)-ms_repeat)/(np*nr)); var_part=max(0,(ss_part/(np-1)-ms_repeat)/(no*nr)); grr=var_repeat+var_op; total=grr+var_part
 return {"repeatability_variance":round(var_repeat,8),"reproducibility_variance":round(var_op,8),"part_variance":round(var_part,8),"grr_percent_study_variation":round(100*math.sqrt(grr/total),4) if total else None,"design":"balanced_crossed_anova","interaction":"not_estimated_requires_separate_model"}

def western_electric(d):
 values=[float(x) for x in d.get("values",[])]; center=float(d.get("center")); sigma=float(d.get("sigma"));req(len(values)>=8 and sigma>0,"eight_points_and_positive_sigma_required")
 r1=[i for i,x in enumerate(values) if abs(x-center)>3*sigma]
 r2=[i for i in range(2,len(values)) if sum(values[j]>center+2*sigma for j in range(i-2,i+1))>=2 or sum(values[j]<center-2*sigma for j in range(i-2,i+1))>=2]
 r3=[i for i in range(4,len(values)) if sum(values[j]>center+sigma for j in range(i-4,i+1))>=4 or sum(values[j]<center-sigma for j in range(i-4,i+1))>=4]
 r4=[i for i in range(7,len(values)) if all(values[j]>center for j in range(i-7,i+1)) or all(values[j]<center for j in range(i-7,i+1))]
 return {"rule1_beyond_3sigma":r1,"rule2_two_of_three_beyond_2sigma":r2,"rule3_four_of_five_beyond_1sigma":r3,"rule4_eight_same_side":r4,"stable":not any((r1,r2,r3,r4)),"control_limits_are_not_specification_limits":True}

def weibull_rank_fit(d):
 times=sorted(float(x) for x in d.get("failure_times",[]));req(len(times)>=3 and all(x>0 for x in times),"three_positive_complete_failures_required");req(d.get("right_censored",0)==0,"censoring_requires_survival_likelihood_model")
 n=len(times); xs=[math.log(x) for x in times]; ys=[math.log(-math.log(1-(i-.3)/(n+.4))) for i in range(1,n+1)]; xm=sum(xs)/n;ym=sum(ys)/n;den=sum((x-xm)**2 for x in xs);req(den>0,"failure_times_need_variation")
 beta=sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/den; intercept=ym-beta*xm; eta=math.exp(-intercept/beta);return {"beta_shape":round(beta,6),"eta_scale":round(eta,6),"method":"median_rank_linear_fit","use":"screening_not_life_claim","censoring_supported":False}

def sampling_plan_lookup(d,registry):
 req(d.get("standard") and d.get("inspection_level") and d.get("aql") is not None,"standard_level_aql_required"); key=f"{d['standard']}|{d['inspection_level']}|{d['aql']}|{d['lot_size']}"
 row=registry.get(key);req(row is not None,"sampling_plan_not_approved_or_calibrated");req(row.get("source_ref") and row.get("approved_by"),"sampling_plan_source_and_approval_required")
 return {"sample_size":row["sample_size"],"accept_number":row["accept_number"],"reject_number":row["reject_number"],"source_ref":row["source_ref"],"lookup_key":key}
