"""S5: Report Generate - Generates structured analysis reports."""
import json
import os
import time
from typing import Dict, List, Optional
from backend.skills.base import BaseSkill, SkillResult


class ReportGenerate(BaseSkill):
    """Generates structured analysis reports using referee and chain analyst."""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.skill_id = "S5_ReportGenerate"

    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        start_time = time.time()
        valid, err = self.validate_inputs(inputs)
        if not valid:
            return self._create_result(False, {}, err, start_time)

        analysis_data = inputs.get("analysis_data", {})
        agent_pool = context.get("agent_pool") if context else None
        llm_caller = context.get("llm_caller") if context else None

        if not agent_pool or not llm_caller:
            return self._create_result(False, {}, "Missing agent_pool or llm_caller in context", start_time)

        # Generate narrative using chain analyst
        chain_analyst = agent_pool.get("chain_analyst")
        narrative_prompt = f"""## 任务：撰写分析叙事

### 分析结果
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

### 要求
请用通俗易懂的中文撰写分析叙事，包括：
1. 事件背景
2. 关键发现
3. 多方观点对比
4. 最终判断和理由

输出格式（JSON）：
{{
  "narrative": "完整的分析叙事文本（500-800字）",
  "key_insights": ["核心洞察1", "核心洞察2", "核心洞察3"]
}}"""

        narrative_result = await llm_caller(
            model_tier="medium",
            system_prompt=chain_analyst.get_system_prompt(),
            user_message=narrative_prompt,
            task_type="narrative_generation"
        )

        narrative_data = narrative_result.get("data", {}) if narrative_result.get("success") else {}
        narrative_text = narrative_data.get("narrative", "无法生成叙事。")

        # Generate structured report using referee
        referee = agent_pool.get("referee")
        report_prompt = referee.build_report_prompt(analysis_data, narrative_text)
        report_result = await llm_caller(
            model_tier="heavy",
            system_prompt=referee.get_system_prompt(),
            user_message=report_prompt,
            task_type="report_generation"
        )

        if not report_result.get("success"):
            return self._create_result(False, {}, f"Report generation failed: {report_result.get('error')}", start_time)

        report_data = report_result.get("data", {})

        return self._create_result(True, {
            "report": report_data,
            "narrative": narrative_text,
            "key_insights": narrative_data.get("key_insights", []),
            "prediction": report_data.get("prediction", {}),
            "executive_summary": report_data.get("executive_summary", ""),
            "risk_factors": report_data.get("risk_factors", []),
            "supporting_evidence": report_data.get("supporting_evidence", [])
        }, start_time=start_time)

    def validate_inputs(self, inputs: Dict) -> tuple[bool, Optional[str]]:
        if "analysis_data" not in inputs:
            return False, "Missing 'analysis_data' in inputs"
        return True, None
