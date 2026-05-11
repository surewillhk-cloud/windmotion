"""Referee Agent - Global coordinator and final decision maker."""
from typing import Dict, List, Optional
from backend.agents.base import BaseAgent


class RefereeAgent(BaseAgent):
    """裁判 Agent - 全局协调者和最终裁决者。

    Responsibilities:
    - 生成因果图谱草案
    - 合并审查意见
    - 在审议中做最终裁决
    - 生成结构化报告
    """

    def __init__(self, config: Dict):
        super().__init__(config)

    def build_graph_draft_prompt(self, events: List[Dict], context: str) -> str:
        events_text = "\n".join(
            f"- [{e.get('id', 'N/A')}] {e.get('description', 'N/A')}"
            for e in events
        )
        return f"""## 任务：生成因果图谱草案

### 已识别事件
{events_text}

### 分析上下文
{context}

### 要求
请基于以上事件，构建一个因果图谱草案。

输出格式（JSON）：
{{
  "nodes": [
    {{"id": "node_1", "label": "节点描述", "type": "event|factor|outcome", "importance": 1-5}}
  ],
  "edges": [
    {{"source": "node_1", "target": "node_2", "relation": "导致|影响|触发", "strength": 0.0-1.0, "evidence": "证据描述"}}
  ],
  "prediction_target": "预测目标描述",
  "initial_probability": 50,
  "confidence": "高/中/低",
  "key_assumptions": ["假设1", "假设2"]
}}"""

    def build_merge_prompt(self, draft: Dict, reviews: List[Dict]) -> str:
        reviews_text = "\n\n".join(
            f"### 审查者: {r.get('agent_name', 'Unknown')} (维度: {r.get('dimension', 'N/A')})\n"
            f"发现的问题: {r.get('issues', [])}\n"
            f"建议修改: {r.get('suggestions', [])}"
            for r in reviews
        )
        return f"""## 任务：合并审查意见并修订因果图谱

### 原始草案
节点数: {len(draft.get('nodes', []))}
边数: {len(draft.get('edges', []))}

### 审查意见
{reviews_text}

### 要求
1. 采纳合理的审查意见
2. 拒绝不合理的建议并说明理由
3. 输出修订后的因果图谱

输出格式（JSON）：
{{
  "revised_graph": {{...修订后的图谱...}},
  "accepted_suggestions": [{{"source": "审查者", "suggestion": "...", "reason": "采纳理由"}}],
  "rejected_suggestions": [{{"source": "审查者", "suggestion": "...", "reason": "拒绝理由"}}],
  "final_probability": 55,
  "confidence": "高/中/低"
}}"""

    def build_ruling_prompt(self, challenge_results: List[Dict], response_results: List[Dict]) -> str:
        challenges = "\n".join(
            f"- {r.get('agent_name', 'Unknown')}: 质疑点={r.get('challenge_point', 'N/A')}, 建议概率={r.get('suggested_probability', 'N/A')}%"
            for r in challenge_results
        )
        responses = "\n".join(
            f"- {r.get('agent_name', 'Unknown')}: 回应={r.get('response', 'N/A')}, 概率={r.get('probability', 'N/A')}%"
            for r in response_results
        )
        return f"""## 任务：审议裁决

### 质疑阶段结果
{challenges}

### 回应阶段结果
{responses}

### 要求
作为裁判，请综合双方观点，做出最终裁决。

输出格式（JSON）：
{{
  "ruling_summary": "裁决总结",
  "final_probability": 60,
  "confidence": "高/中/低",
  "key_factors": ["关键因素1", "关键因素2"],
  "dissenting_notes": "如有异议的说明",
  "rationale": "裁决理由"
}}"""

    def build_report_prompt(self, analysis_data: Dict, narrative: str) -> str:
        return f"""## 任务：生成结构化分析报告

### 分析数据
{{
  "whale_address": "{analysis_data.get('whale_address', 'N/A')}",
  "prediction_target": "{analysis_data.get('prediction_target', 'N/A')}",
  "final_probability": {analysis_data.get('final_probability', 50)},
  "confidence": "{analysis_data.get('confidence', 'N/A')}",
  "events_count": {len(analysis_data.get('events', []))},
  "agents_participated": {len(analysis_data.get('agent_results', []))}
}}

### 叙事草稿
{narrative}

### 要求
生成完整的结构化报告。

输出格式（JSON）：
{{
  "executive_summary": "执行摘要（200字以内）",
  "prediction": {{
    "target": "预测目标",
    "probability": 65,
    "confidence": "高/中/低",
    "time_horizon": "时间范围"
  }},
  "key_events": [{{"event": "...", "impact": "高/中/低", "direction": "正面/负面"}}],
  "risk_factors": ["风险1", "风险2"],
  "supporting_evidence": ["证据1", "证据2"],
  "methodology": "方法论说明",
  "disclaimer": "免责声明"
}}"""
