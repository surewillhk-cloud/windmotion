"""Smart Recommend - Generates intelligent filter and strategy recommendations."""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class SmartRecommendService:
    """Generates smart recommendations based on historical analysis data."""

    def __init__(self, db=None):
        self.db = db

    async def get_recommendations(self) -> List[Dict]:
        """Generate smart recommendations."""
        recommendations = []

        # Analyze historical data patterns
        if self.db:
            # Find top performing filter criteria
            top_whales = await self.db.fetch(
                "SELECT * FROM whales ORDER BY score DESC LIMIT 50"
            )

            if top_whales:
                # Recommend adjusting filter thresholds
                avg_win_rate = sum(w.get("win_rate", 0) for w in top_whales) / len(top_whales)
                if avg_win_rate > 65:
                    recommendations.append({
                        "type": "filter_adjust",
                        "title": "提高胜率门槛",
                        "description": f"Top鲸鱼平均胜率{avg_win_rate:.0f}%，建议将最低胜率从60%提高到{int(avg_win_rate - 5)}%",
                        "impact": "减少低质量结果，提高分析效率",
                        "action": {"min_win_rate": int(avg_win_rate - 5)}
                    })

                # Find common strategy patterns
                patterns = {}
                for w in top_whales:
                    for p in w.get("strategy_patterns", []):
                        patterns[p] = patterns.get(p, 0) + 1

                if patterns:
                    top_pattern = max(patterns, key=patterns.get)
                    recommendations.append({
                        "type": "pattern_insight",
                        "title": f"热门策略模式: {top_pattern}",
                        "description": f"在Top鲸鱼中，{top_pattern}模式出现{patterns[top_pattern]}次",
                        "impact": "关注此模式的鲸鱼可能获得更好的分析结果",
                        "action": {"focus_pattern": top_pattern}
                    })

        return recommendations

    async def get_token_recommendations(self) -> List[Dict]:
        """Recommend tokens to watch based on whale activity."""
        return []
