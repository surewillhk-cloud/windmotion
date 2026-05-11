"""Export Service - Exports analysis data in various formats."""
import json
import csv
import io
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ExportService:
    """Exports analysis data in CSV, JSON, and PDF formats."""

    def export_whales_csv(self, whales: List[Dict]) -> str:
        """Export whale list as CSV."""
        output = io.StringIO()
        if not whales:
            return ""

        fieldnames = ["address", "total_profit_usd", "win_rate", "roi",
                      "trade_count", "token_count", "score", "last_active"]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for whale in whales:
            writer.writerow(whale)

        return output.getvalue()

    def export_analysis_json(self, analysis: Dict) -> str:
        """Export analysis result as JSON."""
        return json.dumps(analysis, ensure_ascii=False, indent=2, default=str)

    def export_rounds_csv(self, rounds: List[Dict]) -> str:
        """Export trading rounds as CSV."""
        output = io.StringIO()
        if not rounds:
            return ""

        fieldnames = ["id", "token_symbol", "total_invested_usd", "total_returned_usd",
                      "net_profit_usd", "roi", "max_drawdown_pct", "hold_days", "status"]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for round_data in rounds:
            writer.writerow(round_data)

        return output.getvalue()

    def export_factor_report(self, factor_scores: Dict) -> str:
        """Export factor analysis as formatted text."""
        lines = ["=" * 50, "因子分析报告", "=" * 50, ""]

        for fid in sorted(factor_scores.keys()):
            score = factor_scores[fid]
            stars = "★" * int(score.get("score", 0)) + "☆" * (5 - int(score.get("score", 0)))
            lines.append(f"{fid}: {score.get('name', '')} - {score.get('score', 0)}/5 {stars}")
            if score.get("summary"):
                lines.append(f"  {score['summary']}")
            lines.append("")

        return "\n".join(lines)
