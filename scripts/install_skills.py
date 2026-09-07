#!/usr/bin/env python3
"""Install selected repository links without overwriting existing objects."""
from pathlib import Path
import argparse
import sys

ROOT=Path(__file__).resolve().parents[1]

def install(destination, selected, check=False):
    names={p.parent.name for p in ROOT.glob('*/SKILL.md')}
    if not set(selected)<=names: return ['unknown skill selection']
    # Governance and adjacent domains stay in the checkout; isolated copies do
    # not preserve ../governance references. Resolve the link before use.
    errors=[]
    for name in selected:
        link=destination/name;source=ROOT/name
        if link.is_symlink():
            if link.resolve()!=source: errors.append(f'{name}: conflicting symlink')
        elif link.exists(): errors.append(f'{name}: existing object will not be overwritten')
        elif check: errors.append(f'{name}: not installed')
    if errors or check: return errors
    destination.mkdir(parents=True,exist_ok=True)
    for name in selected:
        link=destination/name
        if not link.is_symlink(): link.symlink_to(ROOT/name,target_is_directory=True)
    return []

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--skill',action='append');p.add_argument('--check',action='store_true');a=p.parse_args()
    selected=a.skill or sorted(x.parent.name for x in ROOT.glob('*/SKILL.md'))
    errors=install(a.root.expanduser().resolve(),selected,a.check)
    for error in errors: print(error,file=sys.stderr)
    if not errors: print(f'{len(selected)} skill links verified; keep the full repository checkout in place.')
    return 2 if errors else 0
if __name__=='__main__':raise SystemExit(main())
