#!/usr/bin/env python3
from plco_common import integer, run_cli

STAGES=("qualified_exposure","visit","engage","add_to_cart","checkout","paid_order")
def evaluate(data):
    counts={s:integer(data.get("counts",{}).get(s,0),s) for s in STAGES}; errors=[]; rates={}
    for a,b in zip(STAGES,STAGES[1:]):
        if counts[b]>counts[a]: errors.append(f"{b} exceeds {a}")
        rates[f"{a}_to_{b}"]=None if counts[a]==0 else counts[b]/counts[a]
    if counts["qualified_exposure"]==0: errors.append("zero exposure: conversion is undefined")
    valid=not errors
    weakest=None if not valid else min(rates,key=rates.get)
    return {"status":"pass" if valid else "invalid","counts":counts,"rates":rates,"weakest_transition":weakest,"errors":errors}
if __name__ == "__main__": run_cli(evaluate,"PLCO-funnel-1")
