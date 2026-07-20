#!/usr/bin/env python3
"""Cross-skill integration tests for CIDM ↔ VLB对接协议.

Tests verify:
1. cidm-integration.md write-back field mapping is consistent with CIDM SKILL.md
2. Write-back output protocol includes all required fields
3. Historical report protection rules are consistent across both skills
4. Cross-skill reference links resolve correctly
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CIDM_SKILL = ROOT / "category-investment-decision" / "SKILL.md"
VLB_SKILL = ROOT / "video-link-breakdown" / "SKILL.md"
VLB_CIDM_INTEGRATION = ROOT / "video-link-breakdown" / "references" / "cidm-integration.md"
RULES_MD = ROOT / "RULES.md"
CIM_SKILL = ROOT / "competitive-intelligence-monitoring" / "SKILL.md"
CIM_INTEGRATION = ROOT / "competitive-intelligence-monitoring" / "references" / "skill-integration-protocol.md"
CIG_SKILL = ROOT / "consumer-insights-customer-growth" / "SKILL.md"
CIG_INTEGRATION = ROOT / "consumer-insights-customer-growth" / "references" / "skill-integration-protocol.md"
D09_SKILL = ROOT / "advertising-analysis-measurement-optimization" / "SKILL.md"
D07_SKILL = ROOT / "logistics-inventory-fulfillment-decision" / "SKILL.md"
D08_SKILL = ROOT / "platform-store-listing-conversion" / "SKILL.md"


class CrossSkillFieldMapping(unittest.TestCase):
    """Verify VLB→CIDM write-back field mapping is consistent."""

    def setUp(self) -> None:
        self.integration_text = VLB_CIDM_INTEGRATION.read_text(encoding="utf-8")
        self.cidm_text = CIDM_SKILL.read_text(encoding="utf-8")
        self.vlb_text = VLB_SKILL.read_text(encoding="utf-8")

    def test_write_back_dimensions_match_cidm(self):
        """VLB write-back must reference CIDM dimension names that exist in CIDM SKILL.md."""
        cidm_dimensions = ["内容传播", "利润空间", "风险可控性", "机会窗口"]
        for dim in cidm_dimensions:
            self.assertIn(dim, self.cidm_text, f"CIDM SKILL.md missing dimension: {dim}")

    def test_write_back_fields_present(self):
        """cidm-integration.md must specify all required write-back fields."""
        required_fields = [
            "原 CIDM 版本",
            "原分",
            "建议分",
            "证据",
            "假设",
            "置信度",
            "五道门槛",
        ]
        for field in required_fields:
            self.assertIn(
                field,
                self.integration_text,
                f"cidm-integration.md missing write-back field: {field}",
            )

    def test_read_fields_match_cidm_output(self):
        """VLB must read fields that CIDM actually produces."""
        read_fields = ["内容传播评分", "利润评分", "风险评分", "切入楔子", "最弱假设"]
        for field in read_fields:
            self.assertIn(
                field,
                self.integration_text,
                f"cidm-integration.md missing read field: {field}",
            )


class SystemWideProfessionalInvariant(unittest.TestCase):
    """Every skill must preserve professional depth in every execution mode."""

    def test_all_skills_declare_professional_hard_constraint(self):
        for skill_file in (CIDM_SKILL, VLB_SKILL, CIM_SKILL, CIG_SKILL, D09_SKILL):
            with self.subTest(skill=skill_file.parent.name):
                text = skill_file.read_text(encoding="utf-8")
                self.assertIn("专业性与决策可用性硬约束", text)
                self.assertIn("只允许压缩展示", text)
                self.assertIn("停止条件", text)
                self.assertIn("决策影响", text)
        d07 = D07_SKILL.read_text(encoding="utf-8")
        for phrase in ("专家级", "压缩展示", "停止条件", "不得替代"):
            self.assertIn(phrase, d07)
        d08 = D08_SKILL.read_text(encoding="utf-8")
        for phrase in ("专家级", "压缩展示", "停止条件", "具体优化", "不得替代"):
            self.assertIn(phrase, d08)

    def test_decision_ownership_is_explicit(self):
        expected = {
            CIDM_SKILL: "最终主权",
            CIM_SKILL: "外部竞争事实",
            VLB_SKILL: "视频观察",
            CIG_SKILL: "授权客户证据",
            D09_SKILL: "广告架构",
            D07_SKILL: "物流网络",
            D08_SKILL: "页面承接",
        }
        for skill_file, phrase in expected.items():
            with self.subTest(skill=skill_file.parent.name):
                self.assertIn(phrase, skill_file.read_text(encoding="utf-8"))

    def test_investment_validator_is_routed(self):
        text = CIDM_SKILL.read_text(encoding="utf-8")
        self.assertIn("validate_decision_contract.py", text)
        self.assertTrue((CIDM_SKILL.parent / "scripts" / "validate_decision_contract.py").exists())


class HistoricalReportProtection(unittest.TestCase):
    """Verify both skills agree on not modifying historical reports."""

    def setUp(self) -> None:
        self.integration_text = VLB_CIDM_INTEGRATION.read_text(encoding="utf-8")
        self.cidm_text = CIDM_SKILL.read_text(encoding="utf-8")

    def test_vlb_does_not_silently_overwrite(self):
        """VLB integration must explicitly state no silent overwrite."""
        self.assertIn("不静默覆盖", self.integration_text)
        self.assertIn("未经用户确认", self.integration_text)

    def test_cidm_does_not_auto_rewrite(self):
        """CIDM SKILL.md must state it does not auto-rewrite old reports."""
        self.assertIn("不自动改写旧 CIDM 报告", self.cidm_text)

    def test_write_back_is_suggestion(self):
        """Write-back must be framed as 'suggested adjustment', not authoritative."""
        self.assertIn("建议调整", self.integration_text)


class CrossSkillRulesConsistency(unittest.TestCase):
    """Verify RULES.md cross-skill section matches actual skill files."""

    def setUp(self) -> None:
        self.rules_text = RULES_MD.read_text(encoding="utf-8")
        self.integration_text = VLB_CIDM_INTEGRATION.read_text(encoding="utf-8")

    def test_rules_document_bidirectional_relationship(self):
        """RULES.md section 10 must document both VLB→CIDM and CIDM→VLB."""
        self.assertIn("video-link-breakdown → category-investment-decision", self.rules_text)
        self.assertIn("category-investment-decision → video-link-breakdown", self.rules_text)

    def test_rules_document_optional_trigger(self):
        """RULES.md must state integration is opt-in, not automatic."""
        self.assertIn("可选", self.rules_text)
        self.assertIn("用户", self.rules_text)

    def test_rules_document_write_back_direction(self):
        """RULES.md must specify what VLB writes back to CIDM."""
        write_back_items = ["内容传播", "利润空间", "风险可控性"]
        for item in write_back_items:
            self.assertIn(
                item,
                self.rules_text,
                f"RULES.md missing write-back mapping for: {item}",
            )


class CompetitiveIntelligenceIntegration(unittest.TestCase):
    """Verify CIM boundaries and event-card routing are explicit."""

    def setUp(self) -> None:
        self.cim = CIM_SKILL.read_text(encoding="utf-8")
        self.protocol = CIM_INTEGRATION.read_text(encoding="utf-8")
        self.rules = RULES_MD.read_text(encoding="utf-8")

    def test_cim_is_documented_as_optional_with_both_skills(self):
        self.assertIn("competitive-intelligence-monitoring ↔ category-investment-decision", self.rules)
        self.assertIn("competitive-intelligence-monitoring ↔ video-link-breakdown", self.rules)

    def test_event_card_and_history_protection(self):
        self.assertIn("情报事件卡", self.cim)
        self.assertIn("不静默覆盖", self.protocol)
        self.assertIn("未经用户确认", self.protocol)

    def test_cim_does_not_claim_downstream_ownership(self):
        for boundary in ["不独立决定品类是否值得进入", "不完成详细 VOC", "不完成视频逐镜头拆解"]:
            self.assertIn(boundary, self.cim)


class ConsumerGrowthIntegration(unittest.TestCase):
    """Verify CIG inference, privacy and cross-skill boundaries."""

    def setUp(self) -> None:
        self.cig = CIG_SKILL.read_text(encoding="utf-8")
        self.protocol = CIG_INTEGRATION.read_text(encoding="utf-8")
        self.rules = RULES_MD.read_text(encoding="utf-8")

    def test_inference_levels_and_no_contact_are_explicit(self):
        for phrase in ["事实 → 描述 → 预测 → 因果 → 决策", "不触达", "预测准确不能证明动作有效"]:
            self.assertIn(phrase, self.cig)

    def test_all_three_relationships_are_documented(self):
        for relationship in ["CIDM ↔ CIG", "CIM ↔ CIG", "VLB ↔ CIG"]:
            self.assertIn(relationship, self.protocol)

    def test_history_and_external_execution_are_protected(self):
        self.assertIn("不静默覆盖", self.protocol)
        self.assertIn("真实曝光", self.protocol)
        self.assertIn("未授权数据", self.cig)

    def test_rules_document_cig_relationships(self):
        for skill in ["category-investment-decision", "competitive-intelligence-monitoring", "video-link-breakdown"]:
            self.assertIn(f"consumer-insights-customer-growth ↔ {skill}", self.rules)


class CrossSkillLinkIntegrity(unittest.TestCase):
    """Verify cross-skill references don't create broken local links."""

    def test_vlb_references_all_resolve(self):
        """All relative links in VLB reference files must resolve."""
        vlb_dir = ROOT / "video-link-breakdown"
        link_re = re.compile(r"\[[^]]+\]\(([^)]+)\)")
        for md_file in vlb_dir.rglob("*.md"):
            text = md_file.read_text(encoding="utf-8")
            for target in link_re.findall(text):
                if "://" in target or target.startswith("#"):
                    continue
                local_target = target.split("#", 1)[0]
                if local_target:
                    resolved = (md_file.parent / local_target).resolve()
                    self.assertTrue(
                        resolved.exists(),
                        f"{md_file.relative_to(ROOT)}: broken link {target}",
                    )

    def test_cidm_references_all_resolve(self):
        """All relative links in CIDM reference files must resolve."""
        cidm_dir = ROOT / "category-investment-decision"
        link_re = re.compile(r"\[[^]]+\]\(([^)]+)\)")
        for md_file in cidm_dir.rglob("*.md"):
            text = md_file.read_text(encoding="utf-8")
            for target in link_re.findall(text):
                if "://" in target or target.startswith("#"):
                    continue
                local_target = target.split("#", 1)[0]
                if local_target:
                    resolved = (md_file.parent / local_target).resolve()
                    self.assertTrue(
                        resolved.exists(),
                        f"{md_file.relative_to(ROOT)}: broken link {target}",
                    )

    def test_d09_references_all_resolve(self):
        d09_dir = ROOT / "advertising-analysis-measurement-optimization"
        link_re = re.compile(r"\[[^]]+\]\(([^)]+)\)")
        for md_file in d09_dir.rglob("*.md"):
            for target in link_re.findall(md_file.read_text(encoding="utf-8")):
                if "://" in target or target.startswith("#"):
                    continue
                local_target = target.split("#", 1)[0]
                if local_target:
                    self.assertTrue((md_file.parent / local_target).resolve().exists(), f"{md_file.relative_to(ROOT)}: broken link {target}")

    def test_d08_references_all_resolve(self):
        d08_dir = ROOT / "platform-store-listing-conversion"
        link_re = re.compile(r"\[[^]]+\]\(([^)]+)\)")
        for md_file in d08_dir.rglob("*.md"):
            for target in link_re.findall(md_file.read_text(encoding="utf-8")):
                if "://" in target or target.startswith("#"):
                    continue
                local_target = target.split("#", 1)[0]
                if local_target:
                    self.assertTrue((md_file.parent / local_target).resolve().exists(), f"{md_file.relative_to(ROOT)}: broken link {target}")


