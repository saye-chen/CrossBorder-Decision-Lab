#!/usr/bin/env python3
"""Deprecated D08 compatibility entry point; use validate_plco_contract.py."""
from plco_common import run_cli
from validate_plco_contract import validate

__all__ = ["validate"]

if __name__ == "__main__":
    run_cli(validate, "PLCO-contract-1")
