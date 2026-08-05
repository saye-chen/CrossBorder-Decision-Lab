#!/usr/bin/env python3
"""Reject generic or scenario-mismatched extreme reports."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GENERIC=("根因按主权、产品/合规","使用适用确定性计算器","E1为授权场景输入","A1对象稳定","I20 实际结果回填")
REQUIRED={
"EC-01":["贡献利润=-8.40","ATP=0","停止扩量"],"EC-02":["GTIN","评论仅绑定ASIN-A","阻断合并"],
"EC-03":["1240/2000=62%","partially_applied","760个对象"],"EC-04":["120V","素材授权限US","禁止发布"],
"EC-05":["同一数据家族","42名客户","小预算迁移实验"],"EC-06":["治疗效果","退款未成熟","停止相关话术"],
"EC-07":["批次B-2407","隔离批次","货权流向"],"EC-08":["错误合并","CLV异常跃升","停止触达"],
"EC-09":["规则快照已过期","unknown","条件草稿"],"EC-10":["CIM与AAMO超时","inconclusive","冻结资本升级"],
"EC-11":["页面变为v3","主实验估计invalid","选择移动端子组"],"EC-12":["停售180天","素材授权已到期","禁止继承有效状态"]}
def validate():
 errors=[]; texts={}
 for sid,markers in REQUIRED.items():
  path=ROOT/"evaluations/extreme-reports"/f"{sid}.md"; text=path.read_text(); texts[sid]=text
  for marker in markers:
   if marker not in text: errors.append(f"{sid}: missing semantic marker {marker}")
  for phrase in GENERIC:
   if phrase in text: errors.append(f"{sid}: retained generic template phrase")
  if len(set(re.findall(r"E\d+",text)))<3: errors.append(f"{sid}: insufficient scenario evidence")
 normalized={sid:re.sub(r"EC-\d+|E\d+|C\d+|I\d+|sha256:[^`]+","",t) for sid,t in texts.items()}
 ids=list(normalized)
 for i,a in enumerate(ids):
  for b in ids[i+1:]:
   la=set(normalized[a].splitlines()); lb=set(normalized[b].splitlines()); ratio=len(la&lb)/max(1,len(la|lb))
   if ratio>.72: errors.append(f"{a}/{b}: semantic line similarity too high {ratio:.2f}")
 return errors
if __name__=="__main__":
 e=validate(); print("EXTREME_SEMANTICS=PASS" if not e else "EXTREME_SEMANTICS=FAIL\n- "+"\n- ".join(e)); raise SystemExit(bool(e))
