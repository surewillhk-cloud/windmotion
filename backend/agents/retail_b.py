"""Retail B Agent - Gambler retail investor perspective."""
from typing import Dict
from backend.agents.base import BaseAgent


class RetailBAgent(BaseAgent):
    """散户B - 赌博型投资者。

    Characteristics:
    - 喜欢梭哈，追热点
    - FOMO情绪驱动
    - 经常在高点买入
    """

    def __init__(self, config: Dict):
        super().__init__(config)

    def build_reasoning_input(self, event: Dict, context: str, graph_snapshot: Dict) -> str:
        return f"""## 事件
类型: {event.get('type', 'N/A')}
描述: {event.get('description', 'N/A')}
涉及Token: {event.get('token', 'N/A')}
近期涨幅: {event.get('price_change_pct', 'N/A')}%

## 当前上下文
{context}

## 我的视角
我是一个赌博型散户投资者。我喜欢梭哈，看到别人赚钱就忍不住冲进去。
我不怎么看基本面，主要看K线和群里消息。涨了就觉得还能涨，跌了就死扛。
我交易频率很高，一天能操作好几次。

请基于我的视角分析此事件。
输出格式（JSON）：
{{
  "emotional_reaction": "我的情绪反应（特别是FOMO程度）",
  "probability_estimate": 65,
  "action_inclination": "我会怎么做",
  "reasoning": "我的推理（体现FOMO和过度自信）",
  "fomo_level": "高/中/低",
  "self_check": {{
    "bias_manifestation": "偏见表现",
    "blind_spot": "盲点"
  }},
  "confidence": "高/中/低"
}}"""
