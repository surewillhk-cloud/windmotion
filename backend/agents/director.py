"""Director Agent - Process controller for event injection and scheduling."""
from typing import Dict, List, Optional
from backend.agents.base import BaseAgent


class DirectorAgent(BaseAgent):
    """导演 Agent - 流程控制者。

    Responsibilities:
    - 事件注入
    - 事件依赖分析
    - 事件分组和调度
    """

    def __init__(self, config: Dict):
        super().__init__(config)

    def build_dependency_analysis_prompt(self, events: List[Dict]) -> str:
        events_text = "\n".join(
            f"- [{e.get('id', 'N/A')}] {e.get('description', 'N/A')} (时间: {e.get('timestamp', 'N/A')})"
            for e in events
        )
        return f"""## 任务：分析事件依赖关系

### 事件列表
{events_text}

### 要求
分析事件之间的依赖关系，确定哪些事件可以并行处理，哪些必须串行处理。

输出格式（JSON）：
{{
  "groups": [
    {{
      "group_id": 1,
      "event_ids": ["event_1", "event_2"],
      "execution": "parallel",
      "reason": "这些事件之间没有因果依赖"
    }},
    {{
      "group_id": 2,
      "event_ids": ["event_3"],
      "execution": "sequential",
      "depends_on": [1],
      "reason": "此事件依赖于第一组的结果"
    }}
  ],
  "event_type_map": {{
    "event_1": "trade_event",
    "event_2": "social_event"
  }}
}}"""

    def build_dispatch_prompt(self, event: Dict, agent_ids: List[str]) -> str:
        return f"""## 任务：事件分派

### 事件
类型: {event.get('type', 'unknown')}
描述: {event.get('description', 'N/A')}

### 可用分析者
{', '.join(agent_ids)}

### 要求
确定此事件需要哪些分析者参与，以及每个分析者的分析重点。

输出格式（JSON）：
{{
  "event_id": "{event.get('id', 'N/A')}",
  "selected_agents": [
    {{"agent_id": "...", "focus": "分析重点"}}
  ],
  "priority": "high/medium/low",
  "parallel": true
}}"""
