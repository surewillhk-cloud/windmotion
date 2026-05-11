"""S12: Price Oracle - Fetches token prices from multiple sources."""
import time
from typing import Dict, List, Optional
from backend.skills.base import BaseSkill, SkillResult


class PriceOracle(BaseSkill):
    """Fetches token prices from DeFiLlama and DEX pool reserves."""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.skill_id = "S12_PriceOracle"
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl = 300  # 5 minutes

    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        start = time.time()
        valid, err = self.validate_inputs(inputs)
        if not valid:
            return self._create_result(False, {}, err, start)

        token_address = inputs["token_address"]
        chain = inputs.get("chain", "bsc")
        timestamps = inputs.get("timestamps", [])

        # Check cache
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
            return self._create_result(False, {}, str(e), start)

    def validate_inputs(self, inputs: Dict) -> tuple:
        if "token_address" not in inputs:
            return False, "Missing token_address"
        return True, None

    async def _fetch_price(self, address: str, chain: str, timestamps: List[int]) -> Dict:
        """Fetch current and historical prices."""
        # Current price from DeFiLlama
        current_price = await self._defillama_price(address, chain)

        # Historical prices
        history = {}
        for ts in timestamps:
            hist_price = await self._defillama_historical(address, chain, ts)
            history[ts] = hist_price

        return {
            "current_price": current_price,
            "historical_prices": history,
            "source": "defillama",
            "chain": chain,
            "address": address
        }

    async def _defillama_price(self, address: str, chain: str) -> float:
        """Fetch current price from DeFiLlama."""
        # In production, this calls: https://coins.llama.fi/prices/current/{chain}:{address}
        return 0.0  # Placeholder for actual API call

    async def _defillama_historical(self, address: str, chain: str, timestamp: int) -> float:
        """Fetch historical price from DeFiLlama."""
        # In production, this calls: https://coins.llama.fi/prices/historical/{timestamp}/{chain}:{address}
        return 0.0

    async def get_token_price_at(self, token_address: str, chain: str, timestamp: int) -> float:
        """Convenience: get price at specific timestamp."""
        result = await self.execute({
            "token_address": token_address,
            "chain": chain,
            "timestamps": [timestamp]
        })
        if result.success:
            return result.data.get("historical_prices", {}).get(timestamp, 0.0)
        return 0.0

    async def batch_prices(self, tokens: List[Dict]) -> Dict[str, float]:
        """Batch fetch prices for multiple tokens."""
        results = {}
        for token in tokens:
            addr = token.get("address", "")
            chain = token.get("chain", "bsc")
            price_data = await self._fetch_price(addr, chain, [])
            results[addr] = price_data.get("current_price", 0.0)
        return results
