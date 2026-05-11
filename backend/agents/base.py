"""Agent Base Class - Defines the interface for all agents."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os


@dataclass
class AgentProfile:
    """Persistent agent profile maintained across analysis sessions."""
    agent_id: str
    role_description: str
    current_probability: Optional[Dict] = None
    history: List[Dict] = field(default_factory=list)
    memory_summary: str = ""
    self_check_records: List[Dict] = field(default_factory=list)

    def update_probability(self, value: int, reason: str, confidence: str):
        self.current_probability = {
            "value": value,
            "reason": reason,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def add_history(self, event_id: str, probability: int, reason: str, self_check: Dict):
        self.history.append({
            "event_id": event_id,
            "probability": probability,
            "reason": reason,
            "self_check": self_check,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "role_description": self.role_description,
            "current_probability": self.current_probability,
            "history": self.history[-20:],
            "memory_summary": self.memory_summary,
            "self_check_records": self.self_check_records[-10:]
        }


class BaseAgent:
    """Base class for all agents in the system."""

    def __init__(self, config: Dict):
        self.id = config["id"]
        self.type = config["type"]
        self.name = config["name"]
        self.name_en = config.get("name_en", config["name"])
        self.model_tier = config["model_tier"]
        self.role_description = config["role_description"]
        self.stance = config.get("stance", "")
        self.cognitive_traits = config.get("cognitive_traits", [])
        self.cognitive_biases = config.get("cognitive_biases", [])
        self.knowledge_domains = config.get("knowledge_domains", [])
        self.profile = AgentProfile(
            agent_id=self.id,
            role_description=self.role_description
        )

    def get_system_prompt(self) -> str:
        traits = "\n".join(f"  - {t}" for t in self.cognitive_traits)
        biases = "\n".join(f"  - {b}" for b in self.cognitive_biases)
        domains = ", ".join(self.knowledge_domains)
        return f"""你是 {self.name}（{self.name_en}）。

身份：{self.role_description}

立场：{self.stance}

认知特征：
{traits}

认知偏见（注意自我纠正）：
{biases}

知识领域：{domains}

请用中文回答。分析要具体、有数据支撑，避免泛泛而谈。"""

    def get_role_context(self) -> Dict:
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "agent_type": self.type,
            "model_tier": self.model_tier,
            "stance": self.stance,
            "cognitive_biases": self.cognitive_biases
        }

    def build_reasoning_input(self, event: Dict, context: str, graph_snapshot: Dict) -> str:
        return f"""## 事件
{json.dumps(event, ensure_ascii=False, indent=2)}

## 当前上下文
{context}

## 因果图谱快照
节点数: {len(graph_snapshot.get('nodes', []))}
边数: {len(graph_snapshot.get('edges', []))}

请基于你的角色立场，分析此事件对预测目标的影响。

输出格式（JSON）：
{{
  "causal_analysis": "你的因果分析...",
  "probability_estimate": 65,
  "reasoning_chain": ["步骤1", "步骤2", ...],
  "self_check": {{
    "deviation": "可能的偏离点",
    "blind_spot": "可能的盲点",
    "counter_evidence": "反面证据"
  }},
  "confidence": "高/中/低"
}}"""

    def build_self_check_prompt(self, analysis_result: Dict, other_results: List[Dict]) -> str:
        others_summary = "\n".join(
            f"- {r.get('agent_name', 'Unknown')}: {r.get('probability_estimate', 'N/A')}%"
            for r in other_results
        )
        return f"""## 你的分析结果
概率估计: {analysis_result.get('probability_estimate', 'N/A')}%

## 其他参与者的估计
{others_summary}

## 自检要求
1. 你的估计与其他人的偏差是什么原因？
2. 你是否遗漏了重要信息？
3. 你的认知偏见是否影响了判断？

输出格式（JSON）：
{{
  "deviation_analysis": "偏差分析",
  "blind_spots": ["盲点1", ...],
  "bias_check": "偏见检查",
  "adjusted_probability": 65,
  "adjustment_reason": "调整原因"
}}"""
