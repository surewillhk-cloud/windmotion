"""S11: Data Fetch - Fetches on-chain and market data from external sources."""
import json
import time
from typing import Dict, List, Optional
from backend.skills.base import BaseSkill, SkillResult


class DataFetch(BaseSkill):
    """Fetches on-chain data, market data, and social data from various sources."""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.skill_id = "S11_DataFetch"
        self.cache: Dict[str, Dict] = {}

    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        start_time = time.time()
        valid, err = self.validate_inputs(inputs)
        if not valid:
            return self._create_result(False, {}, err, start_time)

        data_type = inputs.get("data_type", "")
        params = inputs.get("params", {})
        use_cache = inputs.get("use_cache", True)

        cache_key = f"{data_type}:{json.dumps(params, sort_keys=True)}"
        if use_cache and cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached.get("cached_at", 0) < 300:
                return self._create_result(True, {
                    "data": cached["data"],
                    "data_type": data_type,
                    "source": "cache",
                    "cached_at": cached["cached_at"]
                }, start_time=start_time)

        http_client = context.get("http_client") if context else None
        result_data = {}

        if data_type == "transactions":
            result_data = await self._fetch_transactions(params, http_client)
        elif data_type == "token_info":
            result_data = await self._fetch_token_info(params, http_client)
        elif data_type == "price_history":
            result_data = await self._fetch_price_history(params, http_client)
        elif data_type == "holder_distribution":
            result_data = await self._fetch_holder_distribution(params, http_client)
        elif data_type == "market_data":
            result_data = await self._fetch_market_data(params, http_client)
        elif data_type == "social_mentions":
            result_data = await self._fetch_social_mentions(params, http_client)
        else:
            return self._create_result(False, {}, f"Unknown data_type: {data_type}", start_time)

        if use_cache:
            self.cache[cache_key] = {"data": result_data, "cached_at": time.time()}

        return self._create_result(True, {
            "data": result_data,
            "data_type": data_type,
            "source": "live",
            "params": params
        }, start_time=start_time)

    async def _fetch_transactions(self, params: Dict, http_client) -> Dict:
        address = params.get("address", "")
        chain = params.get("chain", "ethereum")
        limit = params.get("limit", 100)

        if http_client:
            try:
                if chain == "ethereum":
                    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=desc&page=1&offset={limit}"
                elif chain == "bsc":
                    url = f"https://api.bscscan.com/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=desc&page=1&offset={limit}"
                else:
                    return {"transactions": [], "error": f"Unsupported chain: {chain}"}

                response = await http_client.get(url)
                if response.status == 200:
                    data = await response.json()
                    return {"transactions": data.get("result", []), "chain": chain}
            except Exception as e:
                return {"transactions": [], "error": str(e)}

        return {"transactions": [], "chain": chain, "note": "No HTTP client available"}

    async def _fetch_token_info(self, params: Dict, http_client) -> Dict:
        token = params.get("token", "")
        chain = params.get("chain", "ethereum")
        return {
            "token": token,
            "chain": chain,
            "info": {},
            "note": "Token info fetch requires API configuration"
        }

    async def _fetch_price_history(self, params: Dict, http_client) -> Dict:
        token = params.get("token", "")
        days = params.get("days", 30)
        return {
            "token": token,
            "days": days,
            "prices": [],
            "note": "Price history fetch requires API configuration"
        }

    async def _fetch_holder_distribution(self, params: Dict, http_client) -> Dict:
        token = params.get("token", "")
        chain = params.get("chain", "ethereum")
        return {
            "token": token,
            "chain": chain,
            "holders": [],
            "note": "Holder distribution fetch requires API configuration"
        }

    async def _fetch_market_data(self, params: Dict, http_client) -> Dict:
        return {
            "btc_price": 0,
            "eth_price": 0,
            "total_market_cap": 0,
            "fear_greed_index": 50,
            "btc_dominance": 50,
            "note": "Market data fetch requires API configuration"
        }

    async def _fetch_social_mentions(self, params: Dict, http_client) -> Dict:
        token = params.get("token", "")
        return {
            "token": token,
            "mentions": [],
            "sentiment": "neutral",
            "note": "Social mention fetch requires API configuration"
        }

    def validate_inputs(self, inputs: Dict) -> tuple[bool, Optional[str]]:
        if "data_type" not in inputs:
            return False, "Missing 'data_type' in inputs"
        valid_types = ["transactions", "token_info", "price_history", "holder_distribution", "market_data", "social_mentions"]
        if inputs["data_type"] not in valid_types:
            return False, f"data_type must be one of: {', '.join(valid_types)}"
        return True, None
