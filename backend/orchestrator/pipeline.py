"""Forward Inference Pipeline - Orchestrates the full 6-phase analysis."""
import asyncio
import json
import logging
import time
from typing import Dict, Optional
from backend.orchestrator.phase_manager import PhaseManager, PhaseStatus
from backend.orchestrator.timeout import TimeoutManager
from backend.orchestrator.async_handler import AsyncHandler
from backend.orchestrator.ws_progress import WSProgressManager
from backend.agents.pool import AgentPool
from backend.skills.model_route import ModelRouter

logger = logging.getLogger(__name__)


class ForwardPipeline:
    """Orchestrates the forward inference pipeline (Phase 0-5)."""

    def __init__(self, agent_pool: AgentPool, model_router: ModelRouter,
                 ws_manager: WSProgressManager, timeout_config: Dict):
        self.agents = agent_pool
        self.model_router = model_router
        self.ws = ws_manager
        self.timeout_mgr = TimeoutManager(timeout_config)
        self.async_handler = AsyncHandler()
        self.phase_manager = PhaseManager(self.timeout_mgr.phase_timeouts)
        self.results: Dict = {}

    async def run(self, analysis_id: str, inputs: Dict) -> Dict:
        """Execute the full forward inference pipeline."""
        start_time = time.time()
        logger.info(f"Starting forward pipeline for {analysis_id}")

        self.phase_manager.on_progress(
            lambda ph, st, dt: asyncio.ensure_future(
                self.ws.notify_step(analysis_id, ph, st, 0, str(st), dt)
            )
        )

        # Phase 0: Data Preparation
        phase0 = await self.phase_manager.execute_phase(
            "phase_0", self._phase_0_data_prep, inputs
        )
        if phase0.status != PhaseStatus.COMPLETED:
            return self._build_error_result(analysis_id, "phase_0", phase0.error)

        # Phase 1: Causal Graph Build
        phase1 = await self.phase_manager.execute_phase(
            "phase_1", self._phase_1_graph_build, phase0.data
        )
        if phase1.status != PhaseStatus.COMPLETED:
            return self._build_error_result(analysis_id, "phase_1", phase1.error)

        # Phase 2: Event Chain Processing
        phase2 = await self.phase_manager.execute_phase(
            "phase_2", self._phase_2_event_chain, {**phase0.data, **phase1.data}
        )

        # Phase 3: Deliberation (can run parallel with late Phase 2)
        phase3 = await self.phase_manager.execute_phase(
            "phase_3", self._phase_3_deliberation, {**phase1.data, **phase2.data}
        )

        # Phase 4: Final Review
        phase4 = await self.phase_manager.execute_phase(
            "phase_4", self._phase_4_review, {
                "graph": phase1.data.get("graph"),
                "events": phase2.data,
                "deliberation": phase3.data
            }
        )

        # Phase 5: Report Generation
        phase5 = await self.phase_manager.execute_phase(
            "phase_5", self._phase_5_report, {
                "graph": phase1.data.get("graph"),
                "events": phase2.data,
                "deliberation": phase3.data,
                "review": phase4.data,
                "format": inputs.get("format", "full")
            }
        )

        total_time = time.time() - start_time
        logger.info(f"Pipeline completed in {total_time:.1f}s")

        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "total_time_s": total_time,
            "report": phase5.data.get("report"),
            "narrative": phase5.data.get("narrative"),
            "graph": phase1.data.get("graph"),
            "probability_timeline": phase2.data.get("probability_timeline"),
            "deliberation_records": phase3.data.get("records"),
            "phase_summary": self.phase_manager.get_summary()
        }

    async def _phase_0_data_prep(self, inputs: Dict) -> Dict:
        """Phase 0: Fetch data, parse transactions, calculate factors."""
        address = inputs["address"]
        chain = inputs.get("chain", "bsc")

        # Import skills lazily
        from backend.skills.data_fetch import DataFetch
        from backend.skills.factor_reverse import FactorReverse

        data_fetch = DataFetch()
        factor_reverse = FactorReverse()

        # Fetch transaction history
        fetch_result = await data_fetch.execute({
            "address": address,
            "chain": chain,
            "data_types": ["transactions", "token_transfers", "dex_swaps"]
        })

        if not fetch_result.success:
            raise Exception(f"Data fetch failed: {fetch_result.error}")

        # Parse transactions and identify rounds
        factor_result = await factor_reverse.execute({
            "whale_address": address,
            "trade_history": fetch_result.data.get("transactions", []),
            "token_price_history": {}
        })

        return {
            "address": address,
            "chain": chain,
            "raw_data": fetch_result.data,
            "rounds": factor_result.data.get("rounds", []),
            "factor_scores": factor_result.data.get("factor_scores", {}),
            "strategy_pattern": factor_result.data.get("strategy_pattern")
        }

    async def _phase_1_graph_build(self, inputs: Dict) -> Dict:
        """Phase 1: Build causal graph with referee + reviewers."""
        from backend.skills.causal_graph_build import CausalGraphBuild

        graph_skill = CausalGraphBuild()
        result = await graph_skill.execute({
            "seed_data": {
                "rounds": inputs.get("rounds", []),
                "factors": inputs.get("factor_scores", {}),
                "pattern": inputs.get("strategy_pattern")
            },
            "target": inputs.get("target", "profitability"),
            "constraints": {}
        }, context={"agent_pool": self.agents, "model_router": self.model_router})

        if not result.success:
            raise Exception(f"Graph build failed: {result.error}")

        return {"graph": result.data.get("graph"), "activation_map": result.data.get("activation_map")}

    async def _phase_2_event_chain(self, inputs: Dict) -> Dict:
        """Phase 2: Process events through agent analysis."""
        from backend.skills.event_analyze import EventAnalyze
        from backend.skills.probability_price import ProbabilityPrice

        events = inputs.get("events", [])
        graph = inputs.get("graph", {})
        activation_map = inputs.get("activation_map", {})

        event_skill = EventAnalyze()
        prob_skill = ProbabilityPrice()

        all_results = []
        probability_timeline = []
        context = ""

        # Director groups events
        event_groups = self._group_events(events)

        for group in event_groups:
            group_results = []
            for event in group:
                event_type = event.get("type", "default")
                activated = activation_map.get(event_type, ["chain_analyst", "token_analyst", "macro_analyst"])

                result = await event_skill.execute({
                    "event": event,
                    "graph_snapshot": graph,
                    "context": context,
                    "activated_agents": activated
                }, context={"agent_pool": self.agents})

                if result.success:
                    group_results.append(result.data)
                    context += f"\n{result.data.get('event_summary', '')}"

            # Probability pricing after each group
            prob_result = await prob_skill.execute({
                "reasoning_results": group_results,
                "graph_snapshot": graph,
                "agent_profiles": self.agents.get_profiles()
            })

            if prob_result.success:
                probability_timeline.append({
                    "aggregate": prob_result.data.get("weighted_aggregate"),
                    "std_dev": prob_result.data.get("std_dev"),
                    "spread": prob_result.data.get("max_spread")
                })

            all_results.extend(group_results)

        return {
            "event_results": all_results,
            "probability_timeline": probability_timeline,
            "context": context
        }

    async def _phase_3_deliberation(self, inputs: Dict) -> Dict:
        """Phase 3: Run deliberation if triggered."""
        from backend.skills.deliberate import Deliberate

        prob_timeline = inputs.get("probability_timeline", [])
        if not prob_timeline:
            return {"triggered": False, "records": []}

        last_prob = prob_timeline[-1] if prob_timeline else {}
        should_trigger = (
            last_prob.get("spread", 0) > 30 or
            abs(last_prob.get("change", 0)) > 15
        )

        if not should_trigger:
            return {"triggered": False, "records": []}

        deliberation = Deliberate()
        result = await deliberation.execute({
            "trigger_reason": "Probability spread exceeded threshold",
            "probability_dist": last_prob,
            "graph_snapshot": inputs.get("graph", {}),
            "participants": ["chain_analyst", "token_analyst", "retail_a", "institutional"],
            "context": inputs.get("context", "")
        }, context={"agent_pool": self.agents, "model_router": self.model_router})

        return {
            "triggered": True,
            "records": result.data if result.success else {}
        }

    async def _phase_4_review(self, inputs: Dict) -> Dict:
        """Phase 4: Final review - consensus/divergence identification."""
        graph = inputs.get("graph", {})
        deliberation = inputs.get("deliberation", {})

        # Identify consensus and divergence points
        consensus = []
        divergence = []

        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        # Analyze edge verification status
        for edge in edges:
            if edge.get("verified") == True:
                consensus.append(edge)
            elif edge.get("verified") == False:
                divergence.append(edge)

        return {
            "consensus_paths": len(consensus),
            "divergence_paths": len(divergence),
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "deliberation_triggered": deliberation.get("triggered", False)
        }

    async def _phase_5_report(self, inputs: Dict) -> Dict:
        """Phase 5: Generate final report and narrative."""
        from backend.skills.report_generate import ReportGenerate

        report_skill = ReportGenerate()
        result = await report_skill.execute({
            "final_graph": inputs.get("graph", {}),
            "probability_timeline": inputs.get("events", {}).get("probability_timeline", []),
            "deliberation_records": inputs.get("deliberation", {}).get("records", {}),
            "review_output": inputs.get("review", {}),
            "format": inputs.get("format", "full")
        }, context={"agent_pool": self.agents})

        return result.data if result.success else {"report": {}, "narrative": {}}

    def _group_events(self, events: list) -> list:
        """Group events by dependency for sequential/parallel processing."""
        if not events:
            return []
        # Simple grouping: batch of 2-3 events per group
        groups = []
        for i in range(0, len(events), 2):
            groups.append(events[i:i+2])
        return groups

    def _build_error_result(self, analysis_id: str, phase: str, error: str) -> Dict:
        return {
            "analysis_id": analysis_id,
            "status": "failed",
            "failed_phase": phase,
            "error": error,
            "phase_summary": self.phase_manager.get_summary()
        }
