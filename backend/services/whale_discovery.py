"""Whale Discovery - Finds and evaluates whale addresses."""
import logging
from typing import Dict, List, Optional
from backend.models.whale import Whale

logger = logging.getLogger(__name__)


class WhaleDiscoveryService:
    """Discovers and evaluates whale addresses based on filter criteria."""

    def __init__(self, db=None, redis=None):
        self.db = db
        self.redis = redis

    async def discover(self, filter_config: Dict) -> List[Whale]:
        """Run whale discovery with given filter configuration."""
        # In production: query BSCScan/The Graph for large transactions
        # Filter by criteria, calculate scores
        logger.info("Running whale discovery...")
        return []

    async def get_whale_details(self, address: str) -> Optional[Whale]:
        """Get detailed whale information."""
        # Check cache first
        if self.redis:
            cached = await self.redis.get_cached_whale(address)
            if cached:
                return Whale.from_dict(cached)

        # Fetch from DB
        if self.db:
            row = await self.db.fetchrow(
                "SELECT * FROM whales WHERE address = $1", address
            )
            if row:
                whale = Whale.from_dict(row)
                if self.redis:
                    await self.redis.cache_whale_data(address, whale.to_dict())
                return whale

        return None

    async def update_whale_score(self, address: str, analysis_result: Dict):
        """Update whale score based on analysis result."""
        score = self._calculate_score(analysis_result)
        if self.db:
            await self.db.execute(
                "UPDATE whales SET score = $1, updated_at = NOW() WHERE address = $2",
                score, address
            )

    def _calculate_score(self, result: Dict) -> float:
        """Calculate composite whale score (0-100)."""
        factors = result.get("factor_scores", {})
        if not factors:
            return 0

        weights = {"F1": 0.25, "F2": 0.25, "F3": 0.20, "F4": 0.15, "F5": 0.15}
        total = 0
        for fid, weight in weights.items():
            score = factors.get(fid, {}).get("score", 0)
            total += score * weight * 20  # Scale 0-5 to 0-100

        return min(100, max(0, total))
