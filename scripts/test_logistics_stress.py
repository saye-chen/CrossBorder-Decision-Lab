#!/usr/bin/env python3
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];LIFD=ROOT/"logistics-inventory-fulfillment-decision"
class LogisticsStress(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill=(LIFD/"SKILL.md").read_text();cls.refs="\n".join(p.read_text() for p in (LIFD/"references").glob("*.md"));cls.scenarios=json.loads((LIFD/"references/expert-scenarios.json").read_text())
    def test_runtime_and_sovereignty(self):
        for term in ["LIFD-2026.04","D01资本进入/退出","D04供应商/采购/生产/质量","D06公司级资金和定价","AAMO广告动作","proposed"]: self.assertIn(term,self.skill)
    def test_nine_layer_and_gates(self):
        for term in ["对象与时点","数据有效性","Hard gates","状态识别","根因分层","候选生成","确定性比较","动作设计","闭环"]: self.assertIn(term,self.skill)
    def test_full_chain_references(self):
        for term in ["ATP/CTP","供需平衡","仓内作业","供应商退货","特殊货物","批次谱系","主数据","Dropshipping","Cost-to-Serve","完美订单","海外库存退出"]: self.assertIn(term,self.skill+self.refs)
    def test_dynamic_fact_gate(self):
        for term in ["执行时核验","核验日","不把旧规则"]: self.assertIn(term,self.refs)
    def test_failure_exit_controls(self):
        for term in ["清算商","货代运输角色","最终流向","召回、禁售或安全风险库存不得进入销售路径"]: self.assertIn(term,self.refs)
    def test_scripts_exist_and_routed(self):
        names=["logistics_economics.py","inventory_ledger.py","replenishment.py","network_routing.py","inventory_allocation.py","order_capacity.py","reverse_exit.py","cost_to_serve.py","traceability_recall.py","validate_decision_contract.py"]
        for name in names:
            self.assertTrue((LIFD/"scripts"/name).exists());self.assertIn(name,self.skill)
    def test_sixty_unique_scenarios(self):
        self.assertEqual(len(self.scenarios),60);self.assertEqual(len({x["id"] for x in self.scenarios}),60)
        domains={x["domain"] for x in self.scenarios}
        for domain in ["replenishment","routing","allocation","warehouse","reverse","exit","promising","special_cargo","traceability","master_data","security","contract","cost_to_serve"]: self.assertIn(domain,domains)
    def test_p0_failure_cases(self):
        blocked=[x for x in self.scenarios if x["expected_gate"]=="blocked"]
        self.assertGreaterEqual(len(blocked),12)
if __name__=="__main__":unittest.main(verbosity=2)