class ProductTransferabilityProtocol(unittest.TestCase):
    """Verify cidm-integration.md enforces product transferability assessment before dimension adjustments."""

    def setUp(self) -> None:
        self.integration_text = VLB_CIDM_INTEGRATION.read_text(encoding="utf-8")

    def test_transferability_section_exists(self):
        """cidm-integration.md must have a product transferability assessment section."""
        self.assertIn("产品可迁移性评估", self.integration_text)

    def test_three_transfer_levels_defined(self):
        """Must define 同品, 相近品, 跨品类 transfer levels."""
        for level in ["同品", "相近品", "跨品类"]:
            self.assertIn(level, self.integration_text, f"Missing transfer level: {level}")

    def test_confidence_downgrade_for_adjacent_products(self):
        """相近品 level must trigger confidence downgrade."""
        self.assertIn("置信度降一级", self.integration_text)

    def test_cross_category_no_scoring(self):
        """跨品类 level must not produce dimension adjustments."""
        # Find the 跨品类 row and verify it says no dimension adjustment
        cross_category_pattern = r"跨品类.*不做维度调整"
        self.assertRegex(
            self.integration_text,
            cross_category_pattern,
            "跨品类 level must explicitly state no dimension adjustments",
        )

    def test_output_protocol_starts_with_transferability(self):
        """Output protocol must list transferability assessment as first item."""
        # The output protocol section should mention transferability before dimension adjustments
        output_section = self.integration_text[self.integration_text.index("## 输出协议") :]
        transfer_pos = output_section.index("产品可迁移性评估")
        dimension_pos = output_section.index("逐项调整说明")
        self.assertLess(
            transfer_pos,
            dimension_pos,
            "Transferability assessment must come before dimension adjustments in output protocol",
        )

    def test_validation_actions_required(self):
        """相近品 level must require transferability validation actions."""
        self.assertIn("迁移性验证动作", self.integration_text)

    def test_transferability_before_mapping(self):
        """Transferability section must come before write-back mapping section."""
        transfer_pos = self.integration_text.index("产品可迁移性评估")
        mapping_pos = self.integration_text.index("## 回写映射")
        self.assertLess(
            transfer_pos,
            mapping_pos,
            "Transferability assessment must come before write-back mapping",
        )


