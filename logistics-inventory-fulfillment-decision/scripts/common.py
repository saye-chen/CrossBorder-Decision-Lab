#!/usr/bin/env python3
import argparse, hashlib, json, math
from pathlib import Path

def cli():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--output",required=True);return p.parse_args()
def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def save(path,data): Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True),encoding="utf-8")
def canonical_json(value): return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha256_json(value): return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
def num(v,name,minimum=None):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v): raise ValueError(f"{name} must be finite number")
    if minimum is not None and v<minimum: raise ValueError(f"{name} must be >= {minimum}")
    return float(v)
def n(d,key,default=0,minimum=0): return num(d.get(key,default),key,minimum)
def main(run):
    a=cli()
    try: out=run(load(a.input));out={"status":"ok",**out}
    except (ValueError,KeyError,TypeError) as e: out={"status":"error","error":str(e)}
    save(a.output,out)
    if out["status"]=="error": raise SystemExit(2)
