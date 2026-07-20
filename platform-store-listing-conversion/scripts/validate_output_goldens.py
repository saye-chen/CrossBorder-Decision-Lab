#!/usr/bin/env python3
import json, pathlib, sys

GLOBAL=("对象","证据截止","Gate","证据","反证","根因","具体","成功","停止","回滚")
SPEC={
 "decision-card.md":("结论","标题保守版","owner"),
 "three-layer-diagnostic.md":("Listing诊断","主图与图组Brief","详情诊断","跨层一致性"),
 "conversion-diagnosis-memo.md":("漏斗","替代解释","实验"),
 "listing-experiment-memo.md":("预注册","主指标","护栏","inconclusive"),
 "incident-recovery-card.md":("partially_applied","部分成功与失败","关闭"),
 "migration-merge-memo.md":("继承分类","禁止继承","血缘","退出"),
 "store-portfolio-architecture.md":("对象树","角色与导航","蚕食","依赖"),
 "conversion-diligence.md":("Ledger","四页面层诊断","反事实","审计")}

def validate(root):
 root=pathlib.Path(root); errors=[]; results={}
 for name,terms in SPEC.items():
  path=root/name
  if not path.is_file(): errors.append(f"missing {name}"); continue
  body=path.read_text(encoding="utf-8"); missing=[x for x in GLOBAL+terms if x not in body]
  if len(body)<300: missing.append("minimum_depth")
  results[name]={"status":"pass" if not missing else "fail","missing":missing,"characters":len(body)}
  errors.extend(f"{name}: {x}" for x in missing)
 return {"status":"pass" if not errors else "fail","reports":results,"errors":errors}

if __name__=="__main__":
 root=sys.argv[1] if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parents[2]/"evaluations/d08/output-goldens"
 out=validate(root); print(json.dumps(out,ensure_ascii=False,sort_keys=True)); raise SystemExit(0 if out["status"]=="pass" else 2)
