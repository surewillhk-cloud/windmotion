"""Reverse Inference Pipeline - Orchestrates reverse analysis (Phase R0-R5)."""
import asyncio
import logging
import time
from typing import Dict, Optional
from backend.orchestrator.phase_manager import PhaseManager, PhaseStatus
from backend.orchestrator.timeout import TimeoutManager
from backend.orchestrator.ws_progress import WSProgressManager
from backend.agents.pool import AgentPool
from backend.skills.model_route import ModelRouter

logger = logging.getLogger(__name__)


class ReversePipeline:
    """Orchestrates the reverse inference pipeline (Phase R0-R5)."""

    def __init__(self, agent_pool: AgentPool, model_router: ModelRouter,
                 ws_manager: WSProgressManager, timeout_config: Dict):
        self.agents = agent_pool
        self.model_router = model_router
        self.ws = ws_manager
        self.timeout_mgr = TimeoutManager(timeout_config)
        self.phase_manager = PhaseManager(self.timeout_mgr.phase_timeouts)

    async def run(self, analysis_id: str, inputs: Dict) -> Dict:
        """Execute the reverse inference pipeline."""
        start_time = time.time()
        mode = inputs.get("mode", "deep")  # fast, standard, deep

        phases_to_run = self._get_phases_for_mode(mode)
        logger.info(f"Starting reverse pipeline ({mode}) for {analysis_id}")

        results = {}

        # R0: Data Collection
        if "R0" in phases_to_run:
            r0 = await self.phase_manager.execute_phase(
                "phase_r0", self._phase_r0_data_collection, inputs
            )
            if r0.status != PhaseStatus.COMPLETED:
                return self._error_result(analysis_id, "R0", r0.error)
            results["r0"] = r0.data

        # R1: Transaction Parsing & Round Identification
        if "R1" in phases_to_run:
            r1 = await self.phase_manager.execute_phase(
                "phase_r1", self._phase_r1_round_identification, results.get("r0", {})
            )
            if r1.status != PhaseStatus.COMPLETED:
                return self._error_result(analysis_id, "R1", r1.error)
            results["r1"] = r1.data

        if mode == "fast":
            return self._build_result(analysis_id, results, start_time)

        # R2: Decision Node Identification
        if "R2" in phases_to_run:
            r2 = await self.phase_manager.execute_phase(
                "phase_r2", self._phase_r2_decision_nodes, {**results.get("r0", {}), **results.get("r1", {})}
            )
            results["r2"] = r2.data if r2.status == PhaseStatus.COMPLETED else {}

        # R3: Factor Scoring
        if "R3" in phases_to_run:
            r3 = await self.phase_manager.execute_phase(
                "phase_r3", self._phase_r3_factor_scoring, results
            )
            results["r3"] = r3.data if r3.status == PhaseStatus.COMPLETED else {}

        if mode == "standard":
            return self._build_result(analysis_id, results, start_time)

        # R4: Strategy Pattern Recognition
        if "R4" in phases_to_run:
            r4 = await self.phase_manager.execute_phase(
                "phase_r4", self._phase_r4_pattern_recognition, results
            )
            results["r4"] = r4.data if r4.status == PhaseStatus.COMPLETED else {}

        # R5: Report Generation
        if "R5" in phases_to_run:
            r5 = await self.phase_manager.execute_phase(
                "phase_r5", self._phase_r5_report, results
            )
            results["r5"] = r5.data if r5.status == PhaseStatus.COMPLETED else {}

        return self._build_result(analysis_id, results, start_time)

    def _get_phases_for_mode(self, mode: str) -> list:
        mapping = {
            "fast": ["R0", "R1"],
            "standard": ["R0", "R1", "R2", "R3"],
            "deep": ["R0", "R1", "R2", "R3", "R4", "R5"]
        }
        return mapping.get(mode, mapping["deep"])

    async def _phase_r0_data_collection(self, inputs: Dict) -> Dict:
        from backend.skills.data_fetch import DataFetch
        from backend.skills.price_oracle import PriceOracle

        address = inputs["address"]
        chain = inputs.get("chain", "bsc")

        data_fetch = DataFetch()
        price_oracle = PriceOracle()

        fetch_result = await data_fetch.execute({
            "address": address,
            "chain": chain,
            "data_types": ["transactions", "token_transfers", "dex_swaps"]
        })

        if not fetch_result.success:
            raise Exception(f"Data fetch failed: {fetch_result.error}")

        transactions = fetch_result.data.get("transactions", [])
        tokens = list(set(tx.get("token_address", "") for tx in transactions if tx.get("token_address")))

        # Fetch prices for discovered tokens
        price_result = await price_oracle.execute({
            "token_address": tokens[0] if tokens else "",
            "chain": chain
        })

        return {
            "address": address,
            "chain": chain,
            "transactions": transactions,
            "token_prices": price_result.data if price_result.success else {},
            "raw_data": fetch_result.data
        }

    async def _phase_r1_round_identification(self, inputs: Dict) -> Dict:
        from backend.skills.factor_reverse import FactorReverse

        factor_skill = FactorReverse()
        result = await factor_skill.execute({
            "whale_address": inputs.get("address", ""),
            "trade_history": inputs.get("transactions", []),
            "token_price_history": inputs.get("token_prices", {})
        })

        if not result.success:
            raise Exception(f"Round identification failed: {result.error}")

        return {
            "rounds": result.data.get("rounds", []),
            "stats": result.data.get("stats", {})
        }

    async def _phase_r2_decision_nodes(self, inputs: Dict) -> Dict:
        from backend.skills.factor_reverse import FactorReverse

        factor_skill = FactorReverse()
        rounds = inputs.get("rounds", [])

        all_nodes = []
        for round_data in rounds:
            result = await factor_skill.execute({
                "whale_address": inputs.get("address", ""),
                "trade_history": round_data.get("transactions", []),
                "token_price_history": inputs.get("token_prices", {}),
                "phase": "decision_nodes"
            })
            if result.success:
                all_nodes.extend(result.data.get("decision_nodes", []))

        return {"decision_nodes": all_nodes}

    async def _phase_r3_factor_scoring(self, inputs: Dict) -> Dict:
        from backend.skills.factor_reverse import FactorReverse

        factor_skill = FactorReverse()
        result = await factor_skill.execute({
            "whale_address": inputs.get("r0", {}).get("address", ""),
            "trade_history": inputs.get("r0", {}).get("transactions", []),
            "token_price_history": inputs.get("r0", {}).get("token_prices", {}),
            "rounds": inputs.get("r1", {}).get("rounds", []),
            "decision_nodes": inputs.get("r2", {}).get("decision_nodes", []),
            "phase": "factor_scoring"
        })

        return result.data if result.success else {"factor_scores": {}}

    async def _phase_r4_pattern_recognition(self, inputs: Dict) -> Dict:
        factor_scores = inputs.get("r3", {}).get("factor_scores", {})

        # Load strategy patterns
        import json, os
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'strategy_patterns.json')
        with open(config_path, 'r') as f:
            patterns_config = json.load(f)

        matched = []
        for pattern in patterns_config.get("patterns", []):
            conditions = pattern.get("conditions", {})
            score = self._match_pattern(conditions, factor_scores, inputs)
            if score > 0.5:
                matched.append({
                    "pattern": pattern,
                    "confidence": score,
                    "evidence": "Factor score matching"
                })

        return {"matched_patterns": matched}

    async def _phase_r5_report(self, inputs: Dict) -> Dict:
        from backend.skills.report_generate import ReportGenerate

        report_skill = ReportGenerate()
        result = await report_skill.execute({
            "final_graph": {},
            "rounds": inputs.get("r1", {}).get("rounds", []),
            "factor_scores": inputs.get("r3", {}).get("factor_scores", {}),
            "matched_patterns": inputs.get("r4", {}).get("matched_patterns", []),
            "format": "reverse"
        })

        return result.data if result.success else {"report": {}}

    def _match_pattern(self, conditions: Dict, scores: Dict, inputs: Dict) -> float:
        """Score how well a pattern matches the observed factors."""
        matches = 0
        total = 0

        for key, threshold in conditions.items():
            total += 1
            if key.endswith("_min") or key.endswith("_max"):
                factor_key = key.rsplit("_", 1)[0]
                score_val = scores.get(factor_key, {}).get("score", 0)
                if key.endswith("_min") and score_val >= threshold:
                    matches += 1
                elif key.endswith("_max") and score_val <= threshold:
                    matches += 1
            else:
                matches += 0.5  # Partial match for other conditions

        return matches / total if total > 0 else 0

    def _build_result(self, analysis_id: str, results: Dict, start_time: float) -> Dict:
        total_time = time.time() - start_time
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "total_time_s": total_time,
            "rounds": results.get("r1", {}).get("rounds", []),
            "factor_scores": results.get("r3", {}).get("factor_scores", {}),
            "matched_patterns": results.get("r4", {}).get("matched_patterns", []),
            "report": results.get("r5", {}).get("report", {}),
            "phase_summary": self.phase_manager.get_summary()
        }

    def _error_result(self, analysis_id: str, phase: str, error: str) -> Dict:
        return {
            "analysis_id": analysis_id,
            "status": "failed",
            "failed_phase": phase,
            "error": error
        }
