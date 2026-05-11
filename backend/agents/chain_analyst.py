"""Chain Analyst Agent - On-chain data analysis expert."""
from typing import Dict, List
from backend.agents.base import BaseAgent


class ChainAnalystAgent(BaseAgent):
    """链上分析师 - 链上数据分析专家。

    Focus areas:
    - 大额交易模式
    - 资金流向分析
    - 流动性分析
    - DEX交易机制
    - 地址行为模式识别
    """

    def __init__(self, config: Dict):
        super().__init__(config)

    def build_transaction_analysis_prompt(self, transaction: Dict, context: str) -> str:
        return f"""## 任务：链上交易分析

### 交易数据
{{
  "hash": "{transaction.get('hash', 'N/A')}",
  "from": "{transaction.get('from', 'N/A')}",
  "to": "{transaction.get('to', 'N/A')}",
  "value_usd": {transaction.get('value_usd', 0)},
  "token": "{transaction.get('token', 'N/A')}",
  "chain": "{transaction.get('chain', 'N/A')}",
  "timestamp": "{transaction.get('timestamp', 'N/A')}"
}}

### 上下文
{context}

### 分析要求
1. 识别交易模式（买入/卖出/转账/桥接/LP操作）
2. 分析资金流向
3. 评估对市场的影响
4. 识别异常行为

输出格式（JSON）：
{{
  "transaction_type": "buy|sell|transfer|bridge|lp_add|lp_remove",
  "pattern": "交易模式描述",
  "fund_flow": {{
    "source_type": "exchange|wallet|contract|bridge",
    "dest_type": "exchange|wallet|contract|bridge",
    "direction": "inflow|outflow|internal"
  }},
  "market_impact": "高/中/低",
  "anomaly_flags": ["异常标记1", ...],
  "probability_estimate": 60,
  "reasoning": "分析推理过程"
}}"""

    def build_fund_flow_prompt(self, address: str, transactions: List[Dict]) -> str:
        tx_summary = "\n".join(
            f"- {t.get('timestamp', 'N/A')}: {t.get('from', 'N/A')[:8]}...→{t.get('to', 'N/A')[:8]}... "
            f"${t.get('value_usd', 0):,.0f} ({t.get('token', 'N/A')})"
            for t in transactions[:20]
        )
        return f"""## 任务：资金流向分析

### 目标地址
{address}

### 近期交易（最多20笔）
{tx_summary}

### 分析要求
1. 识别资金的主要来源和去向
2. 分析资金流动模式
3. 识别关联地址
4. 评估资金性质（交易所热钱包/冷钱包/项目方/散户）

输出格式（JSON）：
{{
  "fund_flow_summary": "资金流向总结",
  "source_clusters": [{{"type": "exchange|whale|contract", "addresses": [...], "total_usd": 0}}],
  "dest_clusters": [{{"type": "...", "addresses": [...], "total_usd": 0}}],
  "flow_pattern": "accumulation|distribution|rotation|bridge_arbitrage",
  "risk_indicators": ["风险指标1", ...],
  "probability_estimate": 55
}}"""