class PreFlightConsistencyCheck(unittest.TestCase):
    """Verify cidm-integration.md requires pre-flight product consistency check before analysis."""

    def setUp(self) -> None:
        self.integration_text = VLB_CIDM_INTEGRATION.read_text(encoding="utf-8")

    def test_preflight_check_section_exists(self):
        """Must have a product consistency pre-flight check section."""
        self.assertIn("产品一致性前置检查", self.integration_text)

    def test_three_products_defined(self):
        """Must define the three products to compare: CIDM target, VLB video product, VLB replication target."""
        self.assertIn("CIDM 目标产品", self.integration_text)
        self.assertIn("VLB 视频产品", self.integration_text)
        self.assertIn("VLB 复刻目标产品", self.integration_text)

    def test_all_match_scenario(self):
        """Must handle case where all three products are identical."""
        self.assertIn("A = B = C", self.integration_text)

    def test_video_differs_scenario(self):
        """Must handle case where video product differs from CIDM target."""
        self.assertIn("B ≠ A", self.integration_text)

    def test_all_different_scenario(self):
        """Must handle case where all three products are different."""
        self.assertIn("三者互不相同", self.integration_text)

    def test_preflight_before_transferability(self):
        """Pre-flight check must come before transferability assessment."""
        preflight_pos = self.integration_text.index("产品一致性前置检查")
        transfer_pos = self.integration_text.index("产品可迁移性评估")
        self.assertLess(
            preflight_pos,
            transfer_pos,
            "Pre-flight consistency check must come before transferability assessment",
        )

    def test_reminder_not_block(self):
        """Pre-flight check must remind user but not block analysis."""
        self.assertIn("提醒不等于阻断", self.integration_text)


