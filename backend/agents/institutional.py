"""Institutional Agent - Institutional investor perspective."""
from typing import Dict
from backend.agents.base import BaseAgent


class InstitutionalAgent(BaseAgent):
    """机构投资者 - 机构资金管理者。

    Characteristics:
    - 管理大资金
    - 风险控制第一优先级
    - 决策流程严谨
    - 需要多维度数据支撑
    """

    def __init__(self, config: Dict):
        super().__init__(config)

    def build_reasoning_input(self, event: Dict, context: str, graph_snapshot: Dict) -> str:
        return f"""## 事件
类型: {event.get('type', 'N/A')}
描述: {event.get('description', 'N/A')}
涉及金额: ${event.get('value_usd', 0):,.0f}
流动性深度: ${event.get('liquidity_usd', 0):,.0f}

## 当前上下文
{context}

## 我的视角
我是一个机构资金管理者。我管理着数千万到数亿美元的资金。
风险控制是我的第一优先级。我不会因为FOMO而冲动交易。
我的决策需要多维度数据支撑：链上数据、基本面、宏观环境、流动性评估。
我特别关注执行成本和市场冲击成本。大额交易会显著影响市场价格。

请基于我的视角分析此事件。
输出格式（JSON）：
{{
  "risk_assessment": "风险评估",
  "liquidity_analysis": "流动性分析（能否容纳我的头寸）",
  "execution_feasibility": "执行可行性",
  "probability_estimate": 50,
  "reasoning": "我的严谨推理过程",
  "position_sizing": "建议仓位（占总资金百分比）",
  "risk_reward_ratio": "风险回报比",
  "self_check": {{
    "bias_manifestation": "过度谨慎可能的代价",
    "blind_spot": "可能忽略的机会"
  }},
  "confidence": "高/中/低"
}}"""
