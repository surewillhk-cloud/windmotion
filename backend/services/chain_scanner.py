"""Chain Scanner - Etherscan API V2 integration for multi-chain on-chain data.

Etherscan API V2: https://docs.etherscan.io/v2-migration
Unified endpoint: https://api.etherscan.io/v2/api?chainid=<id>
A single API key works across 60+ EVM chains.
Free tier: 5 calls/sec, requires API key.
"""
import logging
import os
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# Etherscan V2 unified endpoint
ETHERSCAN_V2_BASE = "https://api.etherscan.io/v2/api"

# Chain IDs for supported chains
CHAIN_IDS = {
    "eth": 1,
    "ethereum": 1,
    "bsc": 56,
    "bnb": 56,
    "polygon": 137,
    "matic": 137,
    "arbitrum": 42161,
    "optimism": 10,
    "avalanche": 43114,
    "fantom": 250,
    "base": 8453,
    "linea": 59144,
    "zksync": 324,
    "scroll": 534352,
}

# Primary API key: prefer ETHERSCAN_API_KEY, fall back to BSCSCAN_API_KEY for backward compat
API_KEY = os.getenv("ETHERSCAN_API_KEY") or os.getenv("BSCSCAN_API_KEY", "")


class ChainScanner:
    """Scans EVM blockchains via Etherscan API V2 for transactions, transfers, and balances.

    Supports 60+ chains with a single API key.
    Default chain is BSC (chainid=56).
    """

    def __init__(self, api_key: Optional[str] = None, chain: str = "bsc"):
        self.api_key = api_key or API_KEY
        self.chain = chain
        self.chain_id = CHAIN_IDS.get(chain.lower(), 56)  # default to BSC
        self.client = httpx.AsyncClient(timeout=30)
        if not self.api_key:
            logger.warning("ETHERSCAN_API_KEY is empty – all API calls will return empty results")

    async def _get(self, params: dict) -> list:
        """Execute an Etherscan API V2 request. Returns result list or empty list on error.

        Automatically injects chainid and apikey parameters.
        """
        if not self.api_key:
            logger.warning("Etherscan API key not set, returning empty result")
            return []

        params["apikey"] = self.api_key
        params["chainid"] = self.chain_id
        try:
            resp = await self.client.get(ETHERSCAN_V2_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status", "0")
            message = data.get("message", "")

            if status == "1":
                return data.get("result", [])

            # "No transactions found" is a valid empty result, not an error
            if message == "No transactions found":
                return []

            logger.warning(f"Etherscan API warning: {message} | result: {data.get('result', '')}")
            return data.get("result", []) if isinstance(data.get("result"), list) else []

        except httpx.TimeoutException:
            logger.error("Etherscan API timeout")
            return []
        except httpx.HTTPStatusError as e:
            logger.error(f"Etherscan API HTTP error: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Etherscan API unexpected error: {e}")
            return []

    async def get_address_transactions(
        self, address: str, page: int = 1, offset: int = 100, sort: str = "desc"
    ) -> List[Dict]:
        """Get external transactions for an address."""
        return await self._get({
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "sort": sort,
            "page": page,
            "offset": offset,
        })

    async def get_token_transfers(
        self, address: str, page: int = 1, offset: int = 100
    ) -> List[Dict]:
        """Get ERC20/BEP20 token transfers for an address."""
        return await self._get({
            "module": "account",
            "action": "tokentx",
            "address": address,
            "sort": "desc",
            "page": page,
            "offset": offset,
        })

    async def get_internal_transactions(self, tx_hash: str) -> List[Dict]:
        """Get internal transactions for a transaction hash."""
        return await self._get({
            "module": "account",
            "action": "txlistinternal",
            "txhash": tx_hash,
        })

    async def get_address_balance(self, address: str) -> float:
        """Get BNB balance for an address (in BNB, not wei)."""
        result = await self._get({
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
        })
        if result and isinstance(result, str):
            try:
                return int(result) / 1e18
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    async def get_token_balance(self, address: str, token_address: str) -> float:
        """Get ERC20 token balance for an address."""
        result = await self._get({
            "module": "account",
            "action": "tokenbalance",
            "address": address,
            "contractaddress": token_address,
            "tag": "latest",
        })
        if result and isinstance(result, str):
            try:
                return int(result) / 1e18  # assumes 18 decimals
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    async def scan_large_transactions(
        self, min_value_bnb: float = 100, chain: Optional[str] = None
    ) -> List[Dict]:
        """Scan for large transactions via known DEX router contracts.

        Queries recent transactions to PancakeSwap Router and filters by value.
        For production use, The Graph or a custom indexer is recommended.
        Optionally override chain to scan a different EVM chain.
        """
        if not self.api_key:
            logger.warning("Cannot scan large transactions: API key not set")
            return []

        # Allow scanning a different chain without creating a new instance
        scan_chain_id = CHAIN_IDS.get(chain.lower(), self.chain_id) if chain else self.chain_id

        # PancakeSwap V2 Router
        dex_routers = [
            "0x10ED43C718714eb63d5aA57B78B54704E256024E",  # PancakeSwap V2
            "0x13f4EA83D0bd40E75C8222255bc855a974568Dd4",  # PancakeSwap V3
        ]

        all_large_txs = []
        min_value_wei = int(min_value_bnb * 1e18)

        for router in dex_routers:
            txs = await self._get({
                "module": "account",
                "action": "txlist",
                "address": router,
                "startblock": 0,
                "endblock": 99999999,
                "sort": "desc",
                "page": 1,
                "offset": 50,
            })
            for tx in txs:
                value_wei = int(tx.get("value", "0"))
                if value_wei >= min_value_wei:
                    all_large_txs.append({
                        "hash": tx.get("hash"),
                        "from": tx.get("from"),
                        "to": tx.get("to"),
                        "value_bnb": value_wei / 1e18,
                        "timestamp": int(tx.get("timeStamp", 0)),
                        "block": int(tx.get("blockNumber", 0)),
                        "method": tx.get("functionName", ""),
                        "gas_used": int(tx.get("gasUsed", 0)),
                    })

        all_large_txs.sort(key=lambda x: x["value_bnb"], reverse=True)
        return all_large_txs

    async def get_token_info(self, token_address: str) -> Optional[Dict]:
        """Get basic token info via Etherscan V2 token supply endpoint.

        Returns supply info; for full metadata (name, symbol, decimals),
        combine with on-chain contract calls.
        """
        supply_result = await self._get({
            "module": "stats",
            "action": "tokensupply",
            "contractaddress": token_address,
        })

        info: Dict = {"address": token_address}
        if supply_result and isinstance(supply_result, str):
            try:
                info["total_supply"] = int(supply_result)
            except (ValueError, TypeError):
                info["total_supply"] = None

        return info

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
