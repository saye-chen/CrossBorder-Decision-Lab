#!/usr/bin/env python3
"""Validate units, currencies, tax bases, timezone and mature windows."""
from mbcm_common import require, text, run_cli, ModelError, iso_datetime, sequence

def validate(d):
    require(d,"records")
    currencies=set(); tax_bases=set(); timezones=set(); units=set()
    for i,row in enumerate(sequence(d["records"],"records",allow_empty=False)):
        require(row,"currency","tax_basis","timezone","unit","window_start","window_end")
        currencies.add(text(row["currency"],f"records[{i}].currency"))
        tax_bases.add(text(row["tax_basis"],f"records[{i}].tax_basis"))
        timezones.add(text(row["timezone"],f"records[{i}].timezone"))
        units.add(text(row["unit"],f"records[{i}].unit"))
        start=iso_datetime(row["window_start"],f"records[{i}].window_start")
        end=iso_datetime(row["window_end"],f"records[{i}].window_end")
        if start.tzinfo is None or end.tzinfo is None: raise ModelError(f"records[{i}]:timezone_offset_required")
        if start>=end: raise ModelError(f"records[{i}]:invalid_window")
    comparable=len(currencies)==len(tax_bases)==len(timezones)==len(units)==1
    return {"comparable":comparable,"currencies":sorted(currencies),"tax_bases":sorted(tax_bases),
            "timezones":sorted(timezones),"units":sorted(units),
            "aggregation_allowed":comparable}
if __name__=="__main__": run_cli(validate,"validate_units_currency_time")
