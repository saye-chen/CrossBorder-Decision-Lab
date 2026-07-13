#!/usr/bin/env python3
"""Validate customer-event CSV structure, time, consent and basic values."""
import argparse, csv, json
from datetime import datetime
from pathlib import Path

REQUIRED = {"event_id", "event_time", "ingest_time", "customer_key", "market", "channel", "event_type", "consent_state", "source"}

def parse_time(value): return datetime.fromisoformat(value.replace("Z", "+00:00"))

def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    issues=[]; seen=set(); rows=0
    with open(a.input,encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f); missing=sorted(REQUIRED-set(reader.fieldnames or []))
        if missing: issues.append({"row":0,"type":"missing_columns","fields":missing})
        for n,row in enumerate(reader,2):
            rows+=1
            for field in REQUIRED:
                if field in row and not row[field].strip(): issues.append({"row":n,"type":"missing_value","field":field})
            eid=row.get("event_id","")
            if eid in seen: issues.append({"row":n,"type":"duplicate_event_id","value":eid})
            seen.add(eid)
            try:
                if parse_time(row["ingest_time"]) < parse_time(row["event_time"]): issues.append({"row":n,"type":"ingest_before_event"})
            except (KeyError,ValueError): issues.append({"row":n,"type":"invalid_time"})
            if row.get("consent_state") not in {"granted","denied","withdrawn","unknown"}: issues.append({"row":n,"type":"invalid_consent_state"})
            for field in ("quantity","amount"):
                if row.get(field):
                    try:
                        if float(row[field]) < 0 and row.get("event_type") not in {"refund","cancel"}: issues.append({"row":n,"type":"unexpected_negative","field":field})
                    except ValueError: issues.append({"row":n,"type":"invalid_number","field":field})
    out={"rows":rows,"valid":not issues,"issues":issues}
    Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
