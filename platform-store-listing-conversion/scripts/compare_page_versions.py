#!/usr/bin/env python3
from d08_common import fail, required, run_cli

def compare(data):
    required(data,("before","after")); a=data["before"]; b=data["after"]
    required(a,("object_id","page_version_id","content"),"before "); required(b,("object_id","page_version_id","content"),"after ")
    if a["object_id"]!=b["object_id"]: fail("versions belong to different objects")
    if a["page_version_id"]==b["page_version_id"]: fail("version ids must differ")
    keys=sorted(set(a["content"])|set(b["content"])); changes=[]
    for k in keys:
        if a["content"].get(k)!=b["content"].get(k): changes.append({"field":k,"before":a["content"].get(k),"after":b["content"].get(k)})
    return {"status":"ok","changed_fields":[x["field"] for x in changes],"changes":changes,"change_count":len(changes)}
if __name__ == "__main__": run_cli(compare,"D08-version-1")
