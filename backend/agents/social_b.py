"""Social B Agent - Bearish Skeptic perspective."""
from typing import Dict
from backend.agents.base import BaseAgent


class SocialBAgent(BaseAgent):
    """社交媒体B - 看空质疑者视角。

    Characteristics:
    - 倾向于怀疑每一个项目
    - 放大风险信号
    - 阴谋论倾向
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
我是一个看空/质疑者。我倾向于怀疑每一个项目，觉得大多数加密项目都是骗局或rug pull。
看到大额买入，我会想"是不是庄家在拉盘出货"。看到利好消息，我会想"是不是项目方在做PR"。
我习惯放大风险信号，对任何乐观叙事保持警惕。

请基于我的视角分析此事件。
输出格式（JSON）：
{{
  "suspicion_narrative": "我的质疑故事线",
  "risk_amplification": ["被我放大的风险1", "风险2"],
  "probability_estimate": 35,
  "reasoning": "我的质疑推理",
  "conspiracy_theories": ["可能的阴谋论（注意标注仅为猜测）"],
  "self_check": {{
    "bias_manifestation": "过度怀疑如何影响判断",
    "blind_spot": "我忽略的积极信号"
  }},
  "confidence": "高/中/低"
}}"""
