#!/usr/bin/env python3
from decimal import Decimal, InvalidOperation
from plco_common import run_cli

FIELDS=("product_name","model","quantity","unit","dimensions","materials","included_items","variant","price","currency","availability","delivery")
def check(data):
    layers=data.get("layers",{}); conflicts=[]
    for field in FIELDS:
        observed={layer:content.get(field) for layer,content in layers.items() if isinstance(content,dict) and content.get(field) is not None}
        normalized=set()
        for value in observed.values():
            try: normalized.add(str(Decimal(str(value).strip())))
            except (InvalidOperation, ValueError): normalized.add(str(value).strip().casefold())
        if len(normalized)>1: conflicts.append({"field":field,"values":observed})
    return {"status":"pass" if not conflicts else "fail","conflicts":conflicts,"checked_fields":list(FIELDS)}
if __name__ == "__main__": run_cli(check,"PLCO-consistency-1")
