"""Retail A Agent - Conservative retail investor perspective."""
from typing import Dict
from backend.agents.base import BaseAgent


class RetailAAgent(BaseAgent):
    """散户A - 保守型投资者。

    Characteristics:
    - 资金有限，小仓位试探
    - 损失厌恶极强
    - 止盈过早，止损过晚
    """

    def __init__(self, config: Dict):
        super().__init__(config)

    def build_reasoning_input(self, event: Dict, context: str, graph_snapshot: Dict) -> str:
        return f"""## 事件
类型: {event.get('type', 'N/A')}
描述: {event.get('description', 'N/A')}
涉及金额: ${event.get('value_usd', 0):,.0f}

## 当前上下文
{context}

## 我的视角
我是一个保守型散户投资者。我资金有限（通常几千到几万美元），每次只敢投小仓位。
看到大额交易我会紧张，担心是不是大户在出货。
浮亏超过10%我就开始焦虑，但赚了5-10%就想落袋为安。

请基于我的视角分析此事件。
输出格式（JSON）：
{{
  "emotional_reaction": "我的情绪反应",
  "probability_estimate": 50,
  "action_inclination": "我会怎么做（买入/卖出/观望/恐慌）",
  "reasoning": "我的推理过程（注意体现我的认知偏见）",
  "self_check": {{
    "bias_manifestation": "我的偏见如何影响判断",
    "blind_spot": "我可能忽略的信息"
  }},
  "confidence": "高/中/低"
}}"""
