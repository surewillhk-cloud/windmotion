"""Retail C Agent - Follower retail investor perspective."""
from typing import Dict
from backend.agents.base import BaseAgent


class RetailCAgent(BaseAgent):
    """散户C - 跟风型投资者。

    Characteristics:
    - 没有自己的判断体系
    - 主要看社交媒体和群里的消息
    - 别人买什么就买什么
    """

    def __init__(self, config: Dict):
        super().__init__(config)

    def build_reasoning_input(self, event: Dict, context: str, graph_snapshot: Dict) -> str:
        return f"""## 事件
类型: {event.get('type', 'N/A')}
描述: {event.get('description', 'N/A')}
社交媒体热度: {event.get('social_mentions', 'N/A')}

## 当前上下文
{context}

## 我的视角
我是一个跟风型散户投资者。我没有自己的分析能力，主要看群里和Twitter上别人怎么说。
如果群里大佬说买，我就买。如果Twitter上很多人讨论某个币，我也会关注。
我不太懂技术分析和基本面分析，就是跟着感觉走。

请基于我的视角分析此事件。
输出格式（JSON）：
{{
  "social_signal": "我看到的社交信号",
  "crowd_sentiment": "大众情绪（看多/看空/中性）",
  "probability_estimate": 55,
  "action_inclination": "我会怎么做",
  "reasoning": "我的推理（主要是从众逻辑）",
  "self_check": {{
    "bias_manifestation": "从众偏见如何影响我",
    "blind_spot": "我忽略的独立分析"
  }},
  "confidence": "高/中/低"
}}"""
