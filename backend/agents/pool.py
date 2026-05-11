"""Agent Pool - Manages all agent instances."""
import json
import os
from typing import Dict, List, Optional
from backend.agents.base import BaseAgent
from backend.agents.referee import RefereeAgent
from backend.agents.director import DirectorAgent
from backend.agents.chain_analyst import ChainAnalystAgent
from backend.agents.token_analyst import TokenAnalystAgent
from backend.agents.macro_analyst import MacroAnalystAgent
from backend.agents.reviewer_a import ReviewerAAgent
from backend.agents.reviewer_b import ReviewerBAgent
from backend.agents.reviewer_c import ReviewerCAgent
from backend.agents.retail_a import RetailAAgent
from backend.agents.retail_b import RetailBAgent
from backend.agents.retail_c import RetailCAgent
from backend.agents.social_a import SocialAAgent
from backend.agents.social_b import SocialBAgent
from backend.agents.institutional import InstitutionalAgent


AGENT_CLASS_MAP = {
    "referee": RefereeAgent,
    "director": DirectorAgent,
    "chain_analyst": ChainAnalystAgent,
    "token_analyst": TokenAnalystAgent,
    "macro_analyst": MacroAnalystAgent,
    "reviewer_a": ReviewerAAgent,
    "reviewer_b": ReviewerBAgent,
    "reviewer_c": ReviewerCAgent,
    "retail_a": RetailAAgent,
    "retail_b": RetailBAgent,
    "retail_c": RetailCAgent,
    "social_a": SocialAAgent,
    "social_b": SocialBAgent,
    "institutional": InstitutionalAgent,
}


class AgentPool:
    """Manages all agent instances."""

    def __init__(self, config_path: Optional[str] = None):
        self.agents: Dict[str, BaseAgent] = {}
        self._load_agents(config_path)

    def _load_agents(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'agents.json')

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            return

        for agent_config in data.get("agents", []):
            agent_id = agent_config["id"]
            agent_class = AGENT_CLASS_MAP.get(agent_id)
            if agent_class:
                self.agents[agent_id] = agent_class(agent_config)

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        return self.agents.get(agent_id)

    def get_by_type(self, agent_type: str) -> List[BaseAgent]:
        return [a for a in self.agents.values() if a.type == agent_type]

    def get_b_agents(self) -> List[BaseAgent]:
        return self.get_by_type("B")

    def get_c_agents(self) -> List[BaseAgent]:
        return self.get_by_type("C")

    def get_all(self) -> List[BaseAgent]:
        return list(self.agents.values())

    def get_profiles(self) -> Dict:
        return {aid: agent.profile.to_dict() for aid, agent in self.agents.items()}
