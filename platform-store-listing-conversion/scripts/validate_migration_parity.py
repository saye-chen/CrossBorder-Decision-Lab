#!/usr/bin/env python3
import json,pathlib,sys

def validate(repo,manifest):
 repo=pathlib.Path(repo); data=json.loads(pathlib.Path(manifest).read_text()); results=[]; errors=[]
 for item in data["items"]:
  source=repo/item["source_skill"]; target=repo/"platform-store-listing-conversion"; row={"source_skill":item["source_skill"],"checks":{}}
  row["checks"]["source_anchors_exist"]=all((source/p).is_file() for p in item["source_anchors"])
  row["checks"]["target_anchors_exist"]=all((target/p).is_file() for p in item["target_anchors"])
  source_skill=(source/"SKILL.md").read_text(encoding="utf-8")
  row["checks"]["source_routes_d08"]="platform-store-listing-conversion" in source_skill
  row["checks"]["retained_owner_declared"]=bool(item.get("retained_owner"))
  row["checks"]["target_declares_source_domain"]=item["source_skill"] in (target/"references/cross-domain-and-migration.md").read_text(encoding="utf-8") or item["retained_owner"].split()[0] in (target/"references/cross-domain-and-migration.md").read_text(encoding="utf-8")
  row["status"]="pass" if all(row["checks"].values()) else "fail"; results.append(row)
  if row["status"]=="fail": errors.append(row)
 return {"status":"pass" if not errors else "fail","results":results,"errors":errors}

if __name__=="__main__":
 repo=pathlib.Path(__file__).resolve().parents[2]; manifest=repo/"platform-store-listing-conversion/references/migration-manifest.json"
 out=validate(repo,manifest); print(json.dumps(out,ensure_ascii=False,sort_keys=True)); raise SystemExit(0 if out["status"]=="pass" else 2)
