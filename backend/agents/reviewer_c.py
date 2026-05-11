"""Reviewer C Agent - Variable Detection for causal graphs."""
from typing import Dict, List
from backend.agents.base import BaseAgent


class ReviewerCAgent(BaseAgent):
    """审查AgentC - 变量检测专家。

    Responsibility: 检查因果图谱中是否缺少关键变量或实体。
    """

    def __init__(self, config: Dict):
        super().__init__(config)

    def build_review_prompt(self, graph: Dict, context: str) -> str:
        nodes_summary = "\n".join(
            f"- [{n.get('id')}] {n.get('label', 'N/A')} (类型: {n.get('type', 'N/A')})"
            for n in graph.get('nodes', [])
        )
        return f"""## 任务：关键变量检测

### 当前图谱节点
{nodes_summary}

### 分析上下文
{context}

### 检查要求
1. 是否缺少关键的控制变量？
2. 是否缺少重要的背景变量？
3. 是否缺少中介变量（连接两个看似无关的节点）？
4. 是否缺少调节变量（影响因果强度的因素）？

输出格式（JSON）：
{{
  "issues": [
    {{
      "type": "missing_control|missing_background|missing_mediator|missing_moderator",
      "description": "缺失变量描述",
      "related_nodes": ["相关节点ID"],
      "severity": "高/中/低",
      "suggested_variable": {{
        "label": "变量名称",
        "type": "factor|context|mechanism",
        "connections": [{{"to": "node_id", "relation": "关系描述"}}]
      }}
    }}
  ],
  "suggestions": [
    {{
      "action": "add_variable",
      "details": {{...}},
      "reason": "添加理由"
    }}
  ],
  "variable_completeness_score": 1-10
}}"""
