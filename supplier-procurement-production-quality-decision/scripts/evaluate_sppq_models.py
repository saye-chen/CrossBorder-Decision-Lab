#!/usr/bin/env python3
import json, pathlib, sys
from sppq_core import ModelError,evaluate
def main():
    if len(sys.argv)!=2: raise SystemExit("usage: evaluate_sppq_models.py input.json")
    try: out=evaluate(json.loads(pathlib.Path(sys.argv[1]).read_text()))
    except (OSError,json.JSONDecodeError,ModelError) as e: raise SystemExit(f"SPPQ model BLOCKED: {e}")
    print(json.dumps(out,ensure_ascii=False,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
