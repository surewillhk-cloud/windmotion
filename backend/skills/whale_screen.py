"""S6: Whale Screen - Identifies and screens whale addresses from on-chain data."""
import json
import os
import time
from typing import Dict, List, Optional
from backend.skills.base import BaseSkill, SkillResult


class WhaleScreen(BaseSkill):
    """Screens and identifies whale addresses based on transaction patterns and holdings."""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.skill_id = "S6_WhaleScreen"
        self.whale_threshold_usd = self.config.get("whale_threshold_usd", 100000)
        self.min_transactions = self.config.get("min_transactions", 5)

    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        start_time = time.time()
        valid, err = self.validate_inputs(inputs)
        if not valid:
            return self._create_result(False, {}, err, start_time)

        addresses = inputs.get("addresses", [])
        transactions = inputs.get("transactions", [])
        filters = inputs.get("filters", {})

        min_value = filters.get("min_value_usd", self.whale_threshold_usd)
        chain_filter = filters.get("chain", None)
        token_filter = filters.get("token", None)

        # Aggregate address statistics
        address_stats: Dict[str, Dict] = {}
        for tx in transactions:
            from_addr = tx.get("from", "").lower()
            to_addr = tx.get("to", "").lower()
            value_usd = tx.get("value_usd", 0)
            token = tx.get("token", "")
            chain = tx.get("chain", "")

            if chain_filter and chain != chain_filter:
                continue
            if token_filter and token != token_filter:
                continue

            for addr in [from_addr, to_addr]:
                if not addr:
                    continue
                if addr not in address_stats:
                    address_stats[addr] = {
                        "address": addr,
                        "total_volume_usd": 0,
                        "transaction_count": 0,
                        "tokens": set(),
                        "chains": set(),
                        "inflow_usd": 0,
                        "outflow_usd": 0
                    }
                stats = address_stats[addr]
                stats["total_volume_usd"] += value_usd
                stats["transaction_count"] += 1
                stats["tokens"].add(token)
                stats["chains"].add(chain)

                if addr == from_addr:
                    stats["outflow_usd"] += value_usd
                if addr == to_addr:
                    stats["inflow_usd"] += value_usd

        # Filter whales
        whales = []
        for addr, stats in address_stats.items():
            if stats["total_volume_usd"] >= min_value and stats["transaction_count"] >= self.min_transactions:
                whale_data = {
                    "address": addr,
                    "total_volume_usd": stats["total_volume_usd"],
                    "transaction_count": stats["transaction_count"],
                    "tokens": list(stats["tokens"]),
                    "chains": list(stats["chains"]),
                    "inflow_usd": stats["inflow_usd"],
                    "outflow_usd": stats["outflow_usd"],
                    "net_flow_usd": stats["inflow_usd"] - stats["outflow_usd"],
                    "whale_type": self._classify_whale(stats)
                }
                whales.append(whale_data)

        whales.sort(key=lambda x: x["total_volume_usd"], reverse=True)

        return self._create_result(True, {
            "whales": whales,
            "total_whales_found": len(whales),
            "total_volume_analyzed": sum(s["total_volume_usd"] for s in address_stats.values()),
            "filters_applied": {
                "min_value_usd": min_value,
                "chain": chain_filter,
                "token": token_filter
            }
        }, start_time=start_time)

    def _classify_whale(self, stats: Dict) -> str:
        """Classify whale type based on behavior patterns."""
        if stats["inflow_usd"] > stats["outflow_usd"] * 2:
            return "accumulator"
        elif stats["outflow_usd"] > stats["inflow_usd"] * 2:
            return "distributor"
        elif stats["transaction_count"] > 50:
            return "active_trader"
        else:
            return "holder"

    def validate_inputs(self, inputs: Dict) -> tuple[bool, Optional[str]]:
        if "transactions" not in inputs:
            return False, "Missing 'transactions' in inputs"
        if not isinstance(inputs["transactions"], list):
            return False, "'transactions' must be a list"
        return True, None
