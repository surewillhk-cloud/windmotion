"""Token Analyst Agent - Token fundamental analysis expert."""
from typing import Dict
from backend.agents.base import BaseAgent


class TokenAnalystAgent(BaseAgent):
    """Token 分析师 - Token基本面分析师。

    Focus areas:
    - 代币经济学
    - 市值评估
    - 持币分布分析
    - 合约安全
    - 流动性深度评估
    """

    def __init__(self, config: Dict):
        super().__init__(config)

    def build_token_analysis_prompt(self, token_data: Dict, context: str) -> str:
        return f"""## 任务：Token基本面分析

### Token数据
{{
  "symbol": "{token_data.get('symbol', 'N/A')}",
  "name": "{token_data.get('name', 'N/A')}",
  "chain": "{token_data.get('chain', 'N/A')}",
  "market_cap": {token_data.get('market_cap', 0)},
  "total_supply": {token_data.get('total_supply', 0)},
  "holder_count": {token_data.get('holder_count', 0)},
  "top10_holder_pct": {token_data.get('top10_holder_pct', 0)},
  "liquidity_usd": {token_data.get('liquidity_usd', 0)},
  "listing_days": {token_data.get('listing_days', 0)},
  "contract_audited": {token_data.get('contract_audited', False)}
}}

### 上下文
{context}

### 分析要求
1. 评估代币经济学合理性
2. 分析持币集中度风险
3. 评估流动性深度
4. 检查合约安全性
5. 给出综合估值判断

输出格式（JSON）：
{{
  "fundamental_score": 1-10,
  "risk_level": "高/中/低",
  "token_economics": {{
    "supply_assessment": "评估结论",
    "concentration_risk": "高/中/低",
    "vesting_schedule": "归属计划评估"
  }},
  "liquidity_assessment": {{
    "depth_rating": "深/中/浅",
    "slippage_risk": "高/中/低"
  }},
  "security_assessment": {{
    "contract_risk": "高/中/低",
    "audit_status": "已审计/未审计/部分审计"
  }},
  "probability_estimate": 60,
  "reasoning": "分析推理"
}}"""

    def build_holder_distribution_prompt(self, token: str, holders: list) -> str:
        holder_summary = "\n".join(
            f"- {h.get('address', 'N/A')[:8]}...: {h.get('balance_pct', 0):.2f}% (${h.get('value_usd', 0):,.0f})"
            for h in holders[:15]
        )
        return f"""## 任务：持币分布分析

### Token: {token}

### 前15大持仓地址
{holder_summary}

### 分析要求
1. 识别大户类型（交易所/项目方/早期投资者/散户）
2. 评估抛压风险
3. 分析持仓集中度
4. 识别可能的关联地址

输出格式（JSON）：
{{
  "distribution_summary": "分布总结",
  "whale_clusters": [{{"type": "exchange|team|investor", "addresses": [...], "total_pct": 0}}],
  "sell_pressure_risk": "高/中/低",
  "concentration_score": 1-10,
  "manipulation_risk": "高/中/低",
  "probability_estimate": 55
}}"""
