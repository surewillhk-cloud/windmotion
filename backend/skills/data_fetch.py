"""S11: Data Fetch - Fetches on-chain and market data from external sources.

Integrates with:
  - ChainScanner (BscScan API) for on-chain data
  - PriceOracle (DeFiLlama) for token prices
"""
import json
import logging
import time
from typing import Dict, List, Optional

from backend.skills.base import BaseSkill, SkillResult

logger = logging.getLogger(__name__)


class DataFetch(BaseSkill):
    """Fetches on-chain data, market data, and social data from various sources."""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.skill_id = "S11_DataFetch"
        self.cache: Dict[str, Dict] = {}
        self._chain_scanner = None
        self._price_oracle = None

    def _get_chain_scanner(self, context: Optional[Dict] = None):
        """Lazy-init ChainScanner from context or create new."""
        if self._chain_scanner is None:
            from backend.services.chain_scanner import ChainScanner
            self._chain_scanner = ChainScanner()
        return self._chain_scanner

    def _get_price_oracle(self):
        """Lazy-init PriceOracle."""
        if self._price_oracle is None:
            from backend.skills.price_oracle import PriceOracle
            self._price_oracle = PriceOracle()
        return self._price_oracle

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

        result_data = {}

        if data_type == "transactions":
            result_data = await self._fetch_transactions(params)
        elif data_type == "token_transfers":
            result_data = await self._fetch_token_transfers(params)
        elif data_type == "token_info":
            result_data = await self._fetch_token_info(params)
        elif data_type == "price":
            result_data = await self._fetch_price(params)
        elif data_type == "price_history":
            result_data = await self._fetch_price_history(params)
        elif data_type == "holder_distribution":
            result_data = await self._fetch_holder_distribution(params)
        elif data_type == "market_data":
            result_data = await self._fetch_market_data(params)
        elif data_type == "social_mentions":
            result_data = await self._fetch_social_mentions(params)
        elif data_type == "balance":
            result_data = await self._fetch_balance(params)
        elif data_type == "internal_transactions":
            result_data = await self._fetch_internal_transactions(params)
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

    async def _fetch_transactions(self, params: Dict) -> Dict:
        """Fetch address transactions via ChainScanner."""
        address = params.get("address", "")
        chain = params.get("chain", "bsc")
        limit = params.get("limit", 100)

        if not address:
            return {"transactions": [], "error": "No address provided"}

        scanner = self._get_chain_scanner()
        if chain == "bsc":
            txs = await scanner.get_address_transactions(address, offset=limit)
            return {"transactions": txs, "chain": chain, "count": len(txs)}
        else:
            return {"transactions": [], "chain": chain, "note": f"Chain {chain} not supported yet"}

    async def _fetch_token_transfers(self, params: Dict) -> Dict:
        """Fetch ERC20 token transfers via ChainScanner."""
        address = params.get("address", "")
        chain = params.get("chain", "bsc")
        limit = params.get("limit", 100)

        if not address:
            return {"transfers": [], "error": "No address provided"}

        scanner = self._get_chain_scanner()
        if chain == "bsc":
            transfers = await scanner.get_token_transfers(address, offset=limit)
            return {"transfers": transfers, "chain": chain, "count": len(transfers)}
        return {"transfers": [], "chain": chain}

    async def _fetch_internal_transactions(self, params: Dict) -> Dict:
        """Fetch internal transactions for a tx hash."""
        tx_hash = params.get("tx_hash", "")
        if not tx_hash:
            return {"internal_txns": [], "error": "No tx_hash provided"}

        scanner = self._get_chain_scanner()
        txns = await scanner.get_internal_transactions(tx_hash)
        return {"internal_txns": txns}

    async def _fetch_balance(self, params: Dict) -> Dict:
        """Fetch address balance."""
        address = params.get("address", "")
        if not address:
            return {"balance": 0.0, "error": "No address provided"}

        scanner = self._get_chain_scanner()
        balance = await scanner.get_address_balance(address)
        return {"address": address, "balance_bnb": balance}

    async def _fetch_token_info(self, params: Dict) -> Dict:
        """Fetch token info via ChainScanner + PriceOracle."""
        token = params.get("token", "")
        chain = params.get("chain", "bsc")

        scanner = self._get_chain_scanner()
        oracle = self._get_price_oracle()

        info = await scanner.get_token_info(token) or {"address": token}
        price = await oracle.get_current_price(token, chain)

        return {
            "token": token,
            "chain": chain,
            "info": info,
            "price": price,
        }

    async def _fetch_price(self, params: Dict) -> Dict:
        """Fetch current token price from DeFiLlama."""
        token = params.get("token", params.get("token_address", ""))
        chain = params.get("chain", "bsc")

        if not token:
            return {"price": 0.0, "error": "No token provided"}

        oracle = self._get_price_oracle()
        price = await oracle.get_current_price(token, chain)

        if price:
            return {"price": price["price"], "symbol": price.get("symbol", ""), "chain": chain, "token": token}
        return {"price": 0.0, "chain": chain, "token": token, "note": "Price not found on DeFiLlama"}

    async def _fetch_price_history(self, params: Dict) -> Dict:
        """Fetch price history from DeFiLlama."""
        token = params.get("token", params.get("token_address", ""))
        chain = params.get("chain", "bsc")
        days = params.get("days", 30)
        timestamps = params.get("timestamps", [])

        if not token:
            return {"prices": [], "error": "No token provided"}

        oracle = self._get_price_oracle()

        # If specific timestamps requested, use historical endpoint
        if timestamps:
            history = []
            for ts in timestamps:
                price = await oracle.get_historical_price(token, ts, chain)
                if price:
                    history.append({"timestamp": ts, "price": price["price"]})
            return {"prices": history, "chain": chain, "token": token, "source": "defillama_historical"}

        # Otherwise use chart endpoint
        import time as _time
        end_ts = int(_time.time())
        start_ts = end_ts - days * 86400
        prices = await oracle.get_price_history(token, start_ts, end_ts, chain)
        return {"prices": prices, "chain": chain, "token": token, "source": "defillama_chart", "days": days}

    async def _fetch_holder_distribution(self, params: Dict) -> Dict:
        """Fetch holder distribution - requires indexer, returns placeholder."""
        token = params.get("token", "")
        chain = params.get("chain", "bsc")
        return {
            "token": token,
            "chain": chain,
            "holders": [],
            "note": "Holder distribution requires The Graph or custom indexer"
        }

    async def _fetch_market_data(self, params: Dict) -> Dict:
        """Fetch broad market data from DeFiLlama."""
        oracle = self._get_price_oracle()

        # Fetch major token prices as market indicators
        major_tokens = [
            {"address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c", "chain": "bsc"},  # WBNB
        ]
        prices = await oracle.batch_prices(major_tokens, chain="bsc")

        return {
            "bnb_price": prices.get("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c", 0),
            "source": "defillama",
            "note": "Full market data (fear/greed, dominance) requires additional APIs"
        }

    async def _fetch_social_mentions(self, params: Dict) -> Dict:
        """Fetch social mentions - requires social API, returns placeholder."""
        token = params.get("token", "")
        return {
            "token": token,
            "mentions": [],
            "sentiment": "neutral",
            "note": "Social mention data requires Twitter/Telegram API integration"
        }

    def validate_inputs(self, inputs: Dict) -> tuple[bool, Optional[str]]:
        if "data_type" not in inputs:
            return False, "Missing 'data_type' in inputs"
        valid_types = [
            "transactions", "token_transfers", "token_info", "price",
            "price_history", "holder_distribution", "market_data",
            "social_mentions", "balance", "internal_transactions",
        ]
        if inputs["data_type"] not in valid_types:
            return False, f"data_type must be one of: {', '.join(valid_types)}"
        return True, None

    async def close(self):
        if self._chain_scanner:
            await self._chain_scanner.close()
        if self._price_oracle:
            await self._price_oracle.close()
