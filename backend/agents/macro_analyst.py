"""Macro Analyst Agent - Macro market analysis expert."""
from typing import Dict
from backend.agents.base import BaseAgent


class MacroAnalystAgent(BaseAgent):
    """宏观环境分析师 - 宏观市场分析师。

    Focus areas:
    - BTC/ETH市场走势
    - 市场周期理论
    - 监管动态
    - 宏观经济指标
    - 市场情绪指标
    """

    def __init__(self, config: Dict):
        super().__init__(config)

    def build_macro_analysis_prompt(self, market_data: Dict, context: str) -> str:
        return f"""## 任务：宏观环境分析

### 市场数据
{{
  "btc_price": {market_data.get('btc_price', 0)},
  "btc_24h_change_pct": {market_data.get('btc_24h_change_pct', 0)},
  "eth_price": {market_data.get('eth_price', 0)},
  "total_market_cap": {market_data.get('total_market_cap', 0)},
  "fear_greed_index": {market_data.get('fear_greed_index', 50)},
  "btc_dominance": {market_data.get('btc_dominance', 50)},
  "funding_rate": {market_data.get('funding_rate', 0)},
  "recent_news": {market_data.get('recent_news', [])}
}}

### 上下文
{context}

### 分析要求
1. 评估当前市场周期阶段
2. 分析系统性风险
3. 评估监管环境
4. 判断市场情绪
5. 对目标Token/事件的宏观影响

输出格式（JSON）：
{{
  "market_cycle_phase": "accumulation|markup|distribution|decline",
  "systemic_risk_level": "高/中/低",
  "regulatory_sentiment": "积极|中性|消极",
  "market_emotion": "极度恐惧|恐惧|中性|贪婪|极度贪婪",
  "macro_impact_on_target": "正面|中性|负面",
  "probability_estimate": 55,
  "key_macro_factors": ["因素1", "因素2"],
  "reasoning": "分析推理"
}}"""
