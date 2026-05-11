"""S12: Price Oracle - Fetches token prices from DeFiLlama.

DeFiLlama API: https://defillama.com/docs/api
Free, no API key required.

Endpoints:
  Current:  https://coins.llama.fi/prices/current/{coins}
  History:  https://coins.llama.fi/prices/historical/{timestamp}/{coins}
  Chart:    https://coins.llama.fi/chart/{coins}?start=xxx&end=xxx&span=24

coins format: {chain}:{address}  e.g. bsc:0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82
"""
import logging
import time
from typing import Dict, List, Optional

import httpx

from backend.skills.base import BaseSkill, SkillResult

logger = logging.getLogger(__name__)

DEFILLAMA_BASE = "https://coins.llama.fi"


class PriceOracle(BaseSkill):
    """Fetches token prices from DeFiLlama. No API key required."""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.skill_id = "S12_PriceOracle"
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl = 300  # 5 minutes
        self.client = httpx.AsyncClient(timeout=15)

    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        start = time.time()
        valid, err = self.validate_inputs(inputs)
        if not valid:
            return self._create_result(False, {}, err, start)

        token_address = inputs["token_address"]
        chain = inputs.get("chain", "bsc")
        timestamps = inputs.get("timestamps", [])

        cache_key = f"{chain}:{token_address}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached.get("ts", 0) < self.cache_ttl:
                return self._create_result(True, cached["data"], start_time=start)

        try:
            price_data = await self._fetch_price(token_address, chain, timestamps)
            self.cache[cache_key] = {"data": price_data, "ts": time.time()}
            return self._create_result(True, price_data, start_time=start)
        except Exception as e:
            logger.error(f"PriceOracle error: {e}")
            return self._create_result(False, {}, str(e), start)

    def validate_inputs(self, inputs: Dict) -> tuple:
        if "token_address" not in inputs:
            return False, "Missing token_address"
        return True, None

    async def _fetch_price(self, address: str, chain: str, timestamps: List[int]) -> Dict:
        """Fetch current and historical prices from DeFiLlama."""
        current = await self.get_current_price(address, chain)

        history = {}
        for ts in timestamps:
            hist = await self.get_historical_price(address, ts, chain)
            if hist:
                history[ts] = hist

        return {
            "current_price": current.get("price", 0.0) if current else 0.0,
            "symbol": current.get("symbol", "") if current else "",
            "historical_prices": history,
            "source": "defillama",
            "chain": chain,
            "address": address,
        }

    async def get_current_price(self, token_address: str, chain: str = "bsc") -> Optional[Dict]:
        """Get current price from DeFiLlama.

        Returns: {"price": float, "symbol": str, "timestamp": int} or None
        """
        coin_id = f"{chain}:{token_address}"
        try:
            resp = await self.client.get(f"{DEFILLAMA_BASE}/prices/current/{coin_id}")
            resp.raise_for_status()
            data = resp.json()
            coins = data.get("coins", {})
            if coin_id in coins:
                entry = coins[coin_id]
                return {
                    "price": entry.get("price", 0.0),
                    "symbol": entry.get("symbol", ""),
                    "timestamp": entry.get("timestamp", 0),
                    "confidence": entry.get("confidence", 0.0),
                }
            return None
        except Exception as e:
            logger.error(f"DeFiLlama current price error for {coin_id}: {e}")
            return None

    async def get_historical_price(
        self, token_address: str, timestamp: int, chain: str = "bsc"
    ) -> Optional[Dict]:
        """Get historical price at a specific Unix timestamp.

        Returns: {"price": float, "symbol": str} or None
        """
        coin_id = f"{chain}:{token_address}"
        try:
            resp = await self.client.get(
                f"{DEFILLAMA_BASE}/prices/historical/{timestamp}/{coin_id}"
            )
            resp.raise_for_status()
            data = resp.json()
            coins = data.get("coins", {})
            if coin_id in coins:
                entry = coins[coin_id]
                return {
                    "price": entry.get("price", 0.0),
                    "symbol": entry.get("symbol", ""),
                }
            return None
        except Exception as e:
            logger.error(f"DeFiLlama historical price error for {coin_id}@{timestamp}: {e}")
            return None

    async def get_price_history(
        self, token_address: str, start_ts: int, end_ts: int, chain: str = "bsc"
    ) -> List[Dict]:
        """Get price history over a time range using the chart endpoint.

        Returns list of {"timestamp": int, "price": float}.
        """
        coin_id = f"{chain}:{token_address}"
        span = max(1, (end_ts - start_ts) // 3600)  # ~1 point per hour
        try:
            resp = await self.client.get(
                f"{DEFILLAMA_BASE}/chart/{coin_id}",
                params={"start": start_ts, "end": end_ts, "span": min(span, 500)},
            )
            resp.raise_for_status()
            data = resp.json()
            coins = data.get("coins", {})
            if coin_id in coins:
                return [
                    {"timestamp": p.get("timestamp", 0), "price": p.get("price", 0.0)}
                    for p in coins[coin_id].get("prices", [])
                ]
            return []
        except Exception as e:
            logger.error(f"DeFiLlama chart error for {coin_id}: {e}")
            return []

    async def batch_prices(
        self, tokens: List[Dict], chain: str = "bsc"
    ) -> Dict[str, float]:
        """Batch fetch current prices for multiple tokens.

        DeFiLlama supports comma-separated coin IDs.
        """
        if not tokens:
            return {}

        coin_ids = ",".join(f"{t.get('chain', chain)}:{t['address']}" for t in tokens)
        try:
            resp = await self.client.get(f"{DEFILLAMA_BASE}/prices/current/{coin_ids}")
            resp.raise_for_status()
            data = resp.json()
            coins = data.get("coins", {})
            return {
                t["address"]: coins.get(f"{t.get('chain', chain)}:{t['address']}", {}).get("price", 0.0)
                for t in tokens
            }
        except Exception as e:
            logger.error(f"DeFiLlama batch price error: {e}")
            return {t["address"]: 0.0 for t in tokens}

    async def get_token_price_at(
        self, token_address: str, chain: str, timestamp: int
    ) -> float:
        """Convenience: get price at specific timestamp."""
        result = await self.execute({
            "token_address": token_address,
            "chain": chain,
            "timestamps": [timestamp],
        })
        if result.success:
            return result.data.get("historical_prices", {}).get(timestamp, {}).get("price", 0.0)
        return 0.0

    async def close(self):
        await self.client.aclose()
