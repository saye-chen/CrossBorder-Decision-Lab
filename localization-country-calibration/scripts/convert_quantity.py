#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from decimal import Decimal
from pathlib import Path
from lcca_common import LCCAError,decimal,quantize,canonical_hash,require_false
FACTORS={('kg','g'):'1000',('g','kg'):'0.001',('lb','kg'):'0.45359237',('kg','lb'):'2.2046226218487757',('cm','in'):'0.3937007874015748',('in','cm'):'2.54'}
def convert(p):
    require_false(p); value=decimal(p.get('value'),'value'); kind=p.get('conversion_type'); source=p.get('source_unit'); target=p.get('target_unit')
    if not p.get('precision'): raise LCCAError('ROUNDING_POLICY_MISSING','precision required')
    if kind=='currency':
        if p.get('base_currency')!=source or p.get('quote_currency')!=target: raise LCCAError('CURRENCY_PAIR_MISMATCH','currency pair mismatches units')
        factor=decimal(p.get('rate'),'rate')
    elif kind=='unit':
        if (source,target) not in FACTORS: raise LCCAError('UNIT_DIMENSION_MISMATCH','unsupported or incompatible units')
        factor=Decimal(FACTORS[(source,target)])
    elif kind=='tax_basis':
        if p.get('professional_approval_status')!='approved': raise LCCAError('TAX_BASIS_UNAPPROVED','approved tax basis required')
        rate=decimal(p.get('rate'),'rate'); direction=p.get('direction')
        factor=(Decimal('1')+rate) if direction=='exclusive_to_inclusive' else Decimal('1')/(Decimal('1')+rate)
    else: raise LCCAError('CONVERSION_TYPE_INVALID','unsupported conversion type')
    raw=value*factor; result=quantize(raw,p['precision'])
    out={'status':'converted','value':format(result,'f'),'source_unit':source,'target_unit':target,'rounding_residual':format(raw-result,'f'),'external_write':False}
    out['result_hash']=canonical_hash(out);return out
def main():
    q=argparse.ArgumentParser();q.add_argument('input',type=Path);a=q.parse_args()
    try: print(json.dumps(convert(json.loads(a.input.read_text())),sort_keys=True));return 0
    except (OSError,json.JSONDecodeError,LCCAError) as e: print(f"{getattr(e,'code','INVALID')}: {e}",file=sys.stderr);return 2
if __name__=='__main__': raise SystemExit(main())
