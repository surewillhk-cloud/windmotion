"""S7: Factor Reverse - Reverse-engineers whale trading factors and strategies."""
import json
import os
import time
from typing import Dict, List, Optional
from backend.skills.base import BaseSkill, SkillResult


class FactorReverse(BaseSkill):
    """Reverse-engineers the decision factors and strategies of whale addresses.

    Analyzes:
    - Entry timing (F1)
    - Exit timing (F2)
    - Position management (F3)
    - Token selection (F4)
    - Behavior patterns (F5)
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.skill_id = "S7_FactorReverse"
        self.reverse_config = self._load_config()

    def _load_config(self) -> Dict:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'reverse_config.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    async def execute(self, inputs: Dict, context: Optional[Dict] = None) -> SkillResult:
        start_time = time.time()
        valid, err = self.validate_inputs(inputs)
        if not valid:
            return self._create_result(False, {}, err, start_time)

        address = inputs.get("address", "")
        transactions = inputs.get("transactions", [])
        price_data = inputs.get("price_data", {})
        mode = inputs.get("mode", "standard")

        phases = self.reverse_config.get("analysis_modes", {}).get(mode, {}).get("phases", ["R0", "R1", "R2", "R3"])
        factor_weights = self.reverse_config.get("factor_weights", {})

        # R0: Transaction classification
        classified_txs = self._classify_transactions(transactions)

        # R1: Decision node extraction
        decision_nodes = self._extract_decision_nodes(classified_txs, price_data)

        factors = {}

        # R2: Factor analysis based on phases
        if "R2" in phases:
            factors["F1_entry_timing"] = self._analyze_entry_timing(decision_nodes, price_data, factor_weights.get("F1_entry_timing", {}))
            factors["F2_exit_timing"] = self._analyze_exit_timing(decision_nodes, price_data, factor_weights.get("F2_exit_timing", {}))
            factors["F3_position_management"] = self._analyze_position_management(decision_nodes, factor_weights.get("F3_position_management", {}))

        # R3: Token selection and behavior
        if "R3" in phases:
            factors["F4_token_selection"] = self._analyze_token_selection(transactions, factor_weights.get("F4_token_selection", {}))
            factors["F5_behavior_pattern"] = self._analyze_behavior_pattern(transactions, factor_weights.get("F5_behavior_pattern", {}))

        # R4: Strategy pattern matching
        matched_strategies = []
        if "R4" in phases:
            matched_strategies = self._match_strategies(factors)

        # R5: ROI calculation
        roi_data = {}
        if "R5" in phases:
            roi_data = self._calculate_roi(decision_nodes, price_data)

        return self._create_result(True, {
            "address": address,
            "mode": mode,
            "phases_completed": phases,
            "classified_transactions": classified_txs,
            "decision_nodes": decision_nodes,
            "factors": factors,
            "matched_strategies": matched_strategies,
            "roi_data": roi_data
        }, start_time=start_time)

    def _classify_transactions(self, transactions: List[Dict]) -> Dict:
        """Classify transactions into categories."""
        classified = {
            "buys": [], "sells": [], "transfers": [],
            "lp_adds": [], "lp_removes": [], "bridges": [],
            "borrows": [], "repays": []
        }
        for tx in transactions:
            tx_type = tx.get("type", "transfer")
            if tx_type in ("buy", "swap_in"):
                classified["buys"].append(tx)
            elif tx_type in ("sell", "swap_out"):
                classified["sells"].append(tx)
            elif tx_type == "lp_add":
                classified["lp_adds"].append(tx)
            elif tx_type == "lp_remove":
                classified["lp_removes"].append(tx)
            elif tx_type == "bridge":
                classified["bridges"].append(tx)
            elif tx_type == "borrow":
                classified["borrows"].append(tx)
            elif tx_type == "repay":
                classified["repays"].append(tx)
            else:
                classified["transfers"].append(tx)
        return {k: len(v) for k, v in classified.items()}

    def _extract_decision_nodes(self, classified_txs: Dict, price_data: Dict) -> List[Dict]:
        """Extract key decision nodes from transaction history."""
        nodes = []
        decision_types = self.reverse_config.get("decision_node_types", [])

        if classified_txs.get("buys", 0) > 0:
            nodes.append({"type": "INITIAL_BUY", "count": classified_txs["buys"]})
        if classified_txs.get("buys", 0) > 1:
            nodes.append({"type": "ADD_POSITION", "count": classified_txs["buys"] - 1})
        if classified_txs.get("sells", 0) > 0:
            nodes.append({"type": "EXIT", "count": classified_txs["sells"]})
        if classified_txs.get("borrows", 0) > 0:
            nodes.append({"type": "LEVERAGE", "count": classified_txs["borrows"]})
        if classified_txs.get("bridges", 0) > 0:
            nodes.append({"type": "BRIDGE", "count": classified_txs["bridges"]})
        if classified_txs.get("lp_adds", 0) > 0:
            nodes.append({"type": "LP_JOIN", "count": classified_txs["lp_adds"]})
        if classified_txs.get("lp_removes", 0) > 0:
            nodes.append({"type": "LP_EXIT", "count": classified_txs["lp_removes"]})

        # HOLD node detection (implicit decisions) per design doc §11.2
        hold_nodes = self._detect_hold_nodes(classified_txs, price_data)
        nodes.extend(hold_nodes)

        return nodes

    def _detect_hold_nodes(self, classified_txs: Dict, price_data: Dict) -> List[Dict]:
        """
        Detect implicit HOLD decisions per design doc:
        - 浮盈 > 100% 时未卖 (unrealized profit > 100% and didn't sell)
        - 浮亏 > 30% 时未割 (unrealized loss > 30% and didn't cut)
        - 价格创新高时未卖 (price hit new ATH and didn't sell)
        - 回调 > 20% 时未割 (drawdown > 20% and didn't cut)
        """
        hold_nodes = []
        hold_config = self.reverse_config.get("hold_detection", {})
        profit_threshold = hold_config.get("unrealized_profit_threshold_pct", 100)
        loss_threshold = hold_config.get("unrealized_loss_threshold_pct", 30)
        drawdown_threshold = hold_config.get("drawdown_threshold_pct", 20)

        prices = price_data.get("historical_prices", [])
        if not prices or not isinstance(prices, list):
            return hold_nodes

        # Track position entry price and ATH
        entry_price = None
        ath_price = 0
        hold_count = 0

        for i, price_point in enumerate(prices):
            price = price_point.get("price", 0) if isinstance(price_point, dict) else price_point
            if price <= 0:
                continue

            # Update ATH
            if price > ath_price:
                ath_price = price

            # Detect entry (first buy)
            if entry_price is None and classified_txs.get("buys", 0) > 0:
                entry_price = price
                continue

            if entry_price is None:
                continue

            # Calculate unrealized P&L
            unrealized_pnl_pct = ((price - entry_price) / entry_price) * 100

            # Rule 1: 浮盈 > 100% 时未卖
            if unrealized_pnl_pct > profit_threshold:
                hold_count += 1
                hold_nodes.append({
                    "type": "HOLD",
                    "subtype": "unrealized_profit",
                    "reason": f"浮盈 {unrealized_pnl_pct:.0f}% 时未卖出",
                    "reason_en": f"Held with {unrealized_pnl_pct:.0f}% unrealized profit",
                    "price_at_point": price,
                    "unrealized_pnl_pct": round(unrealized_pnl_pct, 1),
                    "significance": "high" if unrealized_pnl_pct > 200 else "medium"
                })

            # Rule 2: 浮亏 > 30% 时未割
            if unrealized_pnl_pct < -loss_threshold:
                hold_count += 1
                hold_nodes.append({
                    "type": "HOLD",
                    "subtype": "unrealized_loss",
                    "reason": f"浮亏 {abs(unrealized_pnl_pct):.0f}% 时未割肉",
                    "reason_en": f"Held through {abs(unrealized_pnl_pct):.0f}% unrealized loss",
                    "price_at_point": price,
                    "unrealized_pnl_pct": round(unrealized_pnl_pct, 1),
                    "significance": "high" if abs(unrealized_pnl_pct) > 50 else "medium"
                })

            # Rule 3: 价格创新高时未卖
            if price >= ath_price * 0.99 and unrealized_pnl_pct > 50:
                # Check if this is near ATH
                hold_nodes.append({
                    "type": "HOLD",
                    "subtype": "ath_hold",
                    "reason": f"价格接近ATH时未卖出",
                    "reason_en": "Held at near-ATH price",
                    "price_at_point": price,
                    "ath_price": ath_price,
                    "significance": "high"
                })

            # Rule 4: 回调 > 20% 时未割
            if ath_price > 0:
                drawdown_pct = ((ath_price - price) / ath_price) * 100
                if drawdown_pct > drawdown_threshold:
                    hold_nodes.append({
                        "type": "HOLD",
                        "subtype": "drawdown_hold",
                        "reason": f"从ATH回调 {drawdown_pct:.0f}% 时未割肉",
                        "reason_en": f"Held through {drawdown_pct:.0f}% drawdown from ATH",
                        "price_at_point": price,
                        "drawdown_pct": round(drawdown_pct, 1),
                        "significance": "high" if drawdown_pct > 40 else "medium"
                    })

        # Deduplicate: keep only the most significant hold of each subtype
        seen_subtypes = {}
        for node in hold_nodes:
            st = node["subtype"]
            if st not in seen_subtypes or node.get("significance") == "high":
                seen_subtypes[st] = node

        return list(seen_subtypes.values())

    def _analyze_entry_timing(self, nodes: List[Dict], price_data: Dict, config: Dict) -> Dict:
        sub_factors = config.get("sub_factors", [])
        result = {"score": 0, "details": {}}
        for sf in sub_factors:
            result["details"][sf] = {"value": None, "assessment": "需要更多数据"}
        result["score"] = 3.0  # Default neutral score
        return result

    def _analyze_exit_timing(self, nodes: List[Dict], price_data: Dict, config: Dict) -> Dict:
        sub_factors = config.get("sub_factors", [])
        result = {"score": 0, "details": {}}
        for sf in sub_factors:
            result["details"][sf] = {"value": None, "assessment": "需要更多数据"}
        result["score"] = 3.0
        return result

    def _analyze_position_management(self, nodes: List[Dict], config: Dict) -> Dict:
        sub_factors = config.get("sub_factors", [])
        result = {"score": 0, "details": {}}
        for sf in sub_factors:
            result["details"][sf] = {"value": None, "assessment": "需要更多数据"}
        result["score"] = 3.0
        return result

    def _analyze_token_selection(self, transactions: List[Dict], config: Dict) -> Dict:
        tokens = set(tx.get("token", "") for tx in transactions if tx.get("token"))
        return {
            "unique_tokens": len(tokens),
            "token_list": list(tokens),
            "score": 3.0,
            "assessment": "需要更多数据进行深入分析"
        }

    def _analyze_behavior_pattern(self, transactions: List[Dict], config: Dict) -> Dict:
        if not transactions:
            return {"score": 3.0, "patterns": []}

        timestamps = [tx.get("timestamp", "") for tx in transactions if tx.get("timestamp")]
        return {
            "total_transactions": len(transactions),
            "unique_timestamps": len(set(timestamps)),
            "score": 3.0,
            "patterns": ["需要时间序列分析"]
        }

    def _match_strategies(self, factors: Dict) -> List[Dict]:
        """Match factors against known strategy patterns."""
        patterns_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'strategy_patterns.json')
        try:
            with open(patterns_path, 'r') as f:
                patterns_data = json.load(f)
        except FileNotFoundError:
            return []

        patterns = patterns_data.get("patterns", [])
        matched = []

        for pattern in patterns:
            conditions = pattern.get("conditions", {})
            match_score = 0
            conditions_met = 0
            total_conditions = len(conditions)

            if total_conditions == 0:
                continue

            for key, threshold in conditions.items():
                if key.endswith("_min"):
                    factor_key = key.replace("_min", "")
                    factor = factors.get(factor_key, {})
                    score = factor.get("score", 0)
                    if score >= threshold:
                        conditions_met += 1
                elif key.endswith("_max"):
                    conditions_met += 1  # Simplified check
                else:
                    conditions_met += 1

            match_ratio = conditions_met / total_conditions
            if match_ratio >= 0.5:
                matched.append({
                    "pattern_id": pattern.get("id"),
                    "pattern_name": pattern.get("name"),
                    "pattern_name_zh": pattern.get("name_zh"),
                    "match_ratio": round(match_ratio, 2),
                    "avg_roi_multiplier": pattern.get("avg_roi_multiplier", 1.0),
                    "description": pattern.get("description", "")
                })

        matched.sort(key=lambda x: x["match_ratio"], reverse=True)
        return matched

    def _calculate_roi(self, nodes: List[Dict], price_data: Dict) -> Dict:
        return {
            "total_roi_pct": None,
            "hold_duration_days": None,
            "max_drawdown_pct": None,
            "sharpe_ratio": None,
            "note": "需要完整的价格数据和交易时间戳进行计算"
        }

    def validate_inputs(self, inputs: Dict) -> tuple[bool, Optional[str]]:
        if "address" not in inputs:
            return False, "Missing 'address' in inputs"
        if "transactions" not in inputs:
            return False, "Missing 'transactions' in inputs"
        return True, None