class VersionConsistency(unittest.TestCase):
    """Verify model versions are consistent across skills and RULES.md."""

    def test_cidm_version_in_skill(self):
        """CIDM SKILL.md must declare runtime version."""
        text = CIDM_SKILL.read_text(encoding="utf-8")
        self.assertRegex(text, r"运行时版本：`CIDM-\d{4}\.\d{2}`")

    def test_vlb_version_in_skill(self):
        """VLB SKILL.md must declare runtime version."""
        text = VLB_SKILL.read_text(encoding="utf-8")
        self.assertRegex(text, r"运行时版本：`VLB-\d{4}\.\d{2}`")

    def test_versions_match_readme(self):
        """README.md must reference the same model versions as SKILL.md files."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        cidm_text = CIDM_SKILL.read_text(encoding="utf-8")
        vlb_text = VLB_SKILL.read_text(encoding="utf-8")
        d09_text = D09_SKILL.read_text(encoding="utf-8")

        cidm_version = re.search(r"`(CIDM-\d{4}\.\d{2})`", cidm_text)
        vlb_version = re.search(r"`(VLB-\d{4}\.\d{2})`", vlb_text)
        d09_version = re.search(r"`(D09-\d{4}\.\d{2})`", d09_text)
        self.assertIsNotNone(cidm_version)
        self.assertIsNotNone(vlb_version)
        self.assertIsNotNone(d09_version)
        self.assertIn(cidm_version.group(1), readme)
        self.assertIn(vlb_version.group(1), readme)
        self.assertIn(d09_version.group(1), readme)


class AdvertisingIntegration(unittest.TestCase):
    def test_rules_document_d09_relationships(self):
        rules = RULES_MD.read_text(encoding="utf-8")
        for skill in ["category-investment-decision", "competitive-intelligence-monitoring", "video-link-breakdown", "consumer-insights-customer-growth"]:
            self.assertIn(f"advertising-analysis-measurement-optimization ↔ {skill}", rules)

    def test_d09_keeps_cross_domain_outputs_non_authoritative(self):
        text = D09_SKILL.read_text(encoding="utf-8")
        for phrase in ["proposed / validated / blocked / inconclusive", "不得越权", "不拥有品类投资"]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
