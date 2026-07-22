#!/usr/bin/env python3
from plco_common import fail, fingerprint, required, run_cli

FIELDS=("platform","country","store_id","listing_id","page_version_id","as_of_time")
def validate(data):
    required(data, FIELDS)
    if data.get("comparison"):
        for i,x in enumerate(data["comparison"]): required(x, FIELDS, f"comparison[{i}] ")
        keys={(x["platform"],x["country"],x["store_id"],x["listing_id"]) for x in data["comparison"]}
        if len(keys)>1: fail("comparison mixes different objects")
        versions=[x["page_version_id"] for x in data["comparison"]]
        if len(versions)!=len(set(versions)): fail("duplicate page_version_id")
    object_id=fingerprint({k:data[k] for k in FIELDS[:4]})[:24]
    return {"status":"ok","object_id":object_id,"page_version_id":data["page_version_id"],"comparable":True}
if __name__ == "__main__": run_cli(validate,"PLCO-object-1")
