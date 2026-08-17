"""Canonicalize legacy CIM snapshot field names at the boundary."""
from __future__ import annotations


def canonicalize(snapshot: dict) -> dict:
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be an object")
    product_id = snapshot.get("product_id", snapshot.get("object_id"))
    snapshot_at = snapshot.get("snapshot_at", snapshot.get("observed_at", snapshot.get("as_of_time")))
    result = dict(snapshot)
    if product_id is not None: result["product_id"] = product_id
    if snapshot_at is not None: result["snapshot_at"] = snapshot_at
    result.pop("object_id", None)
    result.pop("observed_at", None)
    result.pop("as_of_time", None)
    return result


def canonicalize_many(rows: list[dict]) -> list[dict]:
    return [canonicalize(row) for row in rows]
