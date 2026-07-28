#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=next(p for p in HERE.parents if (p/"product-innovation-product-management/scripts/validate_consumer_side_adapter.py").is_file())
PATH=REPO/"product-innovation-product-management/scripts/validate_consumer_side_adapter.py"
SPEC=importlib.util.spec_from_file_location("pipm_consumer_side",PATH)
MODULE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODULE)
def validate():return MODULE.validate_files(HERE/"adapter.json",HERE/"acceptance.json")
if __name__=="__main__":
 errors=validate()
 if errors:raise SystemExit("\n".join(errors))
 print("PIPM_CONSUMER_SIDE=PASS")
