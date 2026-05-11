"""Tests for S7: FactorReverse skill."""
import pytest
import asyncio
from backend.skills.factor_reverse import FactorReverse


class TestFactorReverse:
    def setup_method(self):
        self.skill = FactorReverse()

    def test_validate_inputs_missing_address(self):
        valid, err = self.skill.validate_inputs({"transactions": []})
        assert not valid
        assert "address" in err

    def test_validate_inputs_missing_transactions(self):
        valid, err = self.skill.validate_inputs({"address": "0xabc"})
        assert not valid
        assert "transactions" in err

    def test_validate_inputs_valid(self):
        valid, err = self.skill.validate_inputs({"address": "0xabc", "transactions": []})
        assert valid
        assert err is None

    def test_classify_transactions(self):
        txs = [
            {"type": "buy", "token": "CAKE"},
            {"type": "sell", "token": "CAKE"},
            {"type": "transfer", "token": "BNB"},
            {"type": "lp_add", "token": "CAKE"},
        ]
        result = self.skill._classify_transactions(txs)
        assert result["buys"] == 1
        assert result["sells"] == 1
        assert result["transfers"] == 1
        assert result["lp_adds"] == 1

    def test_extract_decision_nodes(self):
        classified = {"buys": 3, "sells": 1, "lp_adds": 0, "lp_removes": 0,
                      "bridges": 0, "borrows": 1, "repays": 0, "transfers": 2}
        nodes = self.skill._extract_decision_nodes(classified, {})
        types = [n["type"] for n in nodes]
        assert "INITIAL_BUY" in types
        assert "ADD_POSITION" in types
        assert "EXIT" in types
        assert "LEVERAGE" in types

    def test_detect_hold_nodes_profit(self):
        classified = {"buys": 1, "sells": 0}
        price_data = {
            "historical_prices": [
                {"price": 1.0}, {"price": 2.5}, {"price": 3.0}
            ]
        }
        holds = self.skill._detect_hold_nodes(classified, price_data)
        # Should detect unrealized profit > 100%
        subtypes = [h["subtype"] for h in holds]
        assert "unrealized_profit" in subtypes

    def test_detect_hold_nodes_loss(self):
        classified = {"buys": 1, "sells": 0}
        price_data = {
            "historical_prices": [
                {"price": 10.0}, {"price": 5.0}, {"price": 6.0}
            ]
        }
        holds = self.skill._detect_hold_nodes(classified, price_data)
        subtypes = [h["subtype"] for h in holds]
        assert "unrealized_loss" in subtypes

    def test_match_strategies(self):
        factors = {
            "F1_entry_timing": {"score": 4.5},
            "F2_exit_timing": {"score": 3.0},
            "F3_position_management": {"score": 2.0},
        }
        matched = self.skill._match_strategies(factors)
        assert isinstance(matched, list)

    def test_analyze_entry_timing(self):
        result = self.skill._analyze_entry_timing([], {}, {"sub_factors": ["price_vs_30d", "price_vs_ath"]})
        assert "score" in result
        assert "details" in result
