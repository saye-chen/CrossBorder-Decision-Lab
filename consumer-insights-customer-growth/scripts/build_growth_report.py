#!/usr/bin/env python3
"""Render a structured growth result as a reviewable Markdown card."""
import argparse,json
from pathlib import Path
def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--output",required=True); a=p.parse_args(); d=json.loads(Path(a.input).read_text())
    lines=["# 客户增长建议卡","",f"- 模型版本：{d.get('model_version','未提供')}",f"- 数据截止：{d.get('data_as_of','未提供')}",f"- 推断层级：{d.get('inference_level','未提供')}","","> 预测用于缩小候选范围；只有可信实验或准实验可以支持增量因果结论。","","## 建议动作",""]
    for x in d.get("selected",[]): lines.append(f"- {x.get('customer_key','群体')} → {x.get('action','未命名动作')}；NIV={x.get('net_incremental_value','—')}")
    if not d.get("selected"): lines.append("- 不触达：当前没有通过资格与净增量价值门槛的动作。")
    lines += ["","## 未入选与护栏",""]
    for x in d.get("not_selected",[]): lines.append(f"- {x.get('customer_key','群体')} / {x.get('action','动作')}：{', '.join(x.get('rejection_reasons',[]))}")
    Path(a.output).write_text("\n".join(lines)+"\n",encoding="utf-8")
if __name__=="__main__": main()
