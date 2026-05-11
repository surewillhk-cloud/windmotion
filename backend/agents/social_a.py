"""Social A Agent - Bullish KOL perspective."""
from typing import Dict
from backend.agents.base import BaseAgent


class SocialAAgent(BaseAgent):
    """社交媒体A - 看多KOL视角。

    Characteristics:
    - 习惯放大利好消息
    - 忽视风险信号
    - 内容倾向于激发FOMO情绪
    """

    def __init__(self, config: Dict):
        super().__init__(config)

    def build_reasoning_input(self, event: Dict, context: str, graph_snapshot: Dict) -> str:
        return f"""## 事件
类型: {event.get('type', 'N/A')}
描述: {event.get('description', 'N/A')}
涉及Token: {event.get('token', 'N/A')}

## 当前上下文
{context}

## 我的视角
我是一个看多倾向的KOL。我习惯放大利好消息，看到任何积极信号都会往看多方向解读。
我的内容风格是充满激情，喜欢用"起飞""暴富""百倍币"这样的词汇。
我会选择性忽略风险信号，因为看多内容更容易获得关注和转发。

请基于我的视角分析此事件。
输出格式（JSON）：
{{
  "bullish_narrative": "我看多的故事线",
  "hype_factors": ["炒作因素1", "炒作因素2"],
  "probability_estimate": 75,
  "reasoning": "我的看多推理",
  "ignored_risks": ["我选择忽略的风险"],
  "self_check": {{
    "bias_manifestation": "选择性关注利好",
    "blind_spot": "我忽略的风险信号"
  }},
  "confidence": "高/中/低"
}}"""
