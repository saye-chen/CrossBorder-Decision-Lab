#!/usr/bin/env python3
"""Safely create and clean marked temporary workspaces for this skill."""

import argparse
import json
import os
import re
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


SKILL_NAME = "category-investment-decision"
MARKER = ".task-owner.json"


def workspace_root():
    return Path(os.environ.get("TMPDIR") or "/tmp") / SKILL_NAME


def slugify(value):
    value = re.sub(r"[^\w-]+", "-", value.strip(), flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-")
    return (value or "task")[:48]


def ensure_child(path, root):
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    if resolved_path == resolved_root or resolved_root not in resolved_path.parents:
        raise ValueError("workspace path must be a child of the skill temporary root")
    return resolved_path


def read_marker(path):
    marker = path / MARKER
    if not marker.is_file():
        raise ValueError(f"missing workspace marker: {marker}")
    with marker.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("skill") != SKILL_NAME or not data.get("task_id"):
        raise ValueError(f"invalid workspace marker: {marker}")
    return data


def create_workspace(slug, task_id):
    root = workspace_root()
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    name = f"{timestamp}-{slugify(slug)}-{uuid.uuid4().hex[:6]}"
    path = ensure_child(root / name, root)
    path.mkdir(mode=0o700)
    marker = {
        "skill": SKILL_NAME,
        "task_id": task_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with (path / MARKER).open("w", encoding="utf-8") as handle:
        json.dump(marker, handle, ensure_ascii=False, indent=2)
    return path, marker


def cleanup_workspace(path_value, expected_task_id=None):
    root = workspace_root()
    path = ensure_child(Path(path_value), root)
    marker = read_marker(path)
    if expected_task_id and marker["task_id"] != expected_task_id:
        raise ValueError("task id does not match workspace marker")
    shutil.rmtree(path)
    if path.exists():
        raise OSError(f"workspace still exists after cleanup: {path}")
    try:
        root.rmdir()
    except OSError:
        pass
    return marker


def list_workspaces():
    root = workspace_root()
    items = []
    if not root.is_dir():
        return items
    for path in sorted(root.iterdir()):
        if not path.is_dir() or not (path / MARKER).is_file():
            continue
        try:
            marker = read_marker(path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        items.append({"path": str(path), **marker})
    return items


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("--slug", required=True)
    create.add_argument("--task-id", required=True)
    cleanup = sub.add_parser("cleanup")
    cleanup.add_argument("path")
    cleanup.add_argument("--task-id")
    cleanup_task = sub.add_parser("cleanup-task")
    cleanup_task.add_argument("--task-id", required=True)
    sub.add_parser("list")
    return parser


def main():
    args = build_parser().parse_args()
    try:
        if args.command == "create":
            path, marker = create_workspace(args.slug, args.task_id)
            result = {"path": str(path), **marker}
        elif args.command == "cleanup":
            marker = cleanup_workspace(args.path, args.task_id)
            result = {"cleaned": str(Path(args.path)), "task_id": marker["task_id"]}
        elif args.command == "cleanup-task":
            paths = [item["path"] for item in list_workspaces() if item["task_id"] == args.task_id]
            for path in paths:
                cleanup_workspace(path, args.task_id)
            result = {"task_id": args.task_id, "cleaned": paths}
        else:
            result = {"workspaces": list_workspaces()}
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
