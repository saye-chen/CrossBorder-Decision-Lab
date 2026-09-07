#!/usr/bin/env python3
"""Strict, local, read-only calculation preparation for three operator tasks.

This adapter runs owned calculators, never approves business decisions. Source
files are immutable; each run creates a new output directory outside the repo.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
TASKS = {
    'ad-profit': ('advertising-analysis-measurement-optimization/scripts/mature_profit.py', ['AAMO', 'PPFC']),
    'product-test': ('category-investment-decision/scripts/reverse_funnel.py', ['CIDM', 'PPFC']),
    'replenishment': ('logistics-inventory-fulfillment-decision/scripts/replenishment.py', ['LIFD', 'PPFC']),
}
AMOUNTS = ['gross_revenue','discount','refund','chargeback','tax','cogs','fulfillment','platform_fee','service_cost','ad_spend']
STAGES = ['supplier_confirmation_days','production_days','quality_release_days','origin_handling_days','main_haul_days','customs_days','inbound_days','receiving_putaway_days']
INVENTORY = ['expected_protection_demand','target_demand_quantile','target_inventory_position','current_inventory_position','opening_available','case_pack','moq','supplier_capacity','cash_capacity_units','warehouse_capacity_units','lifecycle_cap','shelf_life_cap']


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def required(obj, fields, prefix=''):
    missing = [prefix + k for k in fields if k not in obj or obj[k] is None or obj[k] == '']
    if missing:
        raise ValueError('必须补充字段：' + ', '.join(missing))


def numbers(obj, fields):
    required(obj, fields)
    for field in fields:
        value = obj[field]
        if isinstance(value, bool) or not isinstance(value, (int,float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f'{field} 必须是有限非负数字；未知不可填 0')


def prepare(task, payload):
    if not isinstance(payload, dict): raise ValueError('输入必须是对象')
    required(payload, ['case_id','object_id','country','platform','currency','as_of_time','source_class','source_ref','data'])
    for field in ['case_id','object_id','country','platform','currency','source_ref']:
        if not isinstance(payload[field], str) or not payload[field].strip(): raise ValueError(f'{field} 必须是非空文本')
    if payload['source_class'] not in {'synthetic_fixture','authorized_first_party','user_assertion'}:
        raise ValueError('source_class 未支持；先核实输入使用范围')
    if payload.get('external_write') or payload.get('production_ready'):
        raise ValueError('此入口只作受控测算，不执行外部动作或批准生产使用')
    if datetime.fromisoformat(payload['as_of_time'].replace('Z','+00:00')).tzinfo is None:
        raise ValueError('as_of_time 必须包含时区')
    data = payload['data']
    if task == 'ad-profit':
        if not isinstance(data, list) or not data: raise ValueError('data 必须有至少一行订单或不重叠核算记录')
        for row in data:
            required(row, ['order_id','currency','maturity',*AMOUNTS]); numbers(row, AMOUNTS)
            if row['currency'] != payload['currency']: raise ValueError('币种不一致，先完成授权汇率转换')
            if row['maturity'] not in {'mature','immature','excluded'}: raise ValueError('订单成熟状态未识别')
        if all(row['maturity']=='excluded' for row in data): raise ValueError('没有可核算记录')
    elif task == 'product-test':
        required(data,['price','fixed_costs','variable_costs','rates','funnel'])
        numbers(data,['price'])
        if data['price'] <= 0: raise ValueError('price 必须大于 0')
        numbers(data['fixed_costs'],['samples','creative','test_ads'])
        numbers(data['variable_costs'],['product','logistics','packaging','other'])
        numbers(data['rates'],['platform_commission','creator_commission','payment','return_loss'])
        numbers(data['funnel'],['ctr','cvr'])
        for values in (data['fixed_costs'], data['variable_costs']): numbers(values, list(values))
    else:
        numbers(data,INVENTORY + STAGES)
        if data['case_pack'] <= 0: raise ValueError('case_pack 必须大于 0')
        for field in STAGES:
            if data[field] != int(data[field]): raise ValueError(f'{field} 必须是整数天')
        required(data,['order_date','timeline'])
        if not isinstance(data['timeline'],list) or not data['timeline']: raise ValueError('补货必须提供连续库存时间线')
        for row in data['timeline']:
            required(row,['period']); numbers(row,['eligible_arrival','demand','reservation','expected_loss','protection_floor'])
    return data


def calculate(task, data):
    script=ROOT/TASKS[task][0]
    with tempfile.TemporaryDirectory(prefix='cbdl-starter-') as td:
        inp, out = Path(td)/'input.json', Path(td)/'output.json'
        inp.write_text(json.dumps(data,ensure_ascii=False,allow_nan=False))
        if task=='ad-profit':
            inp=Path(td)/'orders.csv'
            with inp.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=['order_id','currency','maturity',*AMOUNTS],extrasaction='ignore');writer.writeheader();writer.writerows(data)
            args=['--input',str(inp),'--output',str(out)]
        elif task=='product-test': args=['standard',str(inp)]
        else: args=['--input',str(inp),'--output',str(out)]
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
        result=subprocess.run([sys.executable,str(script),*args],capture_output=True,text=True,env=env,timeout=60)
        if result.returncode: raise ValueError('计算器拒绝输入：'+(result.stderr or (out.read_text() if out.exists() else result.stdout)).strip())
        value=json.loads(out.read_text() if out.exists() else result.stdout)
    return value, hashlib.sha256(script.read_bytes()).hexdigest()


def run(task, payload, previous=None):
    result={'task':task,'status':'inconclusive','external_write':False,'production_ready':False,'owner_review_required':TASKS[task][1],
            'case_id':payload.get('case_id') if isinstance(payload,dict) else None,'version':1,
            'source_class':payload.get('source_class') if isinstance(payload,dict) else None,
            'allowed_use':'calculation_and_review_only','withheld':['业务审批','真实收益或因果结论'],
            'metrics':None,'next_action':'补齐缺失资料后重新测算','stop':'关键口径、币种或对象无法对齐时停止相关计算'}
    try:
        data=prepare(task,payload)
        if previous:
            if previous.get('case_id') != payload['case_id'] or previous.get('task') != task: raise ValueError('上一版本必须属于同一案例与任务')
            result.update(version=previous['version']+1,parent_hash=digest(previous))
        metrics,code_hash=calculate(task,data)
        result.update(status='proposed',metrics=metrics,input_hash=digest(payload),model=TASKS[task][0],model_hash=code_hash,
                      calculation_hash=digest(metrics),context={k:payload[k] for k in ('object_id','country','platform','currency','as_of_time','source_ref')})
        if task=='ad-profit':
            result['conclusion']='贡献利润测算完成，需核对订单成熟与广告分摊'
            result['next_action']='由运营核对重复归因和退款窗口；财务确认成本；广告负责人再审议调整'
            if metrics['status']=='provisional': result['withheld'].append('未成熟订单下的确定性放量或停投结论')
        elif task=='product-test':
            result['conclusion']='当前情景单位贡献不为正，先修复经济性' if metrics['contribution_margin_per_unit']<=0 else '已算出测试保本所需订单与流量，尚未批准进入'
            result['next_action']='核验 CTR/CVR 与费用假设，再由品类和财务负责人确认测试损失上限'
            result['withheld'].append('竞争、准入、供应或资本门未完成前的 Go/No-Go')
        else:
            result['conclusion']='补货情景已计算，时间线存在缺口' if metrics['continuity']=='fail' else '补货情景已计算，待核实到货与需求假设'
            result['next_action']='由计划负责人核实需求分位和到货资格；财务确认现金上限；采购确认排期'
            result['withheld'].append('未经分布验证的缺货概率、未经批准的采购承诺')
        result['success']='输入可对账，相关负责人确认，并在成熟观察窗回填实际执行与结果'
    except (ValueError,TypeError,KeyError,OverflowError,subprocess.TimeoutExpired) as exc:
        result['conclusion']='资料不足或口径冲突，暂不下经营结论';result['error']=str(exc)
    return result


def render(result):
    lines=['# 经营测算卡','',f"案例：{result['case_id']} · 版本：{result['version']}", '',
           f"**{result['conclusion']}**",'',f"状态：{'待确认建议' if result['status']=='proposed' else '资料不足，暂不下结论'}",'',
           f"下一步：{result['next_action']}",'',f"停止条件：{result['stop']}",'',
           f"复核责任：{'、'.join(result['owner_review_required'])}",'',
           '用途：受控测算与人工复核；不是已批准行动。合成样例不代表真实经营证据。','',
           '暂不支持的结论：'+'；'.join(result['withheld'])]
    if result.get('error'): lines += ['', '补数或修正：'+result['error']]
    if result.get('metrics') is not None: lines += ['','<details><summary>展开计算与证据</summary>','','```json',json.dumps(result,ensure_ascii=False,indent=2),'```','','</details>']
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task',choices=TASKS);parser.add_argument('input',type=Path);parser.add_argument('--output-dir',required=True,type=Path);parser.add_argument('--previous',type=Path)
    args=parser.parse_args();target=args.output_dir.resolve()
    if target==ROOT or ROOT in target.parents: parser.error('输出目录必须在项目仓库外')
    if target.exists(): parser.error('输出目录已存在；请指定新版本目录，源文件不会覆盖')
    try:
        payload=json.loads(args.input.read_text());previous=json.loads(args.previous.read_text()) if args.previous else None
        result=run(args.task,payload,previous)
    except (OSError,ValueError) as exc: parser.error(str(exc))
    target.mkdir(parents=True,exist_ok=False)
    (target/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    (target/'decision-card.md').write_text(render(result))
    feedback={'case_id':result['case_id'],'decision_version':result['version'],'decision_hash':digest(result),'executed':None,'actual_action':None,'observation_window':None,'observed_results':None,'concurrent_changes':[],'reviewer':None,'reviewed_at':None,'result_class':'not_observed','production_ready':False}
    (target/'outcome.json').write_text(json.dumps(feedback,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'output_dir':str(target)},ensure_ascii=False))
    return 0 if result['status']=='proposed' else 2

if __name__=='__main__': raise SystemExit(main())
